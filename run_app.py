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
    code_snippet = """const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// In a real application, this would be a database
let users = [
  { id: 1, name: 'Alice Smith', email: 'alice@example.com' },
  { id: 2, name: 'Bob Johnson', email: 'bob@example.com' },
];

// GET all users
app.get('/api/users', (req, res) => {
  res.status(200).json(users);
});

// GET user by ID
app.get('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const user = users.find(u => u.id === id);

  if (user) {
    res.status(200).json(user);
  } else {
    res.status(404).json({ message: 'User not found' });
  }
});

// POST a new user
app.post('/api/users', (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) {
    return res.status(400).json({ message: 'Name and email are required' });
  }

  const newUser = {
    id: users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1,
    name,
    email,
  };
  users.push(newUser);
  res.status(201).json(newUser);
});

// PUT (update) a user by ID
app.put('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const { name, email } = req.body;

  let userFound = false;
  users = users.map(user => {
    if (user.id === id) {
      userFound = true;
      return { ...user, name: name || user.name, email: email || user.email };
    }
    return user;
  });

  if (userFound) {
    res.status(200).json(users.find(u => u.id === id));
  } else {
    res.status(404).json({ message: 'User not found' });
  }
});

// DELETE a user by ID
app.delete('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const initialLength = users.length;
  users = users.filter(user => user.id !== id);

  if (users.length < initialLength) {
    res.status(204).send(); // No content for successful deletion
  } else {
    res.status(404).json({ message: 'User not found' });
  }
});

// Start the server (only if this file is run directly, not when imported for testing)
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
  });
}

module.exports = app; // Export the app for testing
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
    final_response = result.get("final_response", {})
    
    # The output is now a simple dictionary with "output" and "code" keys.
    if isinstance(final_response, dict):
        print("\n--- Sandbox Output ---")
        print("(Note: The 'unittest' library prints to STDERR by default, even on success.)")
        for line in final_response.get("output", []):
            print(line)
        print("\n--- Code Executed ---")
        print(final_response.get("code", ""))
    else:
        print("No final response found.")

if __name__ == "__main__":
    asyncio.run(main())
