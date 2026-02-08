import streamlit as st
from backend.optimizer import hill_climbing_search
from backend.analyzer import get_metrics

# Page Config
st.set_page_config(page_title="Auto-Refactor Agent", layout="wide")

# Title and Abstract
st.title("🤖 Auto-Refactor: AI Code Optimization Agent")
st.markdown("""
**Abstract:** This system treats code refactoring as a State-Space Search problem. 
It uses **Hill Climbing** algorithms to minimize Cyclomatic Complexity.
""")

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Java Code")
    code_input = st.text_area("Paste your code here:", height=400, value="""
public class Test {
    // This is a messy function
    public void main(String args[]) {
        int x = 0; // x is a bad name
        if (x == 0) {
            System.out.println("Hello");
        }
    }
}
""")
    
    if st.button("Optimize Code 🚀"):
        with st.spinner("Agent is analyzing AST and searching for optimizations..."):
            # Run the AI
            optimized_code, logs, final_metrics = hill_climbing_search(code_input)
            
            # Store results in session state to display in col2
            st.session_state['opt_code'] = optimized_code
            st.session_state['logs'] = logs
            st.session_state['metrics'] = final_metrics

# Output Section
with col2:
    st.subheader("Refactored Code")
    if 'opt_code' in st.session_state:
        st.code(st.session_state['opt_code'], language='java')
        
        st.subheader("Change Log (Planner Output)")
        for log in st.session_state['logs']:
            st.success(log)
            
        st.metric(label="Final Cyclomatic Complexity", value=st.session_state['metrics']['complexity'])