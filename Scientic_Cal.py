import streamlit as st
import math

# Initialize session state for the expression and result
if 'expression' not in st.session_state:
    st.session_state.expression = ""
if 'result' not in st.session_state:
    st.session_state.result = ""

st.title("🔢 Scientific Calculator (Streamlit/Python)")
st.caption("Inspired by Casio fx-991")

# --- Display (Casio-like Screen) ---
# Display the current expression being typed
st.text_input(
    "Expression", 
    value=st.session_state.expression, 
    key="exp_input", 
    disabled=True,
    label_visibility="collapsed"
)
# Display the final result
st.markdown(f"## **Result:** {st.session_state.result}")

# --- Calculation Logic ---
def calculate_expression():
    """Evaluates the mathematical expression entered."""
    try:
        # NOTE: Using eval() is a security risk for production apps.
        # For a basic scientific calculator prototype, you can use it 
        # but a production-ready version needs safer parsing (e.g., sympy or custom parser).
        
        # Replace common function names with their math equivalent
        exp_to_eval = st.session_state.expression.replace('^', '**').replace('log(', 'math.log10(').replace('ln(', 'math.log(').replace('sin(', 'math.sin(math.radians(') # Simple example
        
        final_result = str(eval(exp_to_eval, {"__builtins__": {}}, {"math": math}))
        st.session_state.result = final_result
        st.session_state.expression = final_result # Start new calculation with result
    except Exception as e:
        st.session_state.result = "Error"
        st.session_state.expression = ""

def append_to_expression(symbol):
    """Appends a symbol to the current expression."""
    if st.session_state.result in ["Error", ""]:
        st.session_state.result = "" # Clear previous error/result
    st.session_state.expression += str(symbol)

def clear_all():
    """Clears the entire calculation."""
    st.session_state.expression = ""
    st.session_state.result = ""

# --- Button Layout (Simplified Grid) ---
st.markdown("---")

cols = st.columns(5) # 5 columns for a calculator grid

# Row 1: Clear, Sin, Cos, Tan, Pi
cols[0].button("AC", on_click=clear_all, use_container_width=True)
cols[1].button("sin", on_click=append_to_expression, args=("sin(",), use_container_width=True)
cols[2].button("cos", on_click=append_to_expression, args=("cos(",), use_container_width=True)
cols[3].button("tan", on_click=append_to_expression, args=("tan(",), use_container_width=True)
cols[4].button("π", on_click=append_to_expression, args=(f"math.pi",), use_container_width=True)

# Row 2: 7, 8, 9, /, Log
cols = st.columns(5)
cols[0].button("7", on_click=append_to_expression, args=("7",), use_container_width=True)
cols[1].button("8", on_click=append_to_expression, args=("8",), use_container_width=True)
cols[2].button("9", on_click=append_to_expression, args=("9",), use_container_width=True)
cols[3].button("/", on_click=append_to_expression, args=("/",), use_container_width=True)
cols[4].button("log", on_click=append_to_expression, args=("log(",), use_container_width=True)

# ... continue with more rows for other numbers and operators ...

# Final Row: 0, ., =
cols = st.columns(5)
cols[0].button("0", on_click=append_to_expression, args=("0",), use_container_width=True)
cols[1].button(".", on_click=append_to_expression, args=(".",), use_container_width=True)
cols[2].button("=", on_click=calculate_expression, use_container_width=True)
