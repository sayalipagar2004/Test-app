# app.py
"""
Casio-style Scientific Calculator (Streamlit)
Features:
- Button-grid UI resembling a scientific calculator layout
- Safe AST-based evaluator with a whitelist of functions/constants
- Degree / Radian toggle for trig functions
- Memory: M+, M-, MR, MC and Ans
- History and download
- Copy/paste friendly expression input
Run: streamlit run app.py
"""

import ast
import operator as op
import math
import json
from datetime import datetime

import streamlit as st

# -----------------------
# Safe evaluator
# -----------------------

# Basic binary operators map
_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.FloorDiv: op.floordiv,
}

# Unary operators
_UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

# Allowed names (constants) - filled later
# Allowed functions - filled by make_allowed_funcs so they can respect mode (deg/rad)


def make_allowed_funcs(mode: str):
    """
    Returns (allowed_funcs, allowed_names) depending on mode ('deg' or 'rad').
    For degree mode, trig functions convert input degrees->radians.
    """
    # wrappers for trig to respect mode
    if mode == "deg":
        def sin(x): return math.sin(math.radians(x))
        def cos(x): return math.cos(math.radians(x))
        def tan(x): return math.tan(math.radians(x))
        def asin(x): return math.degrees(math.asin(x))
        def acos(x): return math.degrees(math.acos(x))
        def atan(x): return math.degrees(math.atan(x))
    else:
        sin = math.sin
        cos = math.cos
        tan = math.tan
        asin = math.asin
        acos = math.acos
        atan = math.atan

    allowed_funcs = {
        # basic
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
        "fact": math.factorial,  # integer factorial; alias 'fact'
        "factorial": math.factorial,
        # exponentials and logs
        "exp": math.exp,
        "ln": math.log,  # natural log: ln(x)  -> math.log
        "log": math.log10,  # log10 by default
        "log2": math.log2,
        # trig
        "sin": sin,
        "cos": cos,
        "tan": tan,
        "asin": asin,
        "acos": acos,
        "atan": atan,
        # hyperbolic
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        # misc
        "gamma": math.gamma,
        "pow": math.pow,
        "pi": math.pi,  # note: name 'pi' will be treated as constant if used without ()
        "e": math.e,
    }

    # split constants from functions: keep constants also in allowed_names
    allowed_names = {"pi": math.pi, "e": math.e}
    # also allow true numeric constants spelled in expression like "ans"
    return allowed_funcs, allowed_names


class SafeEval(ast.NodeVisitor):
    """
    AST-based evaluator that only allows:
    - numeric constants
    - binops: + - * / % // **
    - unary +/-
    - function calls for whitelisted functions only (single-name calls)
    - names that map to allowed constants (pi, e, ans, mem)
    """

    def __init__(self, allowed_funcs: dict, allowed_names: dict):
        self.allowed_funcs = allowed_funcs
        self.allowed_names = allowed_names

    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        return super().visit(node)

    def visit_Constant(self, node):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")

    def visit_Num(self, node):  # older compatibility
        return node.n

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in _BIN_OPS:
            return _BIN_OPS[op_type](left, right)
        raise ValueError(f"Operator {op_type} is not allowed")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in _UNARY_OPS:
            return _UNARY_OPS[op_type](operand)
        raise ValueError(f"Unary operator {op_type} is not allowed")

    def visit_Call(self, node):
        # Only simple calls like sin(x) where func is Name allowed
        if isinstance(node.func, ast.Name):
            fname = node.func.id
            if fname not in self.allowed_funcs:
                raise ValueError(f"Function '{fname}' is not allowed")
            func = self.allowed_funcs[fname]
            args = [self.visit(arg) for arg in node.args]
            # no keywords allowed
            if node.keywords:
                raise ValueError("Keyword arguments not allowed")
            try:
                return func(*args)
            except Exception as e:
                raise ValueError(f"Error calling {fname}: {e}")
        raise ValueError("Only direct function calls by name are allowed")

    def visit_Name(self, node):
        if node.id in self.allowed_names:
            return self.allowed_names[node.id]
        # disallow other names (variables, attributes)
        raise ValueError(f"Name '{node.id}' is not allowed")

    def generic_visit(self, node):
        # block any other node types (comprehensions, attributes, etc.)
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def safe_eval(expr: str, mode: str = "rad", extra_names: dict = None):
    """
    Evaluate expression safely with whitelist.
    `mode` is 'rad' or 'deg' and affects trig wrappers.
    `extra_names` can include 'ans' or 'mem' values as numeric constants.
    """
    allowed_funcs, allowed_names = make_allowed_funcs(mode)
    if extra_names:
        allowed_names = {**allowed_names, **extra_names}

    # Parse expression into AST
    try:
        parsed = ast.parse(expr, mode="eval")
    except Exception as e:
        raise ValueError(f"Parse error: {e}")

    evaluator = SafeEval(allowed_funcs, allowed_names)
    return evaluator.visit(parsed)

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Casio-style Scientific Calculator", layout="centered")
st.title("🔢 Casio-style Scientific Calculator (fx-991 like)")

