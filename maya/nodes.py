from maya.chains import get_chain, get_code_response, get_instructions, get_fixer_chain
from maya.state import CoraiAgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
import re
from e2b_code_interpreter import Sandbox
from openevals.code.e2b.pyright import create_async_e2b_pyright_evaluator
from langsmith import traceable
from maya.settings import Settings

@traceable
async def input_node(state: CoraiAgentState, config: RunnableConfig): 
    initial_prompt = state.get("messages", "")
    code_snippet = ""
    if len(initial_prompt) > 1 and hasattr(initial_prompt[1], 'content'):
        code_snippet = initial_prompt[1].content

    print(f"Input Node received: {initial_prompt}")
    chain = get_chain()
    response = await chain.ainvoke({"initial_prompt": initial_prompt, "messages": initial_prompt}, config)
    summary = response.content if hasattr(response, 'content') else str(response)
    return {"summary": summary, "retry_count": 0, "code_snippet": code_snippet}
    
@traceable
async def response_node(state: CoraiAgentState, config: RunnableConfig):
    summary = state.get("summary", "")
    sandbox_err = state.get("sandbox_response_err", "")
    summary_content = str(summary) if isinstance(summary, dict) else (summary.content if hasattr(summary, 'content') else str(summary))
    
    if sandbox_err:
        error_content = "\n".join(sandbox_err["error"]) if isinstance(sandbox_err, dict) and "error" in sandbox_err else str(sandbox_err)
        summary_content = f"{summary_content}\n\nPrevious error:\n{error_content}\n\nFix and retry."
    
    code_chain = get_code_response()
    code_gen = await code_chain.ainvoke({"summary": summary_content, "messages": state["messages"]}, config)
    code = code_gen.content if hasattr(code_gen, 'content') else str(code_gen)
    
    messages = state["messages"] + [HumanMessage(content=summary_content)]
    return {"code": AIMessage(content=code), "messages": messages}

@traceable
async def code_fixer_node(state: CoraiAgentState, config: RunnableConfig):
    sandbox_err = state.get("sandbox_response_err", "")
    code_snippet = state.get("code_snippet", "")
    test_code = state.get("code", "")
    
    error_content = "\n".join(sandbox_err["error"]) if isinstance(sandbox_err, dict) and "error" in sandbox_err else str(sandbox_err)
    
    # Create a detailed prompt for the code fixer
    fixer_prompt = f"""The following JavaScript code snippet has failed the Jest tests with the error below.
    
    Original JavaScript Code:
    ```javascript
    {code_snippet}
    ```
    
    Failing Jest Test Code:
    ```javascript
    {test_code.content if hasattr(test_code, 'content') else test_code}
    ```

    Error from Sandbox:
    {error_content}
    
    Your task is to fix the original JavaScript code so that it passes the tests.
    The error is a `TypeError` because `req.body` is undefined when a `PUT` request is made to a non-existent user. The line `const {{ name, email }} = req.body;` throws an error.
    The code should first find the user by ID. If the user is not found, it should immediately return a `404` error. Only if the user is found should it proceed to access `req.body`.

    Return **only** the corrected JavaScript code, enclosed in a javascript markdown block.
    """
    
    # Use a chain to generate the corrected code
    fixer_chain = get_fixer_chain()
    # Pass empty messages to focus on the detailed prompt
    corrected_code_gen = await fixer_chain.ainvoke({"messages": [HumanMessage(content=fixer_prompt)]}, config)
    corrected_code = corrected_code_gen.content if hasattr(corrected_code_gen, 'content') else str(corrected_code_gen)
    
    # Extract the code from the response
    code_match = re.search(r"```(?:javascript\n)?(.*)```", corrected_code, re.DOTALL)
    if code_match:
        actual_code_to_run = code_match.group(1).strip()
    else:
        # Fallback if no markdown block is found
        actual_code_to_run = corrected_code.strip()
    
    retry_count = state.get("retry_count", 0) + 1
    return {"code_snippet": actual_code_to_run, "retry_count": retry_count}

