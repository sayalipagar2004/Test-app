import streamlit as st
import math

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ---------- CUSTOM STYLES ----------
st.markdown("""
<style>
body {
    background-color: #0f0f0f;
}
div[data-testid="stAppViewContainer"] {
    background-color: #0f0f0f;
}
.calculator {
    background-color: #1a1a1a;
    border-radius: 20px;
    padding: 25px;
    width: 350px;
    margin: auto;
    box-shadow: 0px 0px 25px rgba(0,255,255,0.4);
}
.display {
    background-color: #000;
    color: #00ffcc;
    font-size: 28px;
    text-align: right;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    border: 2px solid #00ffcc;
    height: 60px;
    overflow-x: auto;
}
.grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-gap: 10px;
}
button.cal-btn {
    background-color: #222;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 20px;
    height: 60px;
    width: 100%;
    transition: all 0.2s;
}
button.cal-btn:hover {
    background-color: #00eaff;
    color: #000;
    font-weight: bold;
}
footer, .stDeployButton, #MainMenu, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🧮 Casio fx-991 Style Calculator")

# ---------- SESSION STATE ----------
if "expr" not in st.session_state:
    st.session_state.expr = ""

# ---------- SAFE EVALUATOR ----------
def safe_eval(expr):
    try:
        expr = expr.replace("^", "**")
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
        allowed.update({"abs": abs, "round": round})
        return eval(expr, {"__builtins__": None}, allowed)
    except Exception:
        return "Error"

# ---------- BUTTON HANDLER ----------
def press(key):
    if key == "=":
        st.session_state.expr = str(safe_eval(st.session_state.expr))
    elif key == "C":
        st.session_state.expr = ""
    elif key in ["sin", "cos", "tan", "sqrt", "log", "abs", "round"]:
        st.session_state.expr += f"math.{key}("
    elif key == "pi":
        st.session_state.expr += str(math.pi)
    elif key == "e":
        st.session_state.expr += str(math.e)
    else:
        st.session_state.expr += key

# ---------- UI ----------
st.markdown('<div class="calculator">', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.expr}</div>', unsafe_allow_html=True)

# ---------- BUTTON GRID ----------
button_rows = [
    ["7", "8", "9", "/", "sin"],
    ["4", "5", "6", "*", "cos"],
    ["1", "2", "3", "-", "tan"],
    ["0", ".", "(", ")", "+"],
    ["sqrt", "log", "pi", "e", "="],
    ["C", "^", "%", "abs", "round"]
]

st.markdown('<div class="grid">', unsafe_allow_html=True)
for row in button_rows:
    for key in row:
        if st.button(key, key=key, help=key):
            press(key)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><center><p style='color:#888;'>Casio fx-991EX inspired calculator built with ❤️ using Streamlit</p></center>", unsafe_allow_html=True)
