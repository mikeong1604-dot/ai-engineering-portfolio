# RAG Pipeline with Evaluation Framework — MAS Regulatory Document Q&A

> **A production-style retrieval augmented generation system for Singapore financial regulatory documents, paired with a custom evaluation framework that systematically measures answer quality across multiple dimensions.**

This is the centrepiece project of my AI engineering portfolio. It combines the two patterns most relevant to enterprise AI deployment in regulated industries: grounded question-answering over proprietary documents, and the measurement infrastructure required to deploy such systems responsibly.

---

## Why This Project Matters

In Singapore's financial services sector, RAG is the most deployed AI pattern right now. Every major bank — DBS, OCBC, UOB — is building internal tools for regulatory Q&A, compliance research, and policy lookup. The technical pattern is well known. What separates a prototype from a production system is the evaluation infrastructure around it.

This project demonstrates both halves of that production reality:

1. **A working RAG pipeline** built from scratch — no high-level libraries hiding the mechanics
2. **A custom evaluation framework** that measures whether the pipeline actually works, scores prompt versions against each other, and identifies failure modes by pipeline stage

The decision to build evaluation from scratch rather than use RAGAS was deliberate. Understanding what metrics like *faithfulness* and *groundedness* actually compute — at the level where I could debug them — was more valuable than getting numbers faster.

---

## Architecture Overview

### The RAG Pipeline
                INGESTION (runs once)

PDF Document
     ↓
Text extraction (pypdf)
     ↓
Chunking with overlap (configurable size)
     ↓
Embedding generation (sentence-transformers, all-MiniLM-L6-v2)
     ↓
Vector storage (ChromaDB, persistent)


                QUERY (runs per request)

User Question
     ↓
Question embedding
     ↓
Similarity search in ChromaDB → top N relevant chunks
     ↓
Context injection into prompt
     ↓
Claude generates grounded answer
     ↓
Response (refuses if answer not in context)

### The Evaluation Framework

Test Dataset (10 human-verified Q+A pairs with categories)
     ↓
┌──────────────────────────────────────┐
│  For each question, run through:     │
│     - Prompt V1 (purposefully wrong) │
│     - Prompt V2 (engineered)         │
│                                      │
│  For each answer, score via          │
│  LLM-as-judge on 3 dimensions:       │
│     - Factual correctness            │
│     - Groundedness to source         │
│     - Completeness                   │
└──────────────────────────────────────┘
     ↓
Comparative report identifying:
    - Winner by overall score
    - Winner by dimension
    - Winner by question difficulty
    - Specific failures and their root cause stage

---

## The Failure Taxonomy I Built While Debugging

The most valuable artifact from this project was not the pipeline itself but the failure taxonomy I developed while debugging it. Every RAG system fails at one of three stages, and knowing which stage matters because the fix is different for each.

### Ingestion failures
- **Scanned PDFs** — no text layer exists; pypdf returns empty pages. Fix: switch to OCR or find another relevant document to try.
- **Poor chunking** — concepts split across chunk boundaries, retrieved incomplete. Fix: increase overlap or use semantic chunking.
- **Embedding model mismatch** — embedding chunks with one model and queries with another produces misaligned vector spaces. Fix: use the same model throughout.

### Retrieval failures
- **Too few chunks retrieved** — context is incomplete for synthesis questions. Fix: increase n_results.
- **Too many chunks retrieved** — noise drowns the relevant signal. Fix: tune n_results downward.
- **Query-document language mismatch** — casual user query versus formal regulatory document. Fix: query rewriting via Claude before embedding.

### Generation failures
- **Weak system prompt** — model uses general knowledge instead of retrieved context. Fix: Guardrail stating explicit grounding instructions, refusal clause to reject any questions that is NOT related to the document ingested.
- **Context window exceeded** — instructions buried at the start lose influence. Fix: place critical instructions at end, reduce chunk count.
- **Parametric knowledge bleed-through** — model blends retrieved context with training data subtly. Fix: this is partially unsolvable without evaluation; measure it rather than assume.

This taxonomy is what made the evaluation framework genuinely useful. When a question scored low, I could tell which stage failed and fix it specifically rather than blindly retuning prompts.

---

## Key Design Decisions

### Why sentence-transformers instead of an API-based embedding model

I discovered partway through that Anthropic does not offer a dedicated embeddings endpoint. After verifying against the docs, I chose `sentence-transformers` with `all-MiniLM-L6-v2` for three reasons:

1. **No API costs** — embedding 200 chunks during ingestion is free
2. **Runs locally** — useful for understanding the embedding step mechanically
3. **Provider-agnostic pattern** — swapping to OpenAI or Cohere later is a 5-line change

The tradeoff: slightly lower retrieval quality than API-based options. For learning and prototype-stage work, the tradeoff is correct. In production with sensitive financial data, local embeddings actually become an advantage for data residency and compliance reasons.

### Why ChromaDB instead of FAISS or Pinecone

ChromaDB runs locally without cloud setup, persists to disk between runs, and has a Python-native API. For a learning project this was right. In production I would evaluate Pinecone for scale or pgvector for integration with existing Postgres infrastructure — both of which Singapore banks already run.

### Why two prompt versions instead of one

The eval framework needs a baseline to be meaningful. V1 is deliberately underspecified — a simple "use the context to answer" prompt. V2 is engineered properly with role definition, explicit refusal instructions for out-of-scope questions, and citation guidance. The point of measurement is to show V2 is genuinely better, not to assume it.

### Why LLM-as-judge instead of keyword matching

