# No-memory AI Agent build
This single-agent AI has no tools, memory, guardrails or planning.
It only has the LLM and the openAI API behind the scene.
The foundational components of this openAI Agent SDK including the  Agent object is our focus.
Set up our environment to connect to the openAI API
Monitor what the Agent does through traces using open AI API platform.
And finally run the agent to see it in action using the runner class.

## Set up our environment to connect to the openAI API
To build this no memory single agent Ai, we need the following
Before we can build our first AI agent, we need two things:
1. The `openai-agents` library installed: this constitutes all tools needed to build the . Tools like memory, guardrail etc.
2. Your secret OpenAI API key to communicate with the AI models. From openAI API platform we will obtain a secret key which will be stored in a .env file and ensure the file is placed in same location as

## steps = commands
pip uninstall -y opeana1-agents    # uninstalls any existing agents
pip install --no-cache-dir openai==0.2.2   # install specific version of openai
pip install python-dotenv langchain-openai==0.2.1   # install langchain
pip install --upgrade pydantic   # updates pydantic library

Next is to read the openai API key to make sure it can be read

import os    # helps to accessing the os systems
our python fuction loads and prints a part of the API saved earlier.

After setup, which includes Defining an open ai client/agent to connect to the ai brain(model) through the API( account = agent); given this client a name; next is instructions as to who to be and what to do; then lastly specify models to use.