@traceable
def sandbox_node(state: CoraiAgentState):
    """
    A dynamic, multi-language sandbox execution engine.
    """
    code = state.get("code")
    if not code:
        return {"sandbox_response": ["No code found in the state to run."]}

    settings = Settings()
    with Sandbox(api_key=settings.E2B_API_KEY) as sandbox:
        code_content = code.content if hasattr(code, 'content') else str(code)
        
        code_match = re.search(r"```(?:\w+\n)?(.*)```", code_content, re.DOTALL)
        actual_code_to_run = code_match.group(1).strip() if code_match else code_content.strip()

        # --- Language & Framework Detection ---
        language, test_runner, test_filename, module_filename = "python", "unittest", "test_script.py", "module_to_test.py"
        
        original_code_snippet = state.get("code_snippet", "")

        if "express" in original_code_snippet.lower() or "require('react')" in original_code_snippet.lower():
            language, test_runner, test_filename, module_filename = "javascript", "jest", "test.spec.js", "app.js"
        elif "cargo" in original_code_snippet.lower():
            language, test_runner, test_filename, module_filename = "rust", "cargo", "tests/integration_test.rs", "src/lib.rs"
        elif "public class" in original_code_snippet:
            language, test_runner, test_filename, module_filename = "java", "junit", "Test.java", "Main.java"

        # --- Failsafe for Python ---
        if language == "python" and "def calculate_discount" in actual_code_to_run:
            actual_code_to_run = re.sub(r"def calculate_discount.*?:(?:\n\s+.*)+", "", actual_code_to_run, flags=re.DOTALL)

        # --- Script Assembly ---
        import base64
        encoded_test_code = base64.b64encode(actual_code_to_run.encode('utf-8')).decode('utf-8')
        write_test_code_cmd = f"echo '{encoded_test_code}' | base64 -d > {test_filename}"

        full_script = ""
        if original_code_snippet:
            encoded_original_code = base64.b64encode(original_code_snippet.encode('utf-8')).decode('utf-8')
            write_original_code_cmd = f"echo '{encoded_original_code}' | base64 -d > {module_filename}"
            full_script += f"{write_original_code_cmd} && "
        
        full_script += write_test_code_cmd

        # --- Execution Commands ---
        if test_runner == 'jest':
            full_script = (
                f"npm init -y && npm install express body-parser jest supertest && "
                f"echo '{encoded_original_code}' | base64 -d > {module_filename} && "
                f"echo '{encoded_test_code}' | base64 -d > {test_filename} && "
                f"node_modules/.bin/jest {test_filename}"
            )
        elif test_runner == 'unittest':
            full_script += f" && python -m unittest {test_filename}"
        elif test_runner == 'pytest':
            full_script += f" && pip install pytest && python -m pytest"
        elif test_runner == 'cargo':
            full_script = f"cargo new project && cd project && echo '{encoded_original_code}' | base64 -d > {module_filename} && echo '{encoded_test_code}' | base64 -d > {test_filename} && cargo test"
        elif test_runner == 'junit':
            full_script += f" && mvn test" # Assumes a pom.xml is provided or generated

        print(f"Debug - Language: {language}, Runner: {test_runner}")
        print(f"Debug - Script: {full_script}")

        try:
            proc = sandbox.commands.run(cmd=full_script, timeout=120000) # 2 min timeout
            output = proc.stdout.split('\n')
            if proc.stderr:
                output.extend(["--- STDERR ---", *proc.stderr.split('\n')])

            if proc.exit_code == 0:
                state["sandbox_response"] = {"output": output, "code": actual_code_to_run}
                if "sandbox_response_err" in state:
                    del state["sandbox_response_err"]
            else:
                state["sandbox_response_err"] = {"error": output, "code": actual_code_to_run}

        except Exception as e:
            state["sandbox_response_err"] = {"error": [f"Exception: {str(e)}"], "code": actual_code_to_run}
        
        return state

@traceable
def final_response(state: CoraiAgentState):
    """
    Formats the final response to be clear and concise.
    """
    sandbox_response = state.get("sandbox_response", {})
    sandbox_err = state.get("sandbox_response_err", {})

    if sandbox_err:
        final_response = {
            "output": sandbox_err.get("error", ["No error output from sandbox."]),
            "code": sandbox_err.get("code", "# No code executed.")
        }
    elif not isinstance(sandbox_response, dict):
        final_response = {"output": ["Sandbox response not in expected format."], "code": ""}
    else:
        final_response = {
            "output": sandbox_response.get("output", ["No output from sandbox."]),
            "code": sandbox_response.get("code", "# No code executed.")
        }
            
    state["final_response"] = final_response
    return {"final_response": final_response, "messages": state["messages"]}
