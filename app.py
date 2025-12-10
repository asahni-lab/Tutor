import gradio as gr
import os
import json
import time
import requests
from typing import List, Dict, Generator
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DEFAULTS & CONFIGURATION (Synced with main.py)
# ============================================================================

DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"
# Prioritize API Key from .env, fallback to empty string (user must enter it for OpenAI)
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model names
TEACHER_MODEL_DEFAULT = "llama3.2:latest"
STUDENT1_MODEL_DEFAULT = "llama3.2:1b"
STUDENT2_MODEL_DEFAULT = "gemma3:1b"

# Teacher Config
TEACHER_CONFIG_DEFAULT = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 150,
}

# Student 1 Config
STUDENT1_CONFIG_DEFAULT = {
    "temperature": 0.4,
    "top_p": 0.85,
    "max_tokens": 100,
}

# Student 2 Config
STUDENT2_CONFIG_DEFAULT = {
    "temperature": 0.9,
    "top_p": 0.9,
    "max_tokens": 100,
}

# Prompts
TEACHER_PROMPT_DEFAULT = """You are Professor Maya, a Python programming teacher teaching Curious George and Handson Alex.

TEACHING PROGRESSION (follow this order):
1. Start with print("Hello, World!") - explain strings and basic output
2. Then teach variables: name = "Alice", age = 25
3. Then data types: strings, integers, floats, booleans
4. Keep building progressively based on what students understand

TEACHING STYLE:
- Give ONE concrete code example per message
- Ask students to try it or explain what it does
- Wait for their responses before moving to next concept
- Keep responses to 2-3 sentences max
- Build on what students say"""

STUDENT1_PROMPT_DEFAULT = """You are Curious George, a beginner learning Python with Professor Maya and Handson Alex.
You ask "why" questions about concepts. You want to understand the theory and purpose behind the code.
When Professor Maya shows code, ask questions like "Why do we use quotes?" or "What does this do?"
Keep responses brief (2-3 sentences)."""

STUDENT2_PROMPT_DEFAULT = """You are Handson Alex, a beginner learning Python with Professor Maya and Curious George.
You learn by doing. When you see code, you want to try variations or ask what happens if you change it.
When Professor Maya shows code, ask questions like "What if I use numbers?" or share what you tried.
Keep responses brief (2-3 sentences)."""

INITIAL_TOPIC_DEFAULT = "Let's start learning Python from the very beginning. Show us the first thing every programmer learns!"
MAX_TURNS_DEFAULT = 20

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_ollama_models(base_url: str) -> List[str]:
    """Fetch available models from Ollama"""
    try:
        # Try the standard Ollama API endpoint first if the user provided the v1 base url
        api_url = base_url.replace("/v1", "/api/tags")
        if api_url == base_url: # If replacement didn't happen (no /v1), try appending
             api_url = f"{base_url}/api/tags"
             
        response = requests.get(api_url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
    except:
        pass
        
    # Fallback to trying to list via OpenAI client if direct API fails
    try:
        client = OpenAI(base_url=base_url, api_key="ollama")
        models = client.models.list()
        return [m.id for m in models]
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return ["llama3.2:latest", "llama3.2:1b", "gemma:2b"] # Fallbacks

def get_openai_models() -> List[str]:
    """Return a curated list of OpenAI models"""
    return ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini", "gpt-3.5-turbo"]

def update_model_dropdown(source, ollama_url):
    """Update the model dropdown based on the selected source"""
    if source == "OpenAI API":
        models = get_openai_models()
    else:
        models = get_ollama_models(ollama_url)
    
    if not models:
        models = ["Error: No models found"]

    # allow_custom_value=False ensures a standard dropdown which is more robust for scrolling
    return gr.Dropdown(choices=models, value=models[0] if models else None, interactive=True, allow_custom_value=False)

# ============================================================================
# LOGIC
# ============================================================================

def call_llm(model: str, messages: List[Dict[str, str]], config: Dict, source: str, ollama_url: str, api_key: str) -> str:
    """Send a message to the appropriate LLM provider"""
    try:
        if source == "OpenAI API":
            client = OpenAI(api_key=api_key) # Uses default OpenAI URL
        else:
            client = OpenAI(base_url=ollama_url, api_key="ollama")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=config.get("temperature", 0.7),
            top_p=config.get("top_p", 0.9),
            max_tokens=config.get("max_tokens", 150),
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error calling {model} via {source}: {e}]"

