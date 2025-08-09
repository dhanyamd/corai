from functools import lru_cache 
from langgraph.graph import START, END, StateGraph 
from maya.state import CoraiAgentState
from .nodes import input_node
@lru_cache(maxsize=1)
def create_workflow_graph(): 
    graph_builder = StateGraph(CoraiAgentState)

    graph_builder.add_node("input_router", input_router)
    graph_builder.add_node("reponse_node", response_node)
    graph_builder.add_node("sandbox_node", sandbox_node)
    graph_builder.add_node("evaluate_node", evaluate_node)
    graph_builder.add_node("final_response", final_repsonse)

    graph_builder.add_edge(START, "input_router") 
    graph_builder.add_edge("input_router", "response_node")
    graph_builder.add_edge("response_node", "sandbox_node") 
    graph_builder.add_edge("sandbox_node", "evaluate_node") 

    graph_builder.add_conditional_edges(
    "evaluate_node",
    select_edge,
    {
        "response_node": "response_node",
        "final_response": "final_response"
    }
)

graph_builder.add_edge("final_response", END)