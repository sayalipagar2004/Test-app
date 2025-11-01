# app.py
import streamlit as st
import math

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

st.markdown(
    """
    <style>
    body { background-color: #121212; color: white; }
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #333;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #333;
        color: #00eaff;
        border: 1px solid #00eaff;
    }
    .display {
        font-size: 28px;
        background-color: #000;
        padding: 15px;
        border-radius: 10px;
        color: #00ffcc;
        text-align: right;
        margin-bottom: 10px;
        border: 2px solid #00ffcc;
        height: 70px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧮 Scientific Calculator")

# ---------- INIT ----------
if "expression" not in st.session_state:
    st.session_state.expression = ""

# ---------- SAFE EVALUATOR ----------
def safe_eval(expr):
    try:
        expr = expr.replace("^", "**")
        # allow math functions safely
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
        allowed.update({"abs": abs, "round": round})
        result = eval(expr, {"__builtins__": None}, allowed)
        return result
    except Exception:
        return "Error"

# ---------- DISPLAY ----------
st.markdown(f"<div class='display'>{st.session_state.expression}</div>", unsafe_allow_html=True)

# ---------- BUTTON GRID ----------
buttons = [
    ["7", "8", "9", "/", "sin"],
    ["4", "5", "6", "*", "cos"],
    ["1", "2", "3", "-", "tan"],
    ["0", ".", "(", ")", "+"],
    ["sqrt", "log", "pi", "e", "="],
    ["C", "^", "%", "abs", "round"],
]

for row in buttons:
    cols = st.columns(len(row))
    for i, key in enumerate(row):
        if cols[i].button(key):
            if key == "=":
                st.session_state.expression = str(safe_eval(st.session_state.expression))
            elif key == "C":
                st.session_state.expression = ""
            elif key in ["sin", "cos", "tan", "sqrt", "log", "abs", "round"]:
                st.session_state.expression += f"math.{key}("
            elif key == "pi":
                st.session_state.expression += str(math.pi)
            elif key == "e":
                st.session_state.expression += str(math.e)
            else:
                st.session_state.expression += key

# ---------- FOOTER ----------
st.markdown("---")
st.caption("Casio fx-991 style scientific calculator built with ❤️ using Streamlit.")
