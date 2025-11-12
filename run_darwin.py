#!/usr/bin/env python3
"""
Darwinian Engine + mini-MARL (UCB) for adaptive token allocation.
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
from agents.darwin import fitness, thermostat_adjust, apply_thermostat, allocate_tokens
from agents.bandit import UCB, gen_variants


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


def run_darwin(export_file="darwin_results.json"):
    """Run Darwinian Engine with UCB-based token allocation."""

    # Load Darwin params
    R = int(os.getenv("DE_ROUNDS", "3"))
    P = int(os.getenv("DE_POP", "4"))
    BUDGET = int(os.getenv("DE_BUDGET_TOKENS", "120000"))
    MIN_TOK = int(os.getenv("DE_MIN_TOKENS_AGENT", "4000"))
    MAX_TOK = int(os.getenv("DE_MAX_TOKENS_AGENT", "60000"))
    TARGET_CRI = float(os.getenv("DE_TARGET_CRI", "1.30"))
    TARGET_P95_NET = float(os.getenv("DE_TARGET_P95_NET", "0.0"))
    PRICE_STEP_UP = float(os.getenv("DE_PRICE_STEP_UP", "0.10"))
    COVERAGE_STEP_DOWN = float(os.getenv("DE_COVERAGE_STEP_DOWN", "0.10"))
    COVERAGE_FLOOR = float(os.getenv("DE_COVERAGE_FLOOR", "0.30"))

    print("=" * 70)
    print("DARWINIAN ENGINE + mini-MARL (UCB)")
    print("=" * 70)
    print(f"Rounds: {R} | Population: {P} | Budget: {BUDGET:,} tokens")
    print(f"Target: CRI≥{TARGET_CRI}, NET_p95≥{TARGET_P95_NET}")
    print("=" * 70)

    app = build_graph()
    ucb = UCB()
    all_results = []
    thermo_log = []

    for round_idx in range(R):
        print(f"\n{'='*70}")
        print(f"ROUND {round_idx+1}/{R}")
        print("=" * 70)

        # Generate P arms with variants
        arms = gen_variants(P)

        # Allocate tokens via darwin.allocate_tokens()
        fitness_dummy = [1.0] * P  # Start with uniform for first round
        if round_idx > 0:
            # Use fitness from previous round
            prev_fitness = [r.get("fitness_eta", 1.0) for r in all_results[-P:]]
            fitness_dummy = prev_fitness

        quotas = allocate_tokens(fitness_dummy, BUDGET, MIN_TOK, MAX_TOK)

        round_results = []

        for i, arm in enumerate(arms):
            print(f"\n[{i+1}/{P}] Arm: {arm} | Quota: {quotas[i]:,} tokens", end=" ")

            # Override state params with arm variant
            state_init = GraphState()
            state_init.quota_tokens = quotas[i]

            # Apply arm variants
            if "price_mul" in arm:
                state_init.price_per_point *= arm["price_mul"]
            if "coverage_mul" in arm:
                state_init.coverage *= arm["coverage_mul"]

            # Run agent
            result = app.invoke(state_init)
            if isinstance(result, dict):
                out = GraphState(**result)
            else:
                out = result

            # Calculate fitness
            eta = fitness(out)
            out.fitness_eta = eta

            # Update UCB
            arm_str = json.dumps(arm, sort_keys=True)
            ucb.update(arm_str, eta)

            # Store results
            run_data = {
                "round": round_idx + 1,
                "arm": arm,
                "arm_str": arm_str,
                "quota_tokens": quotas[i],
                "run_id": out.run_id,
                "agent_net_usd": out.agent_net_usd,
                "agdp_usd": out.agdp_usd,
                "compute_cost_usd": out.compute_cost_usd,
                "cri": out.cri,
                "gdp_per_pflop_usd": out.gdp_per_pflop_usd,
                "total_flops": out.total_flops,
                "tokens_used": out.tokens_used,
                "passed": out.passed,
                "fitness_eta": eta,
                "improvement": out.improvement,
                "receipt": out.receipt
            }
            round_results.append(run_data)
            all_results.append(run_data)

            print(f"| NET=${out.agent_net_usd:.2f} CRI={out.cri} fitness={eta:.2f}")

        # Round statistics
        nets = [r["agent_net_usd"] for r in round_results]
        cris = [r["cri"] for r in round_results if r["cri"] is not None]
        fitnesses = [r["fitness_eta"] for r in round_results]

        cri_median = statistics.median(cris) if cris else None
        net_p95 = sorted(nets)[int(0.95*len(nets))] if len(nets) >= 2 else nets[0]

        print(f"\n{'='*70}")
        print(f"ROUND {round_idx+1} STATS:")
        print(f"  NET p95: ${net_p95:.2f}")
        print(f"  CRI p50: {cri_median}")
        print(f"  Fitness mean: {statistics.mean(fitnesses):.2f}")
        print("=" * 70)

        # Thermostat adjustment (after first round)
        if round_idx < R - 1:  # Don't adjust on last round
            # Convert round_results to GraphState objects for thermostat
            cohort_states = []
            for r in round_results:
                state_obj = GraphState()
                state_obj.agent_net_usd = r["agent_net_usd"]
                state_obj.cri = r["cri"]
                cohort_states.append(state_obj)

            env_vars = {
                "DE_TARGET_CRI": str(TARGET_CRI),
                "DE_TARGET_P95_NET": str(TARGET_P95_NET),
                "DE_PRICE_STEP_UP": str(PRICE_STEP_UP),
                "DE_COVERAGE_STEP_DOWN": str(COVERAGE_STEP_DOWN),
                "DE_COVERAGE_FLOOR": str(COVERAGE_FLOOR)
            }

            actions, stats = thermostat_adjust(env_vars, cohort_states)

            if actions:
                print(f"\n🌡️  THERMOSTAT ADJUSTMENT:")
                for action in actions:
                    print(f"  {action[0]} → {action[1]} by {action[2]*100:.0f}%")

                # Apply thermostat globally for next round
                changed = apply_thermostat(os.environ, actions)
                print(f"  Changes applied: {changed}")

            thermo_log.append({
                "round": round_idx + 1,
                "cri_median": cri_median,
                "net_p95": net_p95,
                "actions": [str(a) for a in actions],
                "stats": stats
            })

    # Final statistics
    print(f"\n{'='*70}")
    print("DARWIN ENGINE FINAL STATISTICS")
    print("=" * 70)

    all_nets = [r["agent_net_usd"] for r in all_results]
    all_cris = [r["cri"] for r in all_results if r["cri"] is not None]
    all_fitnesses = [r["fitness_eta"] for r in all_results]
    passed_count = sum(1 for r in all_results if r["passed"])

    final_stats = {
        "total_runs": len(all_results),
        "rounds": R,
        "population_per_round": P,
        "timestamp": datetime.now().isoformat(),
        "net": {
            "mean": statistics.mean(all_nets),
            "median": statistics.median(all_nets),
            "p95": sorted(all_nets)[int(0.95*len(all_nets))],
            "min": min(all_nets),
            "max": max(all_nets)
        },
        "cri": {
            "mean": statistics.mean(all_cris) if all_cris else None,
            "median": statistics.median(all_cris) if all_cris else None,
            "p50": statistics.median(all_cris) if all_cris else None
        },
        "fitness": {
            "mean": statistics.mean(all_fitnesses),
            "median": statistics.median(all_fitnesses),
            "max": max(all_fitnesses)
        },
        "passed_rate": passed_count / len(all_results),
        "passed_count": passed_count,
        "targets": {
            "cri_target": TARGET_CRI,
            "net_p95_target": TARGET_P95_NET,
            "cri_met": (statistics.median(all_cris) >= TARGET_CRI) if all_cris else False,
            "net_met": sorted(all_nets)[int(0.95*len(all_nets))] >= TARGET_P95_NET
        }
    }

    print(f"\nNET (Agent Profit):")
    print(f"  Mean:   ${final_stats['net']['mean']:,.2f}")
    print(f"  Median: ${final_stats['net']['median']:,.2f}")
    print(f"  p95:    ${final_stats['net']['p95']:,.2f}")

    if final_stats['cri']['median']:
        print(f"\nCRI (AGDP/ComputeCost):")
        print(f"  Mean:   {final_stats['cri']['mean']:,.2f}")
        print(f"  Median: {final_stats['cri']['median']:,.2f}")

    print(f"\nFitness (η):")
    print(f"  Mean:   {final_stats['fitness']['mean']:.2f}")
    print(f"  Median: {final_stats['fitness']['median']:.2f}")
    print(f"  Max:    {final_stats['fitness']['max']:.2f}")

    print(f"\nPASS Rate: {final_stats['passed_rate']*100:.1f}% ({passed_count}/{len(all_results)})")

    print(f"\n{'='*70}")
    print("TARGET ACHIEVEMENT:")
    status_cri = "✓" if final_stats['targets']['cri_met'] else "✗"
    status_net = "✓" if final_stats['targets']['net_met'] else "✗"
    print(f"  {status_cri} CRI p50 ≥ {TARGET_CRI}: {final_stats['cri']['p50']}")
    print(f"  {status_net} NET p95 ≥ {TARGET_P95_NET}: ${final_stats['net']['p95']:.2f}")
    print("=" * 70)

    # Export results
    export_data = {
        "statistics": final_stats,
        "thermostat_log": thermo_log,
        "ucb_state": {
            "arms": list(ucb.mean.keys()),
            "means": ucb.mean,
            "counts": ucb.n
        },
        "runs": all_results
    }

    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\n✓ Results exported to: {export_file}")
    print("=" * 70)

    return final_stats


if __name__ == "__main__":
    run_darwin()
