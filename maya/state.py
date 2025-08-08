from langgraph.graph import MessageState 

class CoraiAgentState(MessageState): 
    """
    State class for ai agent workflow

    Attributes: 
     prompt (AnyMessage): the user's message or the first input containing a code snippet or text prompt with the code file
     text_response (str): the response to the intial user's prompt as mentioned above by the ChatGroq llm 
     sandbox_response (str): text_response containing generated code snippet passed down here to get a code response along with other parameters.
     evaluation (str): returns true if the sandbox_response could execute the code properly, returns false if the sandbox_response code execution test failed
     final (str): the final response that is given by the evaluation node.
    """
    prompt : list[str] | str
    test_response: list[str] | str
    sandbox_response : list[str] | str
    evaluation: bool
    final: list[str] | str


