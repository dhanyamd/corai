import requests

from langgraph.prebuilt import create_react_agent

from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel

from bs4 import BeautifulSoup

SYSTEM_PROMPT = """
You are Corai, an expert code generation and review agent of every language. You will be given a piece of code function or file of any language. Your job is to
<input>
read the file or the code that is may or may not be provided with an input text/ prompt. Use this prompt as context in further stages while executing the output later.
<input/>
<writer>
You are proficient in all testing frameworks that exist. you would recieve the input of the code function or file as input and generate proper and efficient test cases to them. 
<example>
this is the input you will be given a file containing code like this :
const express = require('express');
const app = express();

app.use(express.json()); // Middleware to parse JSON bodies

let users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
];

app.post('/users', (req, res) => {
  const newUser = {
    id: users.length + 1, // Simple ID generation
    name: req.body.name
  };
  users.push(newUser);
  res.status(201).json(newUser);
});

module.exports = app;

<answer>

Your job is to effectively produce a test script like this. you shall generate the code considering all best code practises and ensure it's perfect

<code_answer>

const request = require('supertest');
const app = require('./app');

describe('POST /users', () => {
  it('should create a new user and return it', async () => {
    const newUser = { name: 'Charlie' };
    const res = await request(app)
      .post('/users')
      .send(newUser)
      .expect(201);

    expect(res.body).toHaveProperty('id');
    expect(res.body.name).toBe('Charlie');
  });
});
<code_ans/>
<answer/>

<example />
<writer />
"""


@tool


def create_base_agent(model: BaseChatModel):
    langgraph_llms_txt = requests.get(
        "https://langchain-ai.github.io/langgraph/llms.txt"
    ).text
    return create_react_agent(
        model=model,
        tools=[get_langgraph_docs_content],
        prompt=SYSTEM_PROMPT.format(langgraph_llms_txt=langgraph_llms_txt),
    ).with_config(run_name="Base Agent")