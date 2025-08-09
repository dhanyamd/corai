
def input_node(): 
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

    return {"prompt": initial_prompt}

    return input_node
