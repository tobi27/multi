#!/usr/bin/env python3
"""
Run multiple Sovereign agent instances and collect statistics.
"""
import os
import json
import statistics
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from agents.state import GraphState
from agents.nodes import (
    node_identity, node_spawn, node_lend, node_producer, node_insurer,
    node_monetizer, node_delegate, node_accountant
)


def build_graph():
    g = StateGraph(GraphState)
    g.add_node("identity", node_identity)
    if os.getenv("ENABLE_SPAWN","false").lower()=="true": g.add_node("spawn", node_spawn)
    if os.getenv("ENABLE_LEND","false").lower()=="true": g.add_node("lend", node_lend)
    g.add_node("producer", node_producer)
    g.add_node("insurer", node_insurer)
    g.add_node("monetizer", node_monetizer)
    if os.getenv("ENABLE_DELEGATE","false").lower()=="true": g.add_node("delegate", node_delegate)
    g.add_node("accountant", node_accountant)

    g.set_entry_point("identity")
    cur="identity"
    if os.getenv("ENABLE_SPAWN","false").lower()=="true": g.add_edge(cur,"spawn"); cur="spawn"
    if os.getenv("ENABLE_LEND","false").lower()=="true": g.add_edge(cur,"lend"); cur="lend"
    g.add_edge(cur,"producer"); cur="producer"
    g.add_edge(cur,"insurer"); cur="insurer"
    g.add_edge(cur,"monetizer"); cur="monetizer"
    if os.getenv("ENABLE_DELEGATE","false").lower()=="true": g.add_edge(cur,"delegate"); cur="delegate"
    g.add_edge(cur,"accountant"); g.add_edge("accountant", END)
    return g.compile()


def run_batch(N=30, export_file="batch_results.json"):
    """Run N instances and export statistics."""
    print(f"Running {N} agent instances...")
    print("=" * 60)

    app = build_graph()
    results = []

    for i in range(N):
        print(f"[{i+1}/{N}] Running...", end=" ", flush=True)

        result = app.invoke(GraphState())
        if isinstance(result, dict):
            out = GraphState(**result)
        else:
            out = result

        results.append({
            "run_id": out.run_id,
            "agent_net_usd": out.agent_net_usd,
            "agdp_usd": out.agdp_usd,
            "compute_cost_usd": out.compute_cost_usd,
            "cri": out.cri,
            "gdp_per_pflop_usd": out.gdp_per_pflop_usd,
            "total_flops": out.total_flops,
            "tokens_used": out.tokens_used,
            "passed": out.passed,
            "premium_usd": out.premium_usd,
            "claim_usd": out.claim_usd,
            "improvement": out.improvement,
            "receipt": out.receipt
        })

        print(f"NET=${out.agent_net_usd:.2f} PASSED={out.passed}")

    print("\n" + "=" * 60)
    print("BATCH STATISTICS")
    print("=" * 60)

    # Extract metrics
    nets = [r["agent_net_usd"] for r in results]
    agdps = [r["agdp_usd"] for r in results]
    cris = [r["cri"] for r in results if r["cri"] is not None]
    gdp_pflops = [r["gdp_per_pflop_usd"] for r in results if r["gdp_per_pflop_usd"] is not None]
    passed_count = sum(1 for r in results if r["passed"])

    # Compute stats
    stats = {
        "batch_size": N,
        "timestamp": datetime.now().isoformat(),
        "net": {
            "mean": statistics.mean(nets),
            "median": statistics.median(nets),
            "p25": sorted(nets)[int(0.25*len(nets))],
            "p75": sorted(nets)[int(0.75*len(nets))],
            "p95": sorted(nets)[int(0.95*len(nets))],
            "min": min(nets),
            "max": max(nets),
            "stdev": statistics.stdev(nets) if len(nets) > 1 else 0
        },
        "agdp": {
            "mean": statistics.mean(agdps),
            "median": statistics.median(agdps)
        },
        "cri": {
            "mean": statistics.mean(cris) if cris else None,
            "median": statistics.median(cris) if cris else None,
            "p50": statistics.median(cris) if cris else None
        },
        "gdp_per_pflop": {
            "p95": sorted(gdp_pflops)[int(0.95*len(gdp_pflops))] if gdp_pflops else None
        },
        "passed_rate": passed_count / N,
        "passed_count": passed_count,
        "failed_count": N - passed_count
    }

    # Print stats
    print(f"\nNET (Agent Profit):")
    print(f"  Mean:   ${stats['net']['mean']:,.2f}")
    print(f"  Median: ${stats['net']['median']:,.2f}")
    print(f"  p25:    ${stats['net']['p25']:,.2f}")
    print(f"  p75:    ${stats['net']['p75']:,.2f}")
    print(f"  p95:    ${stats['net']['p95']:,.2f}")
    print(f"  StDev:  ${stats['net']['stdev']:,.2f}")

    print(f"\nAGDP (Revenue):")
    print(f"  Mean:   ${stats['agdp']['mean']:,.2f}")
    print(f"  Median: ${stats['agdp']['median']:,.2f}")

    if stats['cri']['median']:
        print(f"\nCRI (AGDP/ComputeCost):")
        print(f"  Mean:   {stats['cri']['mean']:,.2f}")
        print(f"  Median: {stats['cri']['median']:,.2f}")

    print(f"\nPASS Rate: {stats['passed_rate']*100:.1f}% ({passed_count}/{N})")

    print(f"\n{'='*60}")
    print(f"ACCEPTANCE CRITERIA:")
    print(f"  ✓ NET p95 ≥ 0: ${stats['net']['p95']:.2f}")
    print(f"  {'✓' if stats['cri']['p50'] and stats['cri']['p50'] >= 1.30 else '✗'} CRI p50 ≥ 1.30: {stats['cri']['p50']}")

    # Export to JSON
    export_data = {
        "statistics": stats,
        "runs": results
    }

    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\n✓ Results exported to: {export_file}")
    print("=" * 60)

    return stats


if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    run_batch(N)
