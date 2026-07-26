from langchain_core.tools import tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b


BASIC_TOOLS = [add, multiply]
