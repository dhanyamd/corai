#!/usr/bin/env python3
"""
Script to run the Maya LangGraph application.
"""

import asyncio
from maya.graph import graph
from langchain_core.messages import HumanMessage

async def main():
    # Example input - replace with your own
    instruction = "can you write unit tests for this?"
    code_snippet = """def calculate_discount(price, discount_percentage):
    if price < 0 or discount_percentage < 0:
        raise ValueError("Price and discount percentage must be non-negative.")

    discount_amount = price * (discount_percentage / 100)
    final_price = price - discount_amount
    return final_price
"""
    # Create the input state with separate messages for instruction and code
    input_state = {
        "messages": [
            HumanMessage(content=instruction),
            HumanMessage(content=code_snippet)
        ]
    }
    
    # Run the graph with increased recursion limit
    result = await graph.ainvoke(input_state, {"recursion_limit": 200})
    
    print("Final result:")
    final_response = result.get("final_response", "No final response found")
    if isinstance(final_response, dict):
        print("Status:", final_response.get("status", "Unknown"))
        print("Description:", final_response.get("description", ""))
        print("Output:")
        for line in final_response.get("output", []):
            print(line)
        print("Code:")
        print(final_response.get("code", ""))
    else:
        print(final_response)

if __name__ == "__main__":
    asyncio.run(main())
