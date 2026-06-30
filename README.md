---
title: ITSM AI Agent
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.45.0
app_file: app.py
pinned: false
---

# 🤖 ITSM AI Agent

An intelligent IT Service Management assistant built with LangGraph, Groq, ChromaDB, and Tavily.

## What it does
- Answers IT support questions from a knowledge base (ChromaDB RAG)
- Queries a live incidents database (SQLite)
- Searches the web for current information (Tavily)
- Remembers conversation history across multiple turns (LangGraph MemorySaver)

## Tech Stack
- **LangGraph** — custom StateGraph agent with explicit nodes and routing
- **Groq** — fast LLM inference (Llama 4 Scout)
- **ChromaDB** — vector database for RAG knowledge base
- **Tavily** — real-time web search
- **Streamlit** — chat interface

## Evaluation
- 10/10 test cases passing
- 100% keyword accuracy
- 100% tool routing accuracy

## Architecture
User → LLM Node → should_continue?
↓ tool_use → Tool Node → back to LLM
↓ final answer → END

## Local Setup
```bash
git clone https://github.com/hemasribavisetty/itsm-llm-agent
cd itsm-llm-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY and TAVILY_API_KEY to .env
streamlit run app.py
```