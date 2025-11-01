# app.py
"""
Simple Streamlit calculator app with safe expression evaluation and history.
Drop this file into your repo and run: streamlit run app.py
"""

import ast
import operator as op
import streamlit as st
from datetime import datetime
import json

# ---------- Safe evaluator ----------
# allowed operators mapping
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    # (No bitwise ops)
}

def safe_eval(expr: str):
    """
    Safely evaluate a numeric expression using ast.
    Supports + - * / % ** and parentheses, unary +/-. Raises ValueError
    for anything else.
    """
    try:
        parsed = ast.parse(expr, mode='eval')
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Only numeric constants allowed")
        if isinstance(node, ast.Num):  # for older ast
            return node.n
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](left, right)
            else:
                raise ValueError(f"Operator {op_type} not allowed")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](operand)
            else:
                raise ValueError(f"Unary operator {op_type} not allowed")
        if isinstance(node, ast.Call):
            raise ValueError("Function calls are not allowed")
        # Any other node is rejected
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    result = _eval(parsed)
    return result

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Simple Calculator", layout="centered")

st.title("🧮 Simple Calculator (Safe Evaluation)")
st.write("Enter a numeric expression (e.g. `1+2*3`, `(4-1)/3`, `2**8`) and press **Calculate**.")

# Input area
expr = st.text_input("Expression", value="", placeholder="e.g. 12 + 3 * (4 - 1)")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Calculate"):
        if expr.strip() == "":
            st.warning("Please enter an expression.")
        else:
            try:
                result = safe_eval(expr)
                st.success(f"Result: `{result}`")
                # store history
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.insert(0, {
                    "expression": expr,
                    "result": result,
                    "time": datetime.now().isoformat(timespec='seconds')
                })
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("Clear history"):
        st.session_state.history = []
        st.experimental_rerun()

# Quick operator buttons
st.markdown("**Quick operators**")
ops = st.columns([1,1,1,1])
if ops[0].button("+"):
    expr += " + "
if ops[1].button("-"):
    expr += " - "
if ops[2].button("*"):
    expr += " * "
if ops[3].button("/"):
    expr += " / "
# update the text input with the appended operator if clicked
# (Streamlit doesn't allow directly modifying text_input value, so show the suggestion)
st.caption("Tip: you can build expressions using the input box; quick operator buttons append to the suggestion shown above.")

# History
st.markdown("### History")
history = st.session_state.get("history", [])
if history:
    for i, item in enumerate(history):
        st.write(f"{i+1}. `{item['expression']}` = **{item['result']}**  —  _{item['time']}_")
    # provide download of history
    if st.button("Download history (JSON)"):
        st.download_button(
            label="Download",
            data=json.dumps(history, indent=2),
            file_name="calc_history.json",
            mime="application/json"
        )
else:
    st.info("No history yet. Perform a calculation to see it here.")

st.markdown("---")
st.caption("Supported operators: `+`, `-`, `*`, `/`, `%`, `**` (power). Parentheses allowed. No functions or variables allowed — expressions are evaluated safely.")
