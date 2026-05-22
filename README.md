# AI Engineering Portfolio

A structured four-project series documenting my transition from banking and consumer finance into AI engineering. Each project builds on the previous one, progressively introducing the core patterns of modern AI systems — from basic API interaction through to multi-step agent reasoning.

## About Me

I am an AVP at a Singapore bank working in consumer banking product and operations. After several years in finance, I am exploring pivoting applied AI roles — specifically AI Solutions Architect and AI Product positions in Singapore's fintech and banking sector.

This portfolio represents the practical foundation of that transition. Every project here was built by me with the explicit goal of understanding LLM systems at a mechanical level, not just calling APIs.

## Why This Portfolio Exists

Most AI tutorials teach you to build things that work in the happy path. Production AI systems fail in specific, learnable ways — malformed JSON, retrieval drift, prompt regression, agent confusion. This portfolio is structured around those failure modes because that is what hiring managers actually filter for.

## The Four Projects

### [Project 1 — CLI Chatbot with Multi-Turn Memory](./project-1-cli-chatbot/)
*Foundational LLM API patterns and engineered conversation memory.*

Built a terminal chatbot demonstrating that LLMs are stateless and memory must be explicitly maintained. Covers system vs user prompts, context window management, and graceful error handling.

**Key concept:** memory in LLM applications is engineered, not inherent.

---

### [Project 2 — Transaction Classifier with Structured JSON](./project-2-transaction-classifier/)
*Reliable structured output and the LLM + rules hybrid pattern.*

Built a pipeline that classifies raw bank transaction strings into structured JSON with anomaly detection. Addresses the reality that LLMs are token predictors, not JSON serialisers — and what that means for production reliability in regulated banking contexts.

**Key concept:** LLM as interpreter, rules as enforcer. Neither alone is sufficient for compliance.

---

### [Project 3 — RAG Pipeline over Financial Documents & RAG Evaluation Framework](./project-3-RAG-pipeline/)
*Retrieval augmented generation built from scratch over MAS regulatory content & Systematic measurement of AI system quality across multiple dimension.*

Built the full RAG pipeline — PDF ingestion, chunking with overlap, embeddings via sentence-transformers, ChromaDB vector storage, similarity retrieval, and grounded generation. Includes the complete failure taxonomy I developed while debugging.
Built a custom evaluation framework that runs test datasets through two prompt versions, scores outputs on factual correctness, groundedness, and completeness using LLM-as-judge, and produces comparative reports identifying regressions.

**Key concept:** Retrieval quality determines answer quality. Fix retrieval before fixing prompts. Evaluation framework with iterations helps you to pinpoint the area that is causing inaccurate retrievals and outputs. 
Using the evaluation framework, you are able to consistently improve your RAG pipeline through multiple iterations.
This same framework should be applied to production AI in order for it to recommend improvements to its own pipeline to improve its accuracy.

---

### [Project 4 — Financial Research Agent with Tool Use](./project-4-Agent-Tools/)
*Agentic AI with multi-step tool calling for financial research.*

Built an agent that decides which tools to call (live stock prices, fundamental data, calculations) and chains them together to answer multi-part questions. Includes defensive validation, regulatory positioning, and full reasoning trace logging.

**Key concept:** Learnt how to setup tool_schemas and expose them to LLMs to use where they see fit. These tools need to functions or methods that can be called by the agent.
Learnt when integrating with Anthropic, how do you avail and invoke tools on behalf of the agent. The LLM does not invoke the tool directly, it only sends you an indicator that it needs and wants to invoke the tool. It is up to your script to capture that request, and invoke it on the server side.  
Understood the difference between a simple chatbot and an Agent, where the Agent has the autonamy to decide which tools are required, and WHEN they should be using each tool.
Understood the importance of setting up the description of each tool, the expected input and output of each

---

## Themes Across All Projects

**Prevention plus recovery.** Every failure mode needs both — prompts reduce frequency, code prevents failure deterministically. Never trust the model; always trust your code.

**LLM as interpreter, rules as enforcer.** In regulated contexts like banking, LLMs handle ambiguity while deterministic rules handle compliance and auditability.

**Scale changes everything.** What works for 10 inputs breaks at 10,000. Production thinking starts with "what happens at 100x volume?"

**Singapore regulatory context.** MAS requirements around explainability, audit trails, and the distinction between advisory and execution-only services are architectural constraints from day one, not afterthoughts.

## Stack

- **Languages:** Python 3.11
- **Models:** Claude via Anthropic SDK
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB:** ChromaDB
- **Data:** pandas, yfinance
- **Document processing:** pypdf

## Getting Started


You will need:

```bash
git clone https://github.com/mikeong1604-dot/ai-engineering-portfolio.git
cd ai-engineering-portfolio
# Each project has its own requirements.txt
```

You will need an Anthropic API key set in a `.env` file in any project you want to run.

## What's Next

The four projects above represent the foundation. Currently in progress:

- **Project 5** — Multi-agent orchestration with LangGraph and the ReAct pattern


## Contact

https://www.linkedin.com/in/michaelongmomk/


I am actively exploring AI Solutions Architect and AI Product roles in Singapore. If you are hiring or know someone who is, I would value the conversation.