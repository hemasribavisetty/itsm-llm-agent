import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import web_search, query_incidents, search_knowledge_base

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY not found. Check your .env file.")


def main():
    model = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

    agent = create_react_agent(
        model,
        tools=[search_knowledge_base, query_incidents, web_search]
    )

    # Test questions designed to force each tool
    test_questions = [
        "How do I set up VPN on my laptop?",           # should hit knowledge base
        "Show me all critical incidents right now",     # should hit incidents DB
        "What are the latest ransomware threats in 2026?",  # should hit web search
        "I can't get my MFA app working, what should I do and are there any open tickets about it?",  # should use multiple tools
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"USER: {question}")
        print("=" * 60)
        result = agent.invoke({"messages": [("user", question)]})
        for msg in result["messages"]:
            role = msg.__class__.__name__
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if content.strip():
                print(f"[{role}] {content[:400]}")


if __name__ == "__main__":
    main()