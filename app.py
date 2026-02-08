import streamlit as st
from backend.ai_agent import ai_refactor_code
from backend.validator import check_java_syntax

st.set_page_config(page_title="AI Code Cleaner", layout="wide")

st.title("🧠 GenAI Code Refactoring Agent")
st.info("Powered by Local LLM (DeepSeek-Coder) - No Data Leaves Your PC")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Bad Code")
    code_input = st.text_area("Paste Java Code:", height=400, value="""
public class MessyProcessor {
    public void sort(int[] arr) {
        int n = arr.length;
        // Bad Bubble Sort - O(n^2)
        for (int i = 0; i < n-1; i++)
            for (int j = 0; j < n-i-1; j++)
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
    }
}
""")
    
    if st.button("✨ Auto-Repair & Optimize"):
        with st.spinner("AI is thinking... (This depends on your GPU speed)"):
            # 1. GENERATE
            optimized_code = ai_refactor_code(code_input)
            
            # 2. VALIDATE
            is_valid, msg = check_java_syntax(optimized_code)
            
            st.session_state['result_code'] = optimized_code
            st.session_state['validation_msg'] = msg

with col2:
    st.subheader("AI Optimized Result")
    if 'result_code' in st.session_state:
        st.code(st.session_state['result_code'], language='java')
        
        # Validation Badge
        if "Valid" in st.session_state['validation_msg']:
            st.success(st.session_state['validation_msg'])
        else:
            st.error(st.session_state['validation_msg'])