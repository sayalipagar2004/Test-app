# app.py
import ast
import operator as op
import math
import json
from datetime import datetime
import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Casio fx-991 Streamlit Calculator", layout="centered")

# ---------- CUSTOM STYLES ----------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0d1117, #000);
    color: white;
}
.calc-container {
    background: linear-gradient(180deg, #111927, #0a0e16);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 0 30px rgba(0,0,0,0.5);
    max-width: 400px;
    margin: auto;
}
.display {
    background: #dfe6e9;
    color: #2d3436;
    border-radius: 10px;
    padding: 15px;
    text-align: right;
    font-size: 22px;
    font-family: 'Digital-7', monospace;
    margin-bottom: 15px;
    box-shadow: inset 0 0 5px #000;
}
button[kind="primary"] {
    border-radius: 50%;
}
.stButton>button {
    width: 100%;
    height: 50px;
    font-size: 18px;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    transform: scale(1.05);
}
.orange-btn button {
    background-color: #e17055 !important;
    color: white !important;
}
.blue-btn button {
    background-color: #0984e3 !important;
    color: white !important;
}
.gray-btn button {
    background-color: #636e72 !important;
    color: white !important;
}
.white-btn button {
    background-color: #dfe6e9 !important;
    color: #2d3436 !important;
}
.mode-toggle {
    color: #74b9ff;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SAFE EVALUATION ----------
ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
    ast.USub: op.neg, ast.UAdd: op.pos
}

def make_funcs(mode):
    if mode == "DEG":
        def sin(x): return math.sin(math.radians(x))
        def cos(x): return math.cos(math.radians(x))
        def tan(x): return math.tan(math.radians(x))
        def asin(x): return math.degrees(math.asin(x))
        def acos(x): return math.degrees(math.acos(x))
        def atan(x): return math.degrees(math.atan(x))
    else:
        sin, cos, tan, asin, acos, atan = (
            math.sin, math.cos, math.tan, math.asin, math.acos, math.atan)

    funcs = {
        "sin": sin, "cos": cos, "tan": tan,
        "asin": asin, "acos": acos, "atan": atan,
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "exp": math.exp, "abs": abs, "floor": math.floor, "ceil": math.ceil,
        "pi": math.pi, "e": math.e, "fact": math.factorial, "factorial": math.factorial,
        "pow": math.pow, "round": round
    }
    return funcs

def safe_eval(expr, mode, ans):
    funcs = make_funcs(mode)
    names = {"pi": math.pi, "e": math.e, "ans": ans}

    def _eval(node):
        if isinstance(node, ast.Expression): return _eval(node.body)
        elif isinstance(node, ast.Num): return node.n
        elif isinstance(node, ast.Constant): return node.value
        elif isinstance(node, ast.BinOp): return ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp): return ALLOWED_OPS[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.Name): return names[node.id]
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in funcs:
                return funcs[node.func.id](*[_eval(a) for a in node.args])
        raise ValueError("Invalid input")

    return _eval(ast.parse(expr, mode='eval'))

# ---------- STATE ----------
if "expr" not in st.session_state: st.session_state.expr = ""
if "ans" not in st.session_state: st.session_state.ans = 0
if "mode" not in st.session_state: st.session_state.mode = "DEG"

# ---------- FUNCTIONS ----------
def press(x): st.session_state.expr += x
def clear(): st.session_state.expr = ""
def back(): st.session_state.expr = st.session_state.expr[:-1]
def equal():
    try:
        st.session_state.ans = safe_eval(st.session_state.expr, st.session_state.mode, st.session_state.ans)
        st.session_state.expr = str(st.session_state.ans)
    except Exception:
        st.session_state.expr = "Error"

def toggle_mode():
    st.session_state.mode = "RAD" if st.session_state.mode == "DEG" else "DEG"

# ---------- UI ----------
with st.container():
    st.markdown("<div class='calc-container'>", unsafe_allow_html=True)
    st.markdown(f"<div class='display'>{st.session_state.expr or '0'}</div>", unsafe_allow_html=True)
    st.markdown(f"<p class='mode-toggle'>Mode: {st.session_state.mode}</p>", unsafe_allow_html=True)

    # BUTTON LAYOUT
    btn_rows = [
        [("AC","gray-btn",clear), ("⌫","gray-btn",back), ("(", "gray-btn",lambda: press("(")), (")","gray-btn",lambda: press(")")), ("/","orange-btn",lambda: press("/"))],
        [("sin","blue-btn",lambda: press("sin(")), ("cos","blue-btn",lambda: press("cos(")), ("tan","blue-btn",lambda: press("tan(")), ("log","blue-btn",lambda: press("log(")), ("√","blue-btn",lambda: press("sqrt("))],
        [("7","white-btn",lambda: press("7")), ("8","white-btn",lambda: press("8")), ("9","white-btn",lambda: press("9")), ("*","orange-btn",lambda: press("*")), ("^","blue-btn",lambda: press("**"))],
        [("4","white-btn",lambda: press("4")), ("5","white-btn",lambda: press("5")), ("6","white-btn",lambda: press("6")), ("-","orange-btn",lambda: press("-")), ("π","blue-btn",lambda: press("pi"))],
        [("1","white-btn",lambda: press("1")), ("2","white-btn",lambda: press("2")), ("3","white-btn",lambda: press("3")), ("+","orange-btn",lambda: press("+")), ("Ans","blue-btn",lambda: press("ans"))],
        [("0","white-btn",lambda: press("0")), (".","white-btn",lambda: press(".")), ("EXP","blue-btn",lambda: press("exp(")), ("x!","blue-btn",lambda: press("factorial(")), ("=","orange-btn",equal)],
    ]
    for row in btn_rows:
        cols = st.columns(len(row))
        for i, (label, color, func) in enumerate(row):
            with cols[i]:
                st.markdown(f"<div class='{color}'>", unsafe_allow_html=True)
                st.button(label, on_click=func)
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("Mode: DEG/RAD", on_click=toggle_mode)
    with c2:
        st.write(f"Ans = {st.session_state.ans}")

    st.markdown("</div>", unsafe_allow_html=True)
