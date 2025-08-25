# ADK Examples

This repository introduces different concepts in **ADK** through a series of progressively complex examples.

---

## `01-test`
- Demonstrates the **minimum setup required** to run an agent.  
- Highlights **basic constraints** and configuration needed to get started.  

---

## `02-simple`
Explores tool usage and structured outputs:

1. An agent that invokes a **Google-provided tool** (e.g., `google-search`).  
2. An agent that invokes a **custom self-declared tool**.  
3. An agent that returns a **structured output** defined by a Pydantic schema.  

👉 Agents in this stage are executed via the `adk web` command for quick validation.

---

## `03-withmemory`
Introduces **memory and session management** in ADK:

- Key concepts: **Sessions, State, Events, Runner** and how they interact.  
- Moves away from `adk web` to a manual runner setup — similar to **production execution**.  

Examples:
1. **Preference Q&A Agent** – answers based on preloaded user preferences (In-Memory state).  
2. **Preference Managing Agent** – updates preferences dynamically from user messages and stores them in state (In-Memory state).  
3. **Notes Agent** – supports full CRUD on notes, with **persistent memory** backing.  

---

## `04-multiagents`
Explores **multi-agent orchestration**:

- A root **manager agent** that delegates work to sub-agents.  
- Sub-agents include a **Notes Agent** and a **Preferences Agent**.  
- Mimics a customer support workflow where different agents specialize in different tasks.  

---

## `05-callbacks`
Introduces **callbacks** for controlling and inspecting the execution flow:

- `agent_callback` – intercept agent-level behavior.  
- `model_callback` – trace or control LLM calls.  
- `tool_callback` – observe and manipulate tool interactions.  

---

⚡ Each step builds on the previous, showing how to evolve from a **minimal agent** into a **production-ready, multi-agent system with memory and callbacks**.  