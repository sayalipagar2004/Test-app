import streamlit as st
import math

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ---------- INITIAL STATE ----------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "result" not in st.session_state:
    st.session_state.result = ""

# ---------- STYLE (loaded once) ----------
if "css_loaded" not in st.session_state:
    st.markdown("""
    <style>
    div[data-testid="stAppViewContainer"] {
        background-color: #0f0f0f;
    }
    h1, p {
        color: #fff;
        text-align: center;
    }
    .calculator {
        background-color: #1a1a1a;
        border-radius: 15px;
        padding: 20px;
        width: 340px;
        margin: auto;
        box-shadow: 0px 0px 15px rgba(0,255,255,0.4);
    }
    .display {
        background-color: #000;
        color: #00ffcc;
        font-size: 24px;
        text-align: right;
        border-radius: 10px;
        padding: 10px 15px;
        border: 2px solid #00ffcc;
        height: 45px;
        overflow-x: auto;
    }
    .result-display {
        background-color: #111;
        color: #00ffcc;
        font-size: 20px;
        text-align: right;
        border-radius: 10px;
        padding: 6px 15px;
        border: 1px solid #00ffcc;
        margin-bottom: 12px;
        height: 35px;
    }
    button {
        font-weight: bold !important;
    }
    footer, .stDeployButton {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    st.session_state.css_loaded = True

st.title("🧮 Casio-Style Scientific Calculator")

# ---------- SAFE EVALUATION ----------
def safe_eval(expr):
    try:
        expr = expr.replace("^", "**")
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
        allowed.update({"abs": abs, "round": round})
        return eval(expr, {"__builtins__": None}, allowed)
    except Exception:
        return "Error"

# ---------- BUTTON LOGIC ----------
def press(key):
    if key == "=":
        st.session_state.result = str(safe_eval(st.session_state.expr))
    elif key == "C":  # backspace
        st.session_state.expr = st.session_state.expr[:-1]
    elif key == "AC":
        st.session_state.expr = ""
        st.session_state.result = ""
    elif key in ["sin", "cos", "tan", "sqrt", "log", "abs", "round"]:
        st.session_state.expr += f"math.{key}("
    elif key == "π":
        st.session_state.expr += str(math.pi)
    elif key == "e":
        st.session_state.expr += str(math.e)
    else:
        st.session_state.expr += key

# ---------- DISPLAY ----------
st.markdown('<div class="calculator">', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.expr}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="result-display">{st.session_state.result}</div>', unsafe_allow_html=True)

# ---------- BUTTON GRID ----------
buttons = [
    ["7", "8", "9", "÷", "sin"],
    ["4", "5", "6", "×", "cos"],
    ["1", "2", "3", "−", "tan"],
    ["0", ".", "(", ")", "+"],
    ["√", "log", "π", "e", "="],
    ["C", "AC", "^", "%", "round"]
]

mapping = {"÷": "/", "×": "*", "−": "-", "√": "sqrt", "π": "pi"}

cols = st.columns(5)
for row in buttons:
    for i, label in enumerate(row):
        with cols[i % 5]:
            if st.button(label, use_container_width=True):
                press(mapping.get(label, label))
    cols = st.columns(5)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><center><p style='color:#888;'>Casio fx-991EX inspired calculator built with ❤️ using Streamlit</p></center>", unsafe_allow_html=True)
