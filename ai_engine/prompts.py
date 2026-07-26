from typing import List

SUMMARY_SYSTEM_PROMPT = (
    "You are a skilled book-jacket copywriter for an online novel platform. "
    "Write engaging, spoiler-light summaries that make readers want to keep reading. "
    "Never reveal major twists or the ending."
)


def build_summary_prompt(novel_title: str, chapters_text: str) -> str:
    return (
        f'Write a short, engaging summary (3-5 sentences) of the novel "{novel_title}" '
        f"based on the following chapter content. Focus on the premise, setting, and main "
        f"character's situation. Do not reveal the ending or major plot twists.\n\n"
        f"CHAPTER CONTENT:\n{chapters_text}\n\nSUMMARY:"
    )

QA_SYSTEM_PROMPT = (
    "You are a helpful assistant answering reader questions about a specific novel, using "
    "only the story excerpts provided as context. If the answer isn't contained in the "
    "provided excerpts, say you don't have enough information from the story so far — do "
    "not make up plot details. Do not reveal spoilers beyond what's in the given excerpts."
)


def build_qa_prompt(question: str, context_chunks: List[str]) -> str:
    if not context_chunks:
        context_block = "(No story excerpts are available yet.)"
    else:
        context_block = "\n\n".join(
            f"Excerpt {i + 1}:\n{chunk}" for i, chunk in enumerate(context_chunks)
        )

    return (
        f"STORY EXCERPTS:\n{context_block}\n\n"
        f"READER QUESTION: {question}\n\n"
        f"Answer the question using only the excerpts above."
    )

PROOFREAD_SYSTEM_PROMPT = (
    "You are a careful line editor for fiction. Fix grammar, spelling, punctuation, and "
    "awkward phrasing while preserving the author's voice, tone, tense, dialogue, and "
    "paragraph breaks exactly as they are. Do not shorten, expand, or rewrite content, add "
    "new sentences, or change what happens in the scene. Return ONLY the corrected text, "
    "with no preamble, commentary, quotation marks, or markdown fences around it."
)


def build_proofread_prompt(text: str) -> str:
    return f"Correct grammar and spelling in the following chapter text:\n\n{text}"