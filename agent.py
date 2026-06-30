import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from tools import web_search, query_incidents, search_knowledge_base

load_dotenv()

# ─────────────────────────────────────────
# 1. STATE SCHEMA
# Every node reads from and writes back to this.
# add_messages is a reducer — it appends new messages rather than overwriting.
# ─────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ─────────────────────────────────────────
# 2. MODEL + TOOLS
# ─────────────────────────────────────────
TOOLS = [search_knowledge_base, query_incidents, web_search]
TOOL_MAP = {t.name: t for t in TOOLS}

model = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0
).bind_tools(TOOLS)

# ─────────────────────────────────────────
# 3. NODES
# Each node is just a Python function.
# ─────────────────────────────────────────
def llm_node(state: AgentState) -> AgentState:
    """Call the LLM with the current message history."""
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def tool_node(state: AgentState) -> AgentState:
    """Execute whatever tool(s) the LLM requested."""
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name in TOOL_MAP:
            try:
                result = TOOL_MAP[tool_name].invoke(tool_args)
            except Exception as e:
                result = f"Tool error: {str(e)}"
        else:
            result = f"Unknown tool: {tool_name}"

        tool_results.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_name
            )
        )

    return {"messages": tool_results}


# ─────────────────────────────────────────
# 4. ROUTING LOGIC
# This is the conditional edge — it decides what happens next.
# ─────────────────────────────────────────
MAX_ITERATIONS = 10

def should_continue(state: AgentState) -> str:
    """Route to tool_node if the LLM made tool calls, otherwise end."""
    last_message = state["messages"][-1]

    # Count how many AI messages we've had (rough iteration counter)
    ai_message_count = sum(
        1 for m in state["messages"] if isinstance(m, AIMessage)
    )

    # Guard against infinite loops
    if ai_message_count >= MAX_ITERATIONS:
        return END

    # If the last message has tool calls, run the tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"

    # Otherwise the LLM gave a final answer — we're done
    return END


# ─────────────────────────────────────────
# 5. BUILD THE GRAPH
# ─────────────────────────────────────────
def build_agent():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("llm_node", llm_node)
    graph.add_node("tool_node", tool_node)

    # Entry point
    graph.set_entry_point("llm_node")

    # Conditional edge from LLM: either call a tool or end
    graph.add_conditional_edges(
        "llm_node",
        should_continue,
        {
            "tool_node": "tool_node",
            END: END
        }
    )

    # After tools always go back to LLM
    graph.add_edge("tool_node", "llm_node")

    return graph.compile()


# ─────────────────────────────────────────
# 6. RUN IT
# ─────────────────────────────────────────
def run_agent(question: str, agent) -> str:
    result = agent.invoke({"messages": [("user", question)]})
    # Return the last AI message content
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "No answer generated."


if __name__ == "__main__":
    agent = build_agent()

    test_questions = [
        "How do I set up VPN on my laptop?",
        "Show me all critical incidents right now",
        "What are the latest ransomware threats in 2026?",
        "I can't get my MFA app working, what should I do and are there any open tickets about it?",
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"USER: {question}")
        print("=" * 60)
        answer = run_agent(question, agent)
        print(f"AGENT: {answer}")