# Initialize session state
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "ans" not in st.session_state:
    st.session_state.ans = 0
if "mem" not in st.session_state:
    st.session_state.mem = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "mode" not in st.session_state:
    st.session_state.mode = "deg"  # default to degrees because many prefer that
if "last_error" not in st.session_state:
    st.session_state.last_error = ""

# helpers
def append_to_expr(token: str):
    st.session_state.expr = st.session_state.expr + token

def set_expr(value: str):
    st.session_state.expr = value

def clear_expr():
    st.session_state.expr = ""

def backspace():
    st.session_state.expr = st.session_state.expr[:-1]

def evaluate_expression():
    expr = st.session_state.expr.strip()
    if expr == "":
        st.session_state.last_error = "Empty expression."
        return
    try:
        val = safe_eval(expr, mode=st.session_state.mode, extra_names={"ans": st.session_state.ans, "mem": st.session_state.mem})
        # formatting: convert to int if integral
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        st.session_state.ans = val
        st.session_state.history.insert(0, {"expression": expr, "result": val, "time": datetime.now().isoformat(timespec="seconds"), "mode": st.session_state.mode})
        st.session_state.expr = str(val)
        st.session_state.last_error = ""
    except Exception as e:
        st.session_state.last_error = str(e)

def do_clear_history():
    st.session_state.history = []

def memory_store_add():
    try:
        # treat current expression value if possible, else current ans
        val = safe_eval(st.session_state.expr, mode=st.session_state.mode, extra_names={"ans": st.session_state.ans, "mem": st.session_state.mem})
    except Exception:
        val = st.session_state.ans
    st.session_state.mem += val

def memory_sub():
    try:
        val = safe_eval(st.session_state.expr, mode=st.session_state.mode, extra_names={"ans": st.session_state.ans, "mem": st.session_state.mem})
    except Exception:
        val = st.session_state.ans
    st.session_state.mem -= val

def memory_recall():
    st.session_state.expr += str(st.session_state.mem)

def memory_clear():
    st.session_state.mem = 0

def toggle_mode():
    st.session_state.mode = "rad" if st.session_state.mode == "deg" else "deg"

# Top row: display and basic controls
col_disp, col_mode = st.columns([4,1])
with col_disp:
    # show expression editable so user can paste
    st.text_input("Expression", key="expr", value=st.session_state.expr, on_change=lambda: None)
    if st.session_state.last_error:
        st.error("Error: " + st.session_state.last_error)
with col_mode:
    st.markdown("Mode")
    if st.button("Deg↔Rad"):
        toggle_mode()
    st.write(f"**{st.session_state.mode.upper()}**")
    st.write(f"Ans = {st.session_state.ans}")
    st.write(f"Mem = {st.session_state.mem}")

st.markdown("---")

# Buttons grid (rows similar to a scientific calculator)
def button(label, new_token=None, width=1, key=None, on_click=None):
    if new_token is None:
        new_token = label
    if key is None:
        key = f"btn_{label}_{new_token}"
    return st.button(label, key=key, on_click=on_click, args=() )  # we'll handle token appending via on_click wrappers below

# We'll create a bunch of on_click wrappers to append tokens (must be functions without args for on_click)
def make_append_fn(tok):
    def _fn():
        append_to_expr(tok)
    return _fn

# row layout helpers: build rows with many columns
def row_buttons(labels, tokens=None, keys=None, callbacks=None):
    cols = st.columns(len(labels))
    for c, lab in zip(cols, labels):
        with c:
            tok = None
            if tokens:
                tok = tokens[labels.index(lab)]
            k = None
            if keys:
                k = keys[labels.index(lab)]
            cb = None
            if callbacks:
                cb = callbacks[labels.index(lab)]
            if cb:
                st.button(lab, key=k or f"key_{lab}", on_click=cb)
            else:
                st.button(lab, key=k or f"key_{lab}", on_click=make_append_fn(tok or lab))

