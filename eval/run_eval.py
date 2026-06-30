"""
Evaluation harness for the ITSM agent.
Runs all test cases and scores pass/fail based on:
  1. Keyword presence in the final answer
  2. Whether the correct tool was called

Run with: python3 eval/run_eval.py
"""

import sys
import json
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from agent import build_agent

load_dotenv()


def run_test_case(agent, test_case: dict) -> dict:
    """Run a single test case and return results."""
    question = test_case["question"]
    expected_keywords = test_case["expected_keywords"]
    expected_tool = test_case["expected_tool"]

    config = {"configurable": {"thread_id": f"eval_{test_case['id']}"}}

    try:
        result = agent.invoke(
            {"messages": [("user", question)]},
            config=config
        )
    except Exception as e:
        return {
            "id": test_case["id"],
            "question": question,
            "passed": False,
            "keyword_score": 0,
            "tool_correct": False,
            "error": str(e),
            "answer": ""
        }

    # Extract final answer
    answer = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            answer = msg.content
            break

    # Extract tools that were actually called
    tools_called = []
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            tools_called.append(msg.name)

    # Score 1: keyword check
    answer_lower = answer.lower()
    keywords_found = [
        kw for kw in expected_keywords
        if kw.lower() in answer_lower
    ]
    keyword_score = len(keywords_found) / len(expected_keywords)
    keyword_pass = keyword_score >= 0.5  # pass if at least 50% of keywords present

    # Score 2: tool check
    tool_correct = expected_tool in tools_called

    passed = keyword_pass and tool_correct

    return {
        "id": test_case["id"],
        "question": question,
        "category": test_case["category"],
        "passed": passed,
        "keyword_score": round(keyword_score * 100),
        "keywords_found": keywords_found,
        "keywords_missing": [kw for kw in expected_keywords if kw.lower() not in answer_lower],
        "tool_correct": tool_correct,
        "tools_called": tools_called,
        "expected_tool": expected_tool,
        "answer": answer[:200]
    }


def main():
    # Load test cases
    test_cases_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(test_cases_path) as f:
        test_cases = json.load(f)

    print("Building agent...")
    agent = build_agent()

    print(f"Running {len(test_cases)} test cases...\n")

    results = []
    for tc in test_cases:
        print(f"Running {tc['id']}: {tc['question'][:50]}...")
        result = run_test_case(agent, tc)
        results.append(result)
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {status} | Keywords: {result['keyword_score']}% | Tool: {'✅' if result['tool_correct'] else '❌'} ({', '.join(result['tools_called'])})")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    keyword_avg = sum(r["keyword_score"] for r in results) / total
    tool_accuracy = sum(1 for r in results if r["tool_correct"]) / total * 100

    print(f"\n{'='*60}")
    print(f"EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests:      {total}")
    print(f"Passed:           {passed}/{total} ({round(passed/total*100)}%)")
    print(f"Keyword accuracy: {round(keyword_avg)}%")
    print(f"Tool accuracy:    {round(tool_accuracy)}%")

    # Show failures in detail
    failures = [r for r in results if not r["passed"]]
    if failures:
        print(f"\nFAILED TESTS:")
        for r in failures:
            print(f"\n  {r['id']}: {r['question']}")
            if not r["tool_correct"]:
                print(f"    Tool: expected '{r['expected_tool']}', got {r['tools_called']}")
            if r["keywords_missing"]:
                print(f"    Missing keywords: {r['keywords_missing']}")
            print(f"    Answer: {r['answer'][:150]}")

    # Save results to file
    output_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(output_path, "w") as f:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed,
                "pass_rate": round(passed/total*100),
                "keyword_accuracy": round(keyword_avg),
                "tool_accuracy": round(tool_accuracy)
            },
            "results": results
        }, f, indent=2)

    print(f"\nFull results saved to eval/eval_results.json")


if __name__ == "__main__":
    main()