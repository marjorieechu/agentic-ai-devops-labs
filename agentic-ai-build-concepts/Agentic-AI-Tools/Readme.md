### AI Tools
Without tools, AI can only talk. Tools transform AI from talking to Doing
LLMs generate text, but tools let agents EXECUTE tasks
Tools connect to external systems (APIs, databases, apps)
Tools enable: sending emails, booking flights, querying data

### Tools includes:
- frameworks 
- plus ready-made agent products
- plus platforms that already run agents for you
- plus no-code/low-code agent builders
- sometimes even full applications

### Examples include
Crew-ai, LangGraph, LangChain, Autogen, N8N, RAG, MCP, etc.

AI tools connect to each other and the LLM via APIs
However, APIs work great for developers. But for AI agents, they can be a nightmare for the following reasons
- No uniform structure; Every API is different
- Hard to discover; AI can't find available tools on its own
- Error handling; Failures break entire workflows
- Not AI-friendly; Designed for developers, not natural language
- Complex chaining; Multi-step tasks across APIs are difficult
- Security complexity; Authentication adds extra layers

### MCP: The Solution
MCP (Model Context Protocol) is a universal standard for AI to connect to tools, data, and systems. 
It is a universal adapter that helps AI discover, understand, and use tools easily.
It helps to 
- make tools AI-firendly
- simplify integration
- enable discovery
- scales easily

### RAG vs MCP
RAG → Helps AI KNOW more by reading info
MCP → Helps AI DO more by taking action

Both however have the following in common
Use external data (not inside model)
Improve accuracy
Reduce hallucinations
Work with real-world systems

### RAG & MCP
Combine both for real-world solutions
- RAG retrieves knowledge
- MCP executes actions
Combined system gives powerful AI agents