Keyword matching produces false negatives constantly — a semantically correct answer phrased differently from ground truth scores zero. LLM-as-judge handles semantic equivalence. The tradeoff is that the judge is non-deterministic and may have systematic biases that mirror the generator's biases. I documented this limitation explicitly rather than hiding it.

---

## Sample Results

You can find some sample results in v1_results.json, v2_results.json and my test set in test_dataset.json.

V2 wins decisively on factual correctness and groundedness. Both versions struggle on hard synthesis questions where the document has sparse coverage of the underlying concept — a data limitation, not a prompt limitation.

---

## Things I Would Change At Scale

This is a learning-stage system, not a production deployment. If I were taking this to production, here is what would need to change:

**Chunking** — semantic chunking based on document structure rather than fixed character size. Regulatory documents have sections, subsections, and definitional blocks that should not be split arbitrarily.

**Embedding** — evaluate higher-quality models. The current model is lightweight and fast but trades off retrieval quality. For regulatory content where precision matters, the upgrade is worthwhile.

**Retrieval** — implement hybrid retrieval combining dense vectors with keyword search (BM25). Pure semantic search misses cases where exact regulatory terminology matters.

**Evaluation** — expand the test set to 50+ questions across more categories, add a human-verified sample to calibrate LLM-as-judge scores, pin specific model versions to detect drift from provider updates.

**Observability** — log every query, retrieved chunks, generated answer, and inferred confidence. Build dashboards to track quality over time. In production, regression detection should be automated, not manual.

**Compliance** — add audit logging that satisfies MAS requirements: every answer traceable to its source chunks, every model version recorded, every prompt version stored immutably alongside its outputs.

---

## Connection to Singapore Financial Services Context

This project is built deliberately against MAS regulatory documents because that is the domain I am moving into. Several design decisions reflect that context:

**Explicit refusal for out-of-scope questions** — MAS expects automated systems to know what they do not know. A RAG system that confidently answers questions outside its document scope would fail compliance review.

**Source attribution in answers** — every answer references the chunks it drew from. In a real deployment, this would be a clickable link to the document section. Explainability is a regulatory requirement, not a UX nice-to-have.

**Measurement infrastructure as a first-class concern** — MAS has published guidance on AI governance that effectively requires firms to measure and monitor AI system performance over time. Building evaluation from day one rather than as an afterthought matters.

**Refusal of advisory recommendations** — the system answers factual regulatory questions but would refuse to recommend specific compliance actions. This maps to the MAS distinction between informational and advisory services.

---

## Tech Stack

- **Python 3.11**
- **Anthropic SDK** — generation and LLM-as-judge scoring
- **sentence-transformers** (`all-MiniLM-L6-v2`) — embeddings
- **ChromaDB** — local vector storage with persistence
- **pypdf** — document extraction
- **pandas** — eval result aggregation

---

## Project Structure

project3-rag-eval/
├── README.md
├── .env.example
├── rag/
│   ├── ingest.py                 # extraction, chunking, embedding, storage
│   ├── retrieve.py               # similarity search
│   └── ask.py                    # grounded generation
|   └── document.pdf              # Document you want to ingest
├── eval/
│   ├── test_dataset.json         # human-verified Q+A pairs
│   ├── prompts.py                # two prompt versions for comparison
│   ├── scorer.py                 # LLM-as-judge scoring on 3 dimensions
│   ├── runner.py                 # runs both prompts through test set
│   └── report.py                 # generates comparison report
└── chroma_db/                    # generated on first run, not committed

---

## How to Run

### Setup

```bash
git clone [your-repo-url]
cd project3-rag-eval

python -m venv venv
source venv/bin/activate          # or venv\Scripts\activate on Windows

pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

### Build the RAG index

```bash
python rag/ingest.py
```

This extracts the PDF, chunks it, generates embeddings, and stores everything in ChromaDB. Runs once.

### Query the system

```bash
python rag/ask.py
```

Interactive prompt for asking questions against the indexed document.

### Run the evaluation

```bash
python eval/runner.py             # runs both prompts through test set
python eval/report.py             # prints comparison report
```

---

## What This Project Taught Me That I Could Not Have Learned From Tutorials

Three things stand out:

**Retrieval quality determines answer quality.** I spent significant time tuning the generation prompt before realising the issue was upstream. Now I always debug retrieval first by inspecting which chunks come back for a failing question. A perfect generation prompt cannot compensate for bad retrieval — and conversely, good retrieval makes mediocre prompts work surprisingly well.

**You cannot guarantee groundedness — you can only measure it.** Instructions to "answer only from context" reduce hallucination but do not eliminate it. The lost-in-the-middle problem (where instructions buried in long contexts carry less influence) is real and measurable. This is why evaluation infrastructure matters more than perfect prompts.

**Building evaluation from scratch teaches you what RAGAS hides.** I now understand what *faithfulness*, *answer relevancy*, and *context precision* actually compute — because I built them myself. In production I would use RAGAS for speed. But I would not trust scores from a tool I could not debug.

---

## What's Next

The next project in my portfolio is a financial research agent that uses tool calling rather than retrieval — moving from grounded Q&A to multi-step reasoning with actions. Where this project demonstrates the *information layer* of AI systems, the agent demonstrates the *action layer*.

After that, multi-agent orchestration with LangGraph and the ReAct pattern.

---

## Contact

[https://www.linkedin.com/in/michaelongmomk/]  

I am actively exploring AI Solutions Architect and AI Product Manager roles in Singapore's fintech and banking sector. If you are hiring, considering hiring, or simply want to discuss applied AI in regulated industries, I would value the conversation.