def format_conversation_for_prompt(history: List[Dict[str, str]]) -> str:
    """Format conversation history as a readable string for the prompt"""
    if not history:
        return "No conversation yet."
    
    lines = []
    for entry in history:
        name = entry.get("name", "Unknown")
        content = entry.get("content", "")
        lines.append(f"{name}: {content}")
    return "\n\n".join(lines)

def run_conversation_step(
    topic, 
    teacher_source, teacher_model, teacher_temp, teacher_top_p, teacher_prompt,
    student1_source, student1_model, student1_temp, student1_top_p, student1_prompt,
    student2_source, student2_model, student2_temp, student2_top_p, student2_prompt,
    max_turns,
    ollama_url,
    api_key,
    current_messages
):
    """
    Generator function to run the conversation step-by-step.
    Yields the updated list of messages for the Chatbot.
    """
    
    # Define participants
    participants = [
        {
            "name": "Professor Maya", 
            "role": "Teacher",
            "source": teacher_source,
            "model": teacher_model, 
            "prompt": teacher_prompt, 
            "config": {"temperature": teacher_temp, "top_p": teacher_top_p, "max_tokens": 150},
            "avatar": "👩‍🏫" 
        },
        {
            "name": "Curious George", 
            "role": "Student",
            "source": student1_source,
            "model": student1_model, 
            "prompt": student1_prompt, 
            "config": {"temperature": student1_temp, "top_p": student1_top_p, "max_tokens": 100},
            "avatar": "🐵"
        },
        {
            "name": "Handson Alex", 
            "role": "Student",
            "source": student2_source,
            "model": student2_model, 
            "prompt": student2_prompt, 
            "config": {"temperature": student2_temp, "top_p": student2_top_p, "max_tokens": 100},
            "avatar": "🧑‍💻"
        },
    ]
    
    messages = [] 
    conversation_history_internal = []
    
    turn = 0
    while turn < max_turns:
        participant = participants[turn % 3]
        
        # Prepare prompt
        conversation_text = format_conversation_for_prompt(conversation_history_internal)
        
        if not conversation_history_internal:
            user_prompt = f"""You are {participant['name']}.
The topic to discuss is: {topic}

Start the conversation by introducing the topic and asking an opening question."""
        else:
            user_prompt = f"""You are {participant['name']}.

The conversation so far is:
{conversation_text}

Now respond with what you would like to say next, as {participant['name']}. Be natural and conversational."""

        system_prompt = participant["prompt"]
        
        # Call LLM
        response_text = call_llm(
            model=participant["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            config=participant["config"],
            source=participant["source"],
            ollama_url=ollama_url,
            api_key=api_key
        )
        
        # Add to internal history
        conversation_history_internal.append({
            "name": participant["name"],
            "content": response_text
        })
        
        # Add to Chatbot messages
        formatted_content = f"**{participant['name']}** {participant['avatar']}:\n\n{response_text}"
        
        messages.append({
            "role": "assistant",
            "content": formatted_content
        })
        
        yield messages
        
        turn += 1
        time.sleep(0.5) # Small delay for visual pacing

# ============================================================================
# UI LAYOUT
# ============================================================================

with gr.Blocks(title="Multi-Agent Tutor Orchestrator") as demo:
    with gr.Row():
        gr.Markdown("# 🤖 Multi-Agent Tutor Orchestrator")
        gr.Markdown("[📖 Read README](file/README.md)") 

    gr.Markdown("Watch a Teacher and two Students (AI Agents) learn together!")
    
    with gr.Row():
        with gr.Column(scale=2):
            topic_input = gr.Textbox(label="Topic", value=INITIAL_TOPIC_DEFAULT, lines=8)
        with gr.Column(scale=1):
            ollama_url_input = gr.Textbox(label="Ollama URL", value=DEFAULT_OLLAMA_URL)
            api_key_input = gr.Textbox(label="API Key (for OpenAI)", value=DEFAULT_API_KEY, type="password")
            max_turns_input = gr.Slider(label="Max Turns", minimum=1, maximum=50, value=MAX_TURNS_DEFAULT, step=1)

    with gr.Row():
        # Teacher Panel
        with gr.Column(variant="panel"):
            gr.Markdown("### 👩‍🏫 Professor Maya (Teacher)")
            teacher_source = gr.Dropdown(choices=["Ollama", "OpenAI API"], value="Ollama", label="Model Source")
            # allow_custom_value=False to fix scrolling issues
            teacher_model = gr.Dropdown(label="Model", value=TEACHER_MODEL_DEFAULT, choices=[TEACHER_MODEL_DEFAULT], allow_custom_value=False, interactive=True)
            with gr.Row():
                teacher_temp = gr.Slider(label="Temperature", minimum=0.0, maximum=2.0, value=TEACHER_CONFIG_DEFAULT["temperature"], step=0.1)
                teacher_top_p = gr.Slider(label="Top P", minimum=0.0, maximum=1.0, value=TEACHER_CONFIG_DEFAULT["top_p"], step=0.05)
            teacher_prompt = gr.Textbox(label="System Prompt", value=TEACHER_PROMPT_DEFAULT, lines=5)

        # Student 1 Panel
        with gr.Column(variant="panel"):
            gr.Markdown("### 🐵 Curious George (Student 1)")
            student1_source = gr.Dropdown(choices=["Ollama", "OpenAI API"], value="Ollama", label="Model Source")
            student1_model = gr.Dropdown(label="Model", value=STUDENT1_MODEL_DEFAULT, choices=[STUDENT1_MODEL_DEFAULT], allow_custom_value=False, interactive=True)
            with gr.Row():
                student1_temp = gr.Slider(label="Temperature", minimum=0.0, maximum=2.0, value=STUDENT1_CONFIG_DEFAULT["temperature"], step=0.1)
                student1_top_p = gr.Slider(label="Top P", minimum=0.0, maximum=1.0, value=STUDENT1_CONFIG_DEFAULT["top_p"], step=0.05)
            student1_prompt = gr.Textbox(label="System Prompt", value=STUDENT1_PROMPT_DEFAULT, lines=5)

        # Student 2 Panel
        with gr.Column(variant="panel"):
            gr.Markdown("### 🧑‍💻 Handson Alex (Student 2)")
            student2_source = gr.Dropdown(choices=["Ollama", "OpenAI API"], value="Ollama", label="Model Source")
            student2_model = gr.Dropdown(label="Model", value=STUDENT2_MODEL_DEFAULT, choices=[STUDENT2_MODEL_DEFAULT], allow_custom_value=False, interactive=True)
            with gr.Row():
                student2_temp = gr.Slider(label="Temperature", minimum=0.0, maximum=2.0, value=STUDENT2_CONFIG_DEFAULT["temperature"], step=0.1)
                student2_top_p = gr.Slider(label="Top P", minimum=0.0, maximum=1.0, value=STUDENT2_CONFIG_DEFAULT["top_p"], step=0.05)
            student2_prompt = gr.Textbox(label="System Prompt", value=STUDENT2_PROMPT_DEFAULT, lines=5)

    # The Stage
    gr.Markdown("### 🎭 The Stage")
    chatbot = gr.Chatbot(height=600)
    
    with gr.Row():
        start_btn = gr.Button("▶️ Start Conversation", variant="primary")
        clear_btn = gr.Button("🗑️ Clear")

    # Event Handlers
    
    # Update models when source changes
    teacher_source.change(fn=update_model_dropdown, inputs=[teacher_source, ollama_url_input], outputs=teacher_model)
    student1_source.change(fn=update_model_dropdown, inputs=[student1_source, ollama_url_input], outputs=student1_model)
    student2_source.change(fn=update_model_dropdown, inputs=[student2_source, ollama_url_input], outputs=student2_model)

    # Initial load of models
    demo.load(fn=update_model_dropdown, inputs=[teacher_source, ollama_url_input], outputs=teacher_model)
    demo.load(fn=update_model_dropdown, inputs=[student1_source, ollama_url_input], outputs=student1_model)
    demo.load(fn=update_model_dropdown, inputs=[student2_source, ollama_url_input], outputs=student2_model)

    start_btn.click(
        fn=run_conversation_step,
        inputs=[
            topic_input,
            teacher_source, teacher_model, teacher_temp, teacher_top_p, teacher_prompt,
            student1_source, student1_model, student1_temp, student1_top_p, student1_prompt,
            student2_source, student2_model, student2_temp, student2_top_p, student2_prompt,
            max_turns_input,
            ollama_url_input,
            api_key_input,
            chatbot
        ],
        outputs=chatbot
    )
    
    clear_btn.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), allowed_paths=["."])
