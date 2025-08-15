from functools import lru_cache
from langgraph.graph import START, END, StateGraph
from .state import CoraiAgentState
from .nodes import input_node, sandbox_node, response_node, final_response
from langsmith import traceable
from .settings import Settings

# Initialize LangSmith configuration
settings = Settings()
settings.configure_langsmith()

@traceable
def select_edge(state: CoraiAgentState):
    """
    Conditional edge function that determines the next node based on the sandbox execution result.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        str: The name of the next node to route to
    """
    # Check if there's an error from the sandbox execution
    sandbox_err = state.get("sandbox_response_err")
    if sandbox_err:
        error_str = str(sandbox_err).lower()
        # Check for critical errors that should not be retried as they are likely
        # environment or setup issues, not problems with the generated code.
        if (
            "exit code 1" in error_str  # pytest: tests failed
            or "exit code 5" in error_str  # pytest: no tests collected
            or "getaddrinfo failed" in error_str  # Network error
            or "command exited with code 2" in error_str  # Sandbox interruption
        ):
            return "final_response"
        
        # For other errors, attempt to regenerate the code
        return "response_node"
    
    # If there is no error, the sandbox execution was successful
    return "final_response"

@lru_cache(maxsize=1)
@traceable
def create_workflow_graph(): 
    graph_builder = StateGraph(CoraiAgentState)

    graph_builder.add_node("input_router", input_node)
    graph_builder.add_node("response_node", response_node)
    graph_builder.add_node("sandbox_node", sandbox_node)
    graph_builder.add_node("final_response", final_response)

    graph_builder.add_edge(START, "input_router")
    graph_builder.add_edge("input_router", "response_node")
    graph_builder.add_edge("response_node", "sandbox_node")
    # Remove the direct edge from sandbox_node to final_response as it's handled by conditional edges

    graph_builder.add_conditional_edges(
    "sandbox_node",
     select_edge,
    {
        "response_node": "response_node",
        "final_response": "final_response"
    }
)

    graph_builder.add_edge("final_response", END)
    return graph_builder

graph = create_workflow_graph().compile()
