import streamlit as st
from backend.optimizer import reflection_loop
from backend.validator import check_syntax

st.set_page_config(page_title="AI Code Cleaner", layout="wide")

st.title("🧠 Autonomous Multi-Language Refactoring Agent")
st.info("Powered by Local DeepSeek-Coder with Reflection Architecture")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Bad Code")
    language = st.selectbox("Select Language:", ["Python", "Java", "C", "C++"])
    
    # Dynamic default code based on selection
    default_code = ""
    if language == "Python":
        default_code = "def sort(arr):\n    # bad bubble sort\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]"
    elif language == "Java":
        default_code = "public class Messy {\n    public void sort(int[] arr) {\n        // Bad Bubble Sort - O(n^2)\n        for (int i = 0; i < arr.length-1; i++)\n            for (int j = 0; j < arr.length-i-1; j++)\n                if (arr[j] > arr[j+1]) {\n                    int temp = arr[j];\n                    arr[j] = arr[j+1];\n                    arr[j+1] = temp;\n                }\n    }\n}"
    else:
        default_code = "// Paste your C/C++ code here"

    code_input = st.text_area("Source Code:", height=400, value=default_code)
    
    if st.button("✨ Auto-Repair & Optimize"):
        with st.spinner("Agent is analyzing and validating..."):
            
            # Execute the reflection loop
            optimized_code, status, logs = reflection_loop(code_input, language)
            
            st.session_state['result_code'] = optimized_code
            st.session_state['status'] = status
            st.session_state['logs'] = logs
            st.session_state['lang_choice'] = language.lower()

with col2:
    st.subheader("Agent Output")
    
    if 'logs' in st.session_state:
        # I set expanded=True so it stays open for debugging
        with st.expander("🕵️ Agent Thought Process & Reflection Logs", expanded=True):
            for log in st.session_state['logs']:
                st.write(log)
                
    # ALWAYS show the status message, so we can see what went wrong
    if 'status' in st.session_state:
        if "Success" in st.session_state['status']:
            st.success("Validation Passed! Code is structurally sound.")
        else:
            st.error(f"Agent Status: {st.session_state['status']}")
            
    if 'result_code' in st.session_state and st.session_state['result_code']:
        st.code(st.session_state['result_code'], language=st.session_state['lang_choice'])