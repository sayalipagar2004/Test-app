import streamlit as st
import math
import cmath # Useful for potentially supporting complex numbers if needed

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ---------- INITIAL STATE ----------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "result" not in st.session_state:
    st.session_state.result = ""

# ---------- STYLE (loaded once) ----------
# Inject custom CSS for Casio-style look and responsive layout
st.markdown("""
<style>
div[data-testid="stAppViewContainer"] {
    background-color: #0f0f0f;
}
h1, p {
    color: #fff;
    text-align: center;
}
/* Main calculator body (responsive styling) */
.calculator {
    background-color: #1a1a1a;
    border-radius: 15px;
    padding: 20px;
    /* Fixed width for desktop, full width for mobile */
    max-width: 400px; 
    width: 95%; 
    margin: auto;
    box-shadow: 0px 0px 15px rgba(0,255,255,0.4);
}
/* Display for the current expression (green text on black background) */
.display {
    background-color: #000;
    color: #00ffcc;
    font-family: 'Courier New', monospace; /* Classic calculator font */
    font-size: 24px;
    text-align: right;
    border-radius: 10px;
    padding: 10px 15px;
    border: 2px solid #00ffcc;
    height: 45px;
    overflow-x: auto;
    white-space: nowrap; /* Ensures expression stays on one line */
    margin-bottom: 8px;
}
/* Display for the result */
.result-display {
    background-color: #111;
    color: #00ffcc;
    font-family: 'Courier New', monospace;
    font-size: 20px;
    font-weight: bold;
    text-align: right;
    border-radius: 10px;
    padding: 6px 15px;
    border: 1px solid #00ffcc;
    margin-bottom: 12px;
    height: 35px;
    overflow-x: auto;
    white-space: nowrap;
}
/* Streamlit button customization */
div[data-testid="stColumn"] button {
    background-color: #2a2a2a;
    color: #fff;
    border: 1px solid #444;
    border-radius: 8px;
    transition: background-color 0.2s, box-shadow 0.2s;
}
div[data-testid="stColumn"] button:hover {
    background-color: #3d3d3d;
    box-shadow: 0px 0px 5px rgba(0,255,255,0.2);
}
/* Specific style for operators and functions (Casio orange/red) */
div[data-testid="stColumn"]:nth-child(4) button, 
div[data-testid="stColumn"]:nth-child(5) button,
div[data-testid="stColumn"]:nth-child(1) button:nth-child(1) { /* First column, first button (AC) */
    background-color: #c9513e; 
    color: #fff;
}
div[data-testid="stColumn"]:nth-child(3) button:last-child { /* = button */
    background-color: #00ffcc;
    color: #1a1a1a;
    font-weight: bold !important;
}

/* Hide Streamlit footer and deploy button */
footer, .stDeployButton {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🧮 Casio-Style Scientific Calculator")

# --- SAFE EVALUATION ---
def safe_eval(expr):
    """Safely evaluates the expression using a limited set of allowed functions and modules."""
    
    # 1. Pre-process expression string
    expr = expr.replace("^", "**") # Standard power operator
    
    # 2. Define safe scopes
    # Locals/Globals allowed during eval: math, cmath, pi, e, abs, round
    safe_scope = {
        "math": math,
        "cmath": cmath,
        "pi": math.pi, 
        "e": math.e, 
        "abs": abs, 
        "round": round
    }

    try:
        # Use a safe environment (no __builtins__)
        result = eval(expr, {"__builtins__": None}, safe_scope)
        # Format complex numbers nicely if they result
        if isinstance(result, complex):
            return f"{result.real:.10g} + {result.imag:.10g}i" if result.imag != 0 else f"{result.real:.10g}"
        return f"{result:.10g}" # Format to 10 significant digits
    except Exception as e:
        # Catch common errors like ZeroDivisionError, SyntaxError, etc.
        return "Error"

# --- BUTTON LOGIC ---
def press(key):
    """Handles button presses and updates the session state expression."""
    
    # Clear result display on any input if it was an error or a final result
    if st.session_state.result in ["Error"] or (st.session_state.result and key not in ["="]):
        # If the key is a number or operator, and the result is present, start a new expression
        if key.isdigit() or key in ["(", "math.pi", "math.e", "/"]:
            st.session_state.expr = ""
        st.session_state.result = ""
        
    if key == "=":
        st.session_state.result = safe_eval(st.session_state.expr)
    elif key == "C":  # Backspace
        st.session_state.expr = st.session_state.expr[:-1]
    elif key == "AC":
        st.session_state.expr = ""
        st.session_state.result = ""
    elif key in ["math.sin(", "math.cos(", "math.tan(", "math.sqrt(", "math.log(", "abs(", "round("]:
        # Functions that require an opening parenthesis
        st.session_state.expr += key
    elif key == "math.pi":
        # Constants
        st.session_state.expr += "math.pi"
    elif key == "math.e":
        st.session_state.expr += "math.e"
    else:
        # All other keys (numbers, operators, parentheses)
        st.session_state.expr += key
    
    # Re-run the app to update the display
    st.rerun() 

# --- DISPLAY ---
st.markdown('<div class="calculator">', unsafe_allow_html=True)
# Display current expression
st.markdown(f'<div class="display">{st.session_state.expr or "0"}</div>', unsafe_allow_html=True)
# Display result
st.markdown(f'<div class="result-display">{st.session_state.result}</div>', unsafe_allow_html=True)

# --- BUTTON GRID CONFIGURATION ---
buttons = [
    ["AC", "C", "^", "%", "abs("],
    ["7", "8", "9", "÷", "math.sin("],
    ["4", "5", "6", "×", "math.cos("],
    ["1", "2", "3", "−", "math.tan("],
    ["0", ".", "(", ")", "+"],
    ["math.sqrt(", "math.log(", "math.pi", "math.e", "="]
]

# Mapping display symbols to internal string values for evaluation
mapping = {
    "÷": "/", 
    "×": "*", 
    "−": "-", 
    "√": "math.sqrt(", # Not needed since we use math.sqrt( in the list
    "^": "^",
    "math.sin(": "math.sin(",
    "math.cos(": "math.cos(",
    "math.tan(": "math.tan(",
    "math.sqrt(": "math.sqrt(",
    "math.log(": "math.log(",
    "abs(": "abs(",
    "round(": "round(",
    "math.pi": "math.pi",
    "math.e": "math.e",
}

# --- BUTTON GRID GENERATION ---
for row in buttons:
    # Create 5 columns for each row
    cols = st.columns(len(row)) 
    for i, label in enumerate(row):
        # Determine the key to pass to the press function
        # For functions and constants, we use the string that goes into the expression
        key_to_press = mapping.get(label, label)
        
        # Determine the label to show on the button (cleaner version)
        display_label = label.replace("math.", "").replace("(", "").replace("sqrt", "√").replace("log", "log").replace("sin", "sin").replace("cos", "cos").replace("tan", "tan").replace("pi", "π").replace("e", "e")

        with cols[i]:
            if st.button(display_label, use_container_width=True):
                press(key_to_press)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><center><p style='color:#888;'>Casio fx-991EX inspired calculator built with ❤️ using Streamlit</p></center>", unsafe_allow_html=True)
