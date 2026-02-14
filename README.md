#  Autonomous Code Refactoring Agent

An enterprise-style, fully local AI-powered refactoring system that analyzes inefficient or syntactically broken code and automatically generates an optimized, production-ready version.

This project runs completely offline using a local Large Language Model (LLM) via Ollama.

---

## 🚀 Overview

This agent accepts inefficient or broken code and:

- Fixes syntax errors
- Improves time complexity
- Improves space efficiency
- Applies clean code principles
- Returns a fully optimized implementation
- Validates syntax automatically

Unlike cloud-based solutions, this system runs entirely on your local machine.

---

##  Architecture 

The system uses a deterministic single-pass generation pipeline:

1. User submits bad code.
2. Local LLM (DeepSeek-Coder via Ollama) generates optimized code.
3. The backend extracts only the code.
4. Unicode characters are sanitized.
5. AST validation checks for syntax correctness.
6. If invalid → one deterministic retry is performed.
7. Final optimized code is returned to the user.



---

##  Technologies Used

### 1️ Streamlit
Used to build the interactive web UI.

- Code input panel
- Agent output display
- Logs and validation status

---

### 2️⃣ Ollama
Runs the local LLM.

- Model: `deepseek-coder`
- Fully offline after initial download
- Handles code generation

---

### 3️⃣ DeepSeek-Coder (Local LLM)
A code-specialized language model used for:

- Algorithm improvement
- Refactoring
- Clean code transformation
- Complexity optimization

---

### 4️⃣ AST (Abstract Syntax Tree)
Used for syntax validation without executing the code.

```python
ast.parse(code)
