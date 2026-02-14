# 🧠 Autonomous Multi-Language Refactoring Agent

An enterprise-grade, locally hosted AI agent designed to autonomously analyze, refactor, and optimize code. Unlike standard LLM wrappers, this project utilizes an **Actor-Critic Reflection Architecture** and **Retrieval-Augmented Generation (RAG)** to guarantee code structural integrity and enforce strict coding standards without relying on external cloud APIs.

## ✨ Key Features

* **100% Local Inference:** Powered by `Ollama` and `DeepSeek-Coder`. Zero data leaves your machine, ensuring complete privacy for proprietary code.
* **Retrieval-Augmented Generation (RAG):** Uses `ChromaDB` and `SentenceTransformers` to ground the LLM's outputs in strict, customizable coding standards (SOLID principles, Big-O optimization).
* **Actor-Critic Reflection Loop:** The agent doesn't just guess; it compiles. If the generated code contains syntax errors, the Validator (Critic) feeds the exact compiler error back to the LLM (Actor) for autonomous self-correction.
* **Multi-Language Support:** Natively validates and refactors **Python, Java, C, and C++** using language-specific ASTs and compilers.

## ⚙️ System Architecture

1. **Input:** User submits messy, unoptimized code via the `Streamlit` UI.
2. **Retrieval (RAG):** `ChromaDB` vectorizes the input and retrieves the most mathematically relevant coding rules from the local knowledge base.
3. **Generation (Actor):** The local LLM generates optimized code formatted as strict JSON.
4. **Validation (Critic):** The backend intercepts the JSON and validates the code using `ast.parse` (Python), `gcc/g++ -fsyntax-only` (C/C++), or `javac` (Java).
5. **Reflection Loop:** If validation fails, the error is injected into a new prompt, and the LLM iteratively fixes its own mistakes until the code compiles perfectly.

## 🛠️ Prerequisites

Ensure you have the following installed on your system:
* **Python 3.8+**
* **Ollama:** [Download Here](https://ollama.com/)
* **Compilers:** `gcc`/`g++` (for C/C++) and `javac` (for Java) installed and added to your system PATH.

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/Vdv26/Auto-Refactor-Agent.git](https://github.com/Vdv26/Auto-Refactor-Agent.git)
cd Auto-Refactor-Agent