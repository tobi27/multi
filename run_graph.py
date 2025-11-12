#!/usr/bin/env python3
"""
Run the Sovereign MVP pipeline with real data/LLM/payments.
"""
import sys
import uuid
import json
from langgraph.graph import StateGraph, END

from agents.state import GraphState
from agents.nodes import producer_node, insurer_node, platform_node, finalize_node


def build_graph():
    """Build the LangGraph pipeline."""
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("producer", producer_node)
    graph.add_node("insurer", insurer_node)
    graph.add_node("platform", platform_node)
    graph.add_node("finalize", finalize_node)

    # Define edges
    graph.set_entry_point("producer")
    graph.add_edge("producer", "insurer")
    graph.add_edge("insurer", "platform")
    graph.add_edge("platform", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


def main():
    """Main execution."""
    print("=" * 60)
    print("SOVEREIGN MVP - REAL DATA PIPELINE")
    print("=" * 60)

    # Create initial state
    run_id = str(uuid.uuid4())[:8]
    initial_state = GraphState(run_id=run_id)

    print(f"Run ID: {run_id}")
    print(f"Agent ID: {initial_state.agent_id}")
    print(f"Trust Score: {initial_state.trust_score}")
    print()

    # Build and run graph
    print("Building pipeline...")
    app = build_graph()

    print("Executing pipeline...")
    print("-" * 60)

    result = app.invoke(initial_state)

    # LangGraph returns a dict, convert back to GraphState
    if isinstance(result, dict):
        final_state = GraphState(**result)
    else:
        final_state = result

    print("-" * 60)
    print("\n")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    summary = final_state.summary()
    for key, value in summary.items():
        print(f"{key:25s}: {value}")

    print()
    print("=" * 60)
    print("DETAILED ACTIONS")
    print("=" * 60)

    for i, action in enumerate(final_state.actions, 1):
        print(f"\n{i}. {action.kind}")
        print(f"   FLOPs: {action.flops:,}")
        print(f"   Value: €{action.value_eur:.2f}")
        if action.details:
            print(f"   Details: {json.dumps(action.details, indent=6)}")

    print()
    print("=" * 60)
    print("LEDGER RECEIPT")
    print("=" * 60)
    print(f"Run ID: {final_state.run_id}")
    print(f"SHA-256: {final_state.sha256}")
    print(f"Timestamp: {final_state.timestamp}")
    print(f"Stripe Intents: {len(final_state.stripe_intents)}")

    for intent in final_state.stripe_intents:
        print(f"  - {intent['type']}: {intent.get('intent_id', 'N/A')} "
              f"(€{intent.get('amount_eur', 0):.2f})")

    print()
    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)

    if final_state.sla_passed:
        print("✓ SLA PASSED")
    else:
        print("✗ SLA FAILED (claim triggered)")

    if final_state.agent_net_eur > 0:
        print(f"✓ Agent NET positive: €{final_state.agent_net_eur:.2f}")
    else:
        print(f"✗ Agent NET negative: €{final_state.agent_net_eur:.2f}")

    print()
    print("Ledger saved to: proofs.sqlite")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
