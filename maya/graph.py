from functools import lru_cache
from langgraph.graph import START, END, StateGraph
from maya.state import CoraiAgentState
from .nodes import input_node, sandbox_node, response_node, final_response

def select_edge(state: CoraiAgentState):
    """
    Conditional edge function that determines the next node based on the sandbox execution result.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        str: The name of the next node to route to
    """
    # Check if there's an error from the sandbox execution
    if state.get("sandbox_response_err"):
        return "response_node"  # Go back to response_node to regenerate code
    else:
        return "final_response"  # Proceed to final_response when successful
@lru_cache(maxsize=1)
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

    return graph_builder.add_edge("final_response", END)
graph = create_workflow_graph().compile()