# AI Tutor Orchestrator

A Gradio-based application to orchestrate a 3-way conversation between a Teacher and two Students using AI models (Ollama and OpenAI).

## 🌟 What to Expect

This application simulates a dynamic classroom environment where three AI agents interact with each other to teach and learn a specific topic.

### The Personas
1.  **👩‍🏫 Professor Maya (Teacher)**:
    *   Leads the lesson based on the chosen topic.
    *   Explains concepts, provides code examples, and answers questions.
    *   Follows a structured teaching progression.
2.  **🐵 Curious George (Student 1)**:
    *   Focuses on the **"Why"**.
    *   Asks conceptual questions to understand the theory and purpose behind the code.
3.  **🧑‍💻 Handson Alex (Student 2)**:
    *   Focuses on the **"How"** and **"What If"**.
    *   Learns by doing, suggesting variations to code, and experimenting with edge cases.

### Key Features
*   **Mix & Match Models**: Most testing done by setting up the Teacher with GPT-4o (OpenAI) for high-quality instruction while using local Llama 3.2 models (Ollama) for the students to save costs.
*   **Customizable Personalities**: Edit the system prompts to change how the teacher teaches or how the students behave.
*   **Automatic Logging**: Every conversation is automatically saved to the `results/` folder with full metadata for analysis.

## 🚀 Setup Instructions

### 1. Prerequisites
*   **Python 3.10+** installed.
*   **Ollama** installed (for local models). [Download Ollama](https://ollama.com/download)

### 2. Installation

1.  **Clone/Open the repository**.
2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install .
    # OR
    pip install -r requirements.txt # if you generated one
    # OR manually
    pip install openai python-dotenv requests gradio
    ```

### 3. Configure Models

#### Option A: Use Local Models (Ollama)
1.  Ensure Ollama is running (`ollama serve` in a terminal).
2.  Pull the models you want to use. For the default configuration, run:
    ```bash
    ollama pull llama3.2:latest
    ollama pull llama3.2:1b
    ollama pull gemma2:2b
    ```
    *You can use any model available in the Ollama library.*

#### Option B: Use OpenAI
1.  Get your API Key from [platform.openai.com](https://platform.openai.com).
2.  Create a `.env` file in the root directory (copy `.env.example` if available):
    ```env
    OPENAI_API_KEY=sk-your-api-key-here
    ```
    *Alternatively, you can enter the key directly in the App UI.*

### 4. Run the Application

```bash
python app.py
```

Open your browser to the URL shown (usually `http://127.0.0.1:7860`).

## 📂 Project Structure

*   `app.py`: Main application logic and UI.
*   `results/`: Folder where conversation logs are saved automatically.
*   `pyproject.toml`: Project dependencies.
