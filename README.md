# Autonomous Code Refactoring Agent

An enterprise-grade, fully local AI-powered refactoring system designed to transform inefficient, syntactically broken, or poorly structured code into optimized, production-ready implementations. This project leverages a local Large Language Model (LLM) via Ollama, ensuring complete offline operation without reliance on cloud services.

The agent specializes in Python code refactoring, focusing on algorithmic improvements, clean code principles, and adherence to industry standards like SOLID principles and Big-O optimization. It incorporates a knowledge base for contextual guidance, reflection loops for error correction, and rigorous validation to guarantee syntactically correct outputs.

---

## 🚀 Overview

This autonomous agent accepts user-submitted code snippets and performs comprehensive refactoring:

- **Syntax Correction**: Fixes broken or invalid code.
- **Algorithmic Optimization**: Reduces time and space complexity (e.g., replacing O(n²) sorts with O(n log n) alternatives).
- **Clean Code Application**: Renames variables descriptively, adds type hints, docstrings, and follows Python idioms.
- **Validation**: Ensures the output is syntactically valid and structurally sound.
- **Reflection and Retry**: Implements a deterministic retry mechanism for failed generations.

Unlike cloud-based tools, this system runs entirely on your local machine, preserving privacy and avoiding API costs.

---

## 🏗️ Architecture & Methodology

The system employs a modular, reflection-based architecture inspired by AI planning and reinforcement learning principles. It combines deterministic generation with feedback loops to achieve high reliability.

### Core Components

1. **Frontend (Streamlit UI)**: Provides an intuitive interface for code input and output display, including logs and validation status.
2. **AI Agent ([backend/ai_agent.py](backend/ai_agent.py))**: Orchestrates refactoring by querying the knowledge base and prompting the LLM for structured analysis and code generation.
3. **Knowledge Base ([backend/knowledge_base.py](backend/knowledge_base.py))**: Uses ChromaDB with sentence embeddings to retrieve relevant coding standards and rules based on code snippets.
4. **Optimizer ([backend/optimizer.py](backend/optimizer.py))**: Handles code extraction, sanitization, and a reflection loop with up to one retry for optimization tasks.
5. **Validator ([backend/validator.py](backend/validator.py))**: Performs AST-based syntax checking without execution.
6. **Analyzer ([backend/analyzer.py](backend/analyzer.py))**: Computes code metrics like cyclomatic complexity and lines of code (LOC) using Lizard.
7. **Refactorer ([backend/refactorer.py](backend/refactorer.py))**: Applies simple refactoring actions like variable renaming or comment removal.

### Methodology

The methodology integrates Retrieval-Augmented Generation (RAG) with reflection loops:

- **Retrieval-Augmented Generation**: Before prompting the LLM, the system retrieves context from a vectorized knowledge base of coding standards (stored in [data/coding_standards.txt](data/coding_standards.txt)). This ensures outputs align with best practices.
- **Structured Prompting**: Prompts are engineered to elicit specific sections (analysis, algorithm, complexity, code) for consistent, parseable responses.
- **Reflection Loop**: If initial generation fails validation, a deterministic retry is triggered with error feedback, minimizing hallucinations.
- **Heuristic Scoring**: Post-generation, metrics are calculated to quantify improvements (e.g., complexity reduction).

---

## 🔄 Process Flow

The refactoring process follows a deterministic pipeline:

1. **Input Reception**: User submits code via the Streamlit UI in [app.py](app.py).
2. **Context Retrieval**: [`get_refactoring_context`](backend/knowledge_base.py) queries the ChromaDB collection for relevant rules (e.g., SOLID principles, Big-O optimizations).
3. **AI Generation**: [`ai_refactor_code`](backend/ai_agent.py) prompts DeepSeek-Coder to produce structured output, including analysis, optimal algorithm, before/after complexity, and refactored code.
4. **Parsing and Extraction**: [`parse_structured_output`](backend/ai_agent.py) extracts sections; [`extract_python_code`](backend/optimizer.py) isolates code blocks.
5. **Sanitization**: [`sanitize_unicode`](backend/optimizer.py) replaces problematic characters.
6. **Validation**: [`check_syntax`](backend/validator.py) uses AST to verify correctness.
7. **Reflection Retry**: If invalid, [`reflection_loop`](backend/optimizer.py) performs one retry with error details.
8. **Metrics Analysis**: [`get_metrics`](backend/analyzer.py) computes complexity and LOC for feedback.
9. **Output Display**: Results, logs, and status are shown in the UI, with optional simple refactorings via [backend/refactorer.py](backend/refactorer.py).

This process ensures a single-pass success rate with fallback retries, balancing efficiency and accuracy.

---

## 🛠️ Technologies Used

### 1. Streamlit
- Builds the interactive web UI.
- Handles code input, output display, and real-time logs.

### 2. Ollama
- Manages local LLM execution.
- Model: `deepseek-coder:latest` (code-specialized, offline after download).
- Handles prompt-response cycles for generation and retries.

### 3. DeepSeek-Coder (Local LLM)
- Core AI model for code refactoring.
- Performs algorithmic improvements, variable renaming, and clean code transformations.
- Configured with low temperature (0.2) for deterministic outputs.

### 4. ChromaDB
- Vector database for storing and querying coding standards.
- Uses SentenceTransformer embeddings (`all-MiniLM-L6-v2`) for semantic search.
- Populated from [data/coding_standards.txt](data/coding_standards.txt).

### 5. AST (Abstract Syntax Tree)
- Python's built-in module for syntax validation.
- Checks code without execution: `ast.parse(code)`.

### 6. Lizard
- Code analysis library for computing metrics like cyclomatic complexity and LOC.

### 7. Other Dependencies
- See [requirements.txt](requirements.txt) for Python packages (e.g., chromadb, sentence-transformers, ollama).
- [packages.txt](packages.txt) lists system dependencies (e.g., default-jdk).

---

## 📦 Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/auto-refactor-agent.git
   cd auto-refactor-agent
