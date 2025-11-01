import streamlit as st
import math

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ---------- CUSTOM STYLE ----------
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
    border-radius: 20px;
    padding: 25px;
    width: 350px;
    margin: auto;
    box-shadow: 0px 0px 20px rgba(0,255,255,0.4);
}
.display {
    background-color: #000;
    color: #00ffcc;
    font-size: 26px;
    text-align: right;
    border-radius: 10px;
    padding: 10px 15px;
    border: 2px solid #00ffcc;
    height: 50px;
    overflow-x: auto;
}
.result-display {
    background-color: #111;
    color: #00ffcc;
    font-size: 22px;
    text-align: right;
    border-radius: 10px;
    padding: 8px 15px;
    border: 1px solid #00ffcc;
    margin-bottom: 15px;
    height: 40px;
}
button {
    font-weight: bold !important;
}
footer, .stDeployButton {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🧮 Casio-Style Scientific Calculator")

# ---------- STATE ----------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "result" not in st.session_state:
    st.session_state.result = ""

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
    elif key == "C":
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

# ---------- UI ----------
st.markdown('<div class="calculator">', unsafe_allow_html=True)

# Expression and result display
st.markdown(f'<div class="display">{st.session_state.expr}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="result-display">{st.session_state.result}</div>', unsafe_allow_html=True)

# Button Layout
buttons = [
    ["7", "8", "9", "÷", "sin"],
    ["4", "5", "6", "×", "cos"],
    ["1", "2", "3", "−", "tan"],
    ["0", ".", "(", ")", "+"],
    ["√", "log", "π", "e", "="],
    ["C", "^", "%", "abs", "round"]
]

# Render Buttons
for row in buttons:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, use_container_width=True):
                # Convert display symbols to Python operators
                mapping = {"÷": "/", "×": "*", "−": "-", "√": "sqrt", "π": "pi"}
                press(mapping.get(label, label))

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><center><p style='color:#888;'>Casio fx-991EX inspired calculator built with ❤️ using Streamlit</p></center>", unsafe_allow_html=True)