# First row: Clear, backspace, parentheses, divide
r = st.columns(6)
with r[0]:
    st.button("AC", on_click=lambda: set_expr(""))
with r[1]:
    st.button("⌫", on_click=backspace)
with r[2]:
    st.button("(", on_click=make_append_fn("("))
with r[3]:
    st.button(")", on_click=make_append_fn(")"))
with r[4]:
    st.button("%", on_click=make_append_fn("%"))
with r[5]:
    st.button("÷", on_click=make_append_fn("/"))

# Second row: functions
r = st.columns(6)
with r[0]:
    st.button("sin", on_click=make_append_fn("sin("))
with r[1]:
    st.button("cos", on_click=make_append_fn("cos("))
with r[2]:
    st.button("tan", on_click=make_append_fn("tan("))
with r[3]:
    st.button("ln", on_click=make_append_fn("ln("))
with r[4]:
    st.button("log", on_click=make_append_fn("log("))
with r[5]:
    st.button("√", on_click=make_append_fn("sqrt("))

# Third row: powers and factorial
r = st.columns(6)
with r[0]:
    st.button("x²", on_click=make_append_fn("**2"))
with r[1]:
    st.button("x^y", on_click=make_append_fn("**"))
with r[2]:
    st.button("10^x", on_click=make_append_fn("pow(10,"))
with r[3]:
    st.button("e^x", on_click=make_append_fn("exp("))
with r[4]:
    st.button("n!", on_click=make_append_fn("factorial("))
with r[5]:
    st.button("Ans", on_click=lambda: append_to_expr(str(st.session_state.ans)))

# Digits and basic ops (4 rows of digits)
digit_rows = [
    ("7","8","9","×"),
    ("4","5","6","-"),
    ("1","2","3","+"),
    ("0",".","±","="),
]
for row in digit_rows:
    cols = st.columns(4)
    for i, label in enumerate(row):
        with cols[i]:
            if label.isdigit():
                st.button(label, on_click=make_append_fn(label))
            elif label == ".":
                st.button(".", on_click=make_append_fn("."))
            elif label == "±":
                st.button("±", on_click=lambda: append_to_expr("*(-1)"))  # quick way to invert
            elif label in "+-×=":
                if label == "×":
                    st.button("×", on_click=make_append_fn("*"))
                elif label == "=":
                    st.button("=", on_click=evaluate_expression)
                else:
                    st.button(label, on_click=make_append_fn(label))

# Third column: second set of scientific operations + memory
st.markdown("### Memory & Extra")
mem_cols = st.columns(4)
with mem_cols[0]:
    st.button("M+", on_click=memory_store_add)
with mem_cols[1]:
    st.button("M-", on_click=memory_sub)
with mem_cols[2]:
    st.button("MR", on_click=memory_recall)
with mem_cols[3]:
    st.button("MC", on_click=memory_clear)

# Additional useful buttons
extra_cols = st.columns(6)
with extra_cols[0]:
    st.button("pi", on_click=make_append_fn("pi"))
with extra_cols[1]:
    st.button("e", on_click=make_append_fn("e"))
with extra_cols[2]:
    st.button("log2", on_click=make_append_fn("log2("))
with extra_cols[3]:
    st.button("x!", on_click=make_append_fn("factorial("))
with extra_cols[4]:
    st.button("floor", on_click=make_append_fn("floor("))
with extra_cols[5]:
    st.button("ceil", on_click=make_append_fn("ceil("))

st.markdown("---")

# History & download
st.markdown("### History")
if st.session_state.history:
    for i, item in enumerate(st.session_state.history[:30]):
        st.write(f"{i+1}. `{item['expression']}` = **{item['result']}**  — _{item['time']} ({item['mode']})_")
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("Clear history"):
            do_clear_history()
    with c2:
        history_json = json.dumps(st.session_state.history, indent=2)
        st.download_button("Download history (JSON)", data=history_json, file_name="calc_history.json", mime="application/json")
else:
    st.info("No history yet. Press = to evaluate an expression.")

st.markdown("---")
st.caption("Notes: Trig functions obey the selected MODE. Use 'Ans' to reuse the previous result; 'mem' is accessible via MR. Functions must be called with parentheses, e.g. sin(30), log(100).")

