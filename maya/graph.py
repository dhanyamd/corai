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
    # If sandbox_response_err exists, we retry. Otherwise, we're done.
    if "sandbox_response_err" in state and state["sandbox_response_err"]:
        return "response_node"
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
