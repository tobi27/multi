from .state import GraphState
from .tools import (
    tool_producer_oracle, tool_producer_csv, tool_producer_llm, tool_insurer, tool_monetizer,
    tool_spawn, tool_lend, tool_delegate
)

def node_identity(state: GraphState)->GraphState:
    return state

def node_spawn(state: GraphState)->GraphState:
    return tool_spawn(state)

def node_lend(state: GraphState)->GraphState:
    return tool_lend(state)

def node_producer(state: GraphState)->GraphState:
    state = tool_producer_oracle(state)  # priorité à oracle.json si présent
    state = tool_producer_csv(state)     # fallback/complément (CSV ou synth)
    return tool_producer_llm(state)      # complément LLM si clé présente

def node_insurer(state: GraphState)->GraphState:
    return tool_insurer(state)

def node_monetizer(state: GraphState)->GraphState:
    return tool_monetizer(state)

def node_delegate(state: GraphState)->GraphState:
    return tool_delegate(state)

def node_accountant(state: GraphState)->GraphState:
    return state.finalize()
