import ast
import operator
from typing import Any
from langchain_core.tools import tool

# Supported operators for safe AST arithmetic evaluation
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: Any) -> float | int:
    """Recursively evaluate an AST node safely without using raw eval()."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type in _OPERATORS:
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero is undefined.")
            return _OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op_type = type(node.op)
        if op_type in _OPERATORS:
            return _OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


@tool
def calculator(expression: str) -> str:
    """Perform safe mathematical calculations for arithmetic expressions.

    Input: A mathematical expression string, e.g. '15 * 4 + 2' or '(100 / 4) ** 2'.
    Output: The calculated numeric result as a string.
    """
    try:
        clean_expr = expression.strip()
        parsed = ast.parse(clean_expr, mode="eval")
        result = _eval_node(parsed.body)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero is undefined."
    except Exception as exc:
        return f"Error evaluating arithmetic expression '{expression}': {exc}"
