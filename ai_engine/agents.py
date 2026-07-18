import uuid
from typing import List, TypedDict

from langgraph.graph import END, StateGraph

from ai_engine import llm, rag
from ai_engine.prompts import QA_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT, build_qa_prompt, build_summary_prompt

class QAState(TypedDict, total=False):
    novel_id: uuid.UUID
    question: str
    top_k: int
    context_chunks: List[dict]
    answer: str


def _qa_retrieve_node(state: QAState) -> QAState:
    chunks = rag.retrieve_relevant_chunks(
        state["novel_id"], state["question"], top_k=state.get("top_k", 5)
    )
    return {"context_chunks": chunks}


def _qa_generate_node(state: QAState) -> QAState:
    documents = [c["document"] for c in state.get("context_chunks", [])]
    prompt = build_qa_prompt(state["question"], documents)
    answer = llm.generate(prompt, system=QA_SYSTEM_PROMPT, temperature=0.2)
    return {"answer": answer}


def build_qa_graph():
    graph = StateGraph(QAState)
    graph.add_node("retrieve", _qa_retrieve_node)
    graph.add_node("generate", _qa_generate_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


_qa_graph = None


def run_qa(novel_id: uuid.UUID, question: str, top_k: int = 5) -> QAState:
    """Run the compiled QA graph and return the final state (answer + context_chunks)."""
    global _qa_graph
    if _qa_graph is None:
        _qa_graph = build_qa_graph()
    return _qa_graph.invoke({"novel_id": novel_id, "question": question, "top_k": top_k})


class SummaryState(TypedDict, total=False):
    novel_title: str
    chapters_text: str
    summary: str


def _summary_generate_node(state: SummaryState) -> SummaryState:
    prompt = build_summary_prompt(state["novel_title"], state["chapters_text"])
    summary = llm.generate(prompt, system=SUMMARY_SYSTEM_PROMPT, temperature=0.4)
    return {"summary": summary}


def build_summary_graph():
    graph = StateGraph(SummaryState)
    graph.add_node("generate", _summary_generate_node)
    graph.set_entry_point("generate")
    graph.add_edge("generate", END)
    return graph.compile()


_summary_graph = None


def run_summary(novel_title: str, chapters_text: str) -> SummaryState:
    """Run the compiled summary graph and return the final state (summary)."""
    global _summary_graph
    if _summary_graph is None:
        _summary_graph = build_summary_graph()
    return _summary_graph.invoke({"novel_title": novel_title, "chapters_text": chapters_text})
