import os
import sqlite3
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

load_dotenv()

# ─────────────────────────────────────────
# TOOL 1: Web Search (Tavily)
# ─────────────────────────────────────────
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for current information. Use for recent events or external IT questions."""
    results = tavily.search(query=query, max_results=3)
    output = []
    for r in results["results"]:
        output.append(f"Source: {r['url']}\nSummary: {r['content'][:300]}")
    return "\n\n".join(output)


# ─────────────────────────────────────────
# TOOL 2: Incidents Database (SQLite)
# ─────────────────────────────────────────
def init_incidents_db():
    """Create and seed a local SQLite incidents database."""
    conn = sqlite3.connect("incidents.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            title TEXT,
            severity TEXT,
            status TEXT,
            assigned_to TEXT,
            description TEXT
        )
    """)
    # Seed with fake ITSM data
    sample_incidents = [
        ("INC001", "VPN not connecting", "High", "Open", "Alice", "User cannot connect to corporate VPN from home"),
        ("INC002", "Email server down", "Critical", "In Progress", "Bob", "Exchange server unresponsive since 9am"),
        ("INC003", "Laptop slow after update", "Medium", "Open", "Alice", "Performance degraded after Windows update KB5034441"),
        ("INC004", "Printer offline", "Low", "Resolved", "Carol", "Network printer on 3rd floor showing offline"),
        ("INC005", "MFA app not working", "High", "Open", "Bob", "Authenticator app not generating codes for 3 users"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO incidents VALUES (?,?,?,?,?,?)",
        sample_incidents
    )
    conn.commit()
    conn.close()

# Initialize DB when this file is imported
init_incidents_db()

@tool
def query_incidents(question: str) -> str:
    """Query the IT incidents database. Input: natural language question about tickets or incidents."""
    conn = sqlite3.connect("incidents.db")
    cursor = conn.cursor()

    question_lower = question.lower()

    if "critical" in question_lower and ("high" in question_lower or "or" in question_lower):
        cursor.execute(
            "SELECT * FROM incidents WHERE severity IN ('Critical','High') AND status='Open'"
        )
    elif "critical" in question_lower:
        cursor.execute("SELECT * FROM incidents WHERE severity='Critical'")
    elif "open" in question_lower and "high" in question_lower:
        cursor.execute(
            "SELECT * FROM incidents WHERE status='Open' AND severity='High'"
        )
    elif "open" in question_lower:
        cursor.execute("SELECT * FROM incidents WHERE status='Open'")
    elif "resolved" in question_lower:
        cursor.execute("SELECT * FROM incidents WHERE status='Resolved'")
    elif "alice" in question_lower:
        cursor.execute("SELECT * FROM incidents WHERE assigned_to='Alice'")
    elif "bob" in question_lower:
        cursor.execute("SELECT * FROM incidents WHERE assigned_to='Bob'")
    elif any(id in question_lower for id in ["inc001","inc002","inc003","inc004","inc005"]):
        inc_id = next(id.upper() for id in ["inc001","inc002","inc003","inc004","inc005"]
                      if id in question_lower)
        cursor.execute("SELECT * FROM incidents WHERE id=?", (inc_id,))
    else:
        cursor.execute("SELECT * FROM incidents")

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No incidents found matching your query."

    result = []
    for row in rows:
        result.append(
            f"ID: {row[0]} | Title: {row[1]} | Severity: {row[2]} | "
            f"Status: {row[3]} | Assigned: {row[4]}\nDescription: {row[5]}"
        )
    return "\n\n".join(result)


# ─────────────────────────────────────────
# TOOL 3: RAG Knowledge Base (ChromaDB)
# ─────────────────────────────────────────
import chromadb
from chromadb.utils import embedding_functions

def init_knowledge_base():
    """Create and seed a local ChromaDB vector store with IT support articles."""
    client = chromadb.PersistentClient(path="./knowledge_base")
    ef = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="it_support",
        embedding_function=ef
    )

    # Only seed if empty
    if collection.count() == 0:
        docs = [
            "To reset your password, go to account.company.com/reset and enter your employee email. You will receive a reset link within 5 minutes.",
            "VPN setup instructions: Download Cisco AnyConnect from the IT portal. Server address is vpn.company.com. Use your email and password to connect.",
            "To request new hardware, submit a ticket via ServiceNow with category 'Hardware Request'. Approval from your manager is required for items over $500.",
            "If your laptop is running slow, try: 1) Restart it, 2) Run Windows Update, 3) Clear temp files with Disk Cleanup, 4) Contact IT if issue persists.",
            "Multi-factor authentication setup: Download Microsoft Authenticator, go to myaccount.microsoft.com, select Security Info, and add the app as a sign-in method.",
            "Email signature guidelines: Font must be Arial 10pt. Include name, title, phone, and company logo. Do not add personal quotes or images.",
        ]
        ids = [f"doc{i}" for i in range(len(docs))]
        collection.add(documents=docs, ids=ids)
        print("Knowledge base seeded with IT support articles.")

    return collection

# Initialize on import
_kb_collection = init_knowledge_base()

@tool
def search_knowledge_base(query: str) -> str:
    """Search internal IT knowledge base for support articles and procedures."""
    results = _kb_collection.query(query_texts=[query], n_results=2)
    docs = results["documents"][0]
    if not docs:
        return "No relevant articles found in the knowledge base."
    return "\n\n".join([f"Article {i+1}: {doc}" for i, doc in enumerate(docs)])