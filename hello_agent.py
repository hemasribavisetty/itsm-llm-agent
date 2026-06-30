import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY not found. Copy .env.example to .env and add your key.")


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    fake_weather = {
        "tokyo": "Sunny, 24°C",
        "san francisco": "Foggy, 16°C",
        "new york": "Rainy, 18°C",
    }
    return fake_weather.get(city.lower(), f"No data available for {city}")


def main():
    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    model = ChatGroq(model=model_name, temperature=0)
    agent = create_agent(model, tools=[get_weather])

    test_questions = [
        "What's the weather in Tokyo?",
        "Should I bring an umbrella in New York today?",
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"USER: {question}")
        print("=" * 60)
        result = agent.invoke({"messages": [("user", question)]})
        for msg in result["messages"]:
            role = msg.__class__.__name__
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            print(f"[{role}] {content[:200]}")


if __name__ == "__main__":
    main()