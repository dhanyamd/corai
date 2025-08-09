
def input_node(state: CoraiAgentState, config: RunnableConfig): 
    """
    Returns the input that is given to the graph to the input_node
    Args: 
        prompt: str 
        code: str | list[str]
    Yields: 
        summary: str 
        code : str | list[str]
    """
    intial_prompt = state.get("prompt", "")
    print(f"Input Node received: {initial_prompt}")
    chain = get_chain(initial_prompt)
    response = await chain.invoke({"prompt": initial_prompt, messages: state["messages"]}, config)

    return response
