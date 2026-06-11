"""
Helpers for displaying LLM answers nicely in Jupyter.
"""

from IPython.display import display, Markdown


def format_agentic_answer(answer_blocks: list) -> str:
    """
    Convert a list of {'type': 'text'|'reference', ...} blocks into a single
    markdown string, with reference blocks rendered as [Source N] tags.
    """
    parts = []
    for block in answer_blocks:
        if block["type"] == "text":
            parts.append(block["text"])
        elif block["type"] == "reference":
            ids = ", ".join(str(i) for i in block.get("reference_ids", []))
            parts.append(f" `[Source {ids}]`")
    return "".join(parts)


def display_agentic_answer(answer_blocks: list, title: str = "AGENTIC ANSWER"):
    print("═" * 62)
    print(f"  {title}")
    print("═" * 62)
    display(Markdown(format_agentic_answer(answer_blocks)))
