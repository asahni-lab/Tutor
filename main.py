"""
Three-way conversation between Ollama models: Teacher and 2 Students
A simple, self-contained program for learning about multi-model conversations
"""

import json
from typing import List, Dict
from openai import OpenAI

# ============================================================================
# CONFIGURATION - Edit these to match your Ollama models
# ============================================================================

# Initialize OpenAI client pointing to Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama's OpenAI-compatible endpoint
    api_key="ollama"  # Required but unused by Ollama
)

# Model names - using your available Ollama models
TEACHER_MODEL = "llama3.2:latest"      # 3.2B - Biggest model (Teacher)
STUDENT1_MODEL = "llama3.2:1b"         # 1.2B - Medium model (Student 1)
STUDENT2_MODEL = "gemma3:1b"           # 1B - Smallest model (Student 2)

# Model parameters - play with these to change behavior!
# Temperature: 0.0 = very focused/deterministic, 2.0 = very creative/random
# Top_p: 0.1 = conservative, 1.0 = full vocabulary range
# Top_k: lower = more focused, higher = more diverse

TEACHER_CONFIG = {
    "temperature": 0.7,    # Balanced - not too rigid, not too creative
    "top_p": 0.9,          # Allow most vocabulary
    "top_k": 40,           # Moderate diversity
    "max_tokens": 150,     # Limit response length
}

STUDENT1_CONFIG = {
    "temperature": 0.4,    # Slightly more creative for curious questions
    "top_p": 0.85,         # Good vocabulary range
    "top_k": 50,           # More diverse responses
    "max_tokens": 100,     # Shorter student responses
}

STUDENT2_CONFIG = {
    "temperature": 0.9,    # Most creative - likes to experiment
    "top_p": 0.9,          # Full range
    "top_k": 60,           # High diversity
    "max_tokens": 100,     # Shorter student responses
}

DECISION_CONFIG = {
    "temperature": 0.3,    # Low temp for yes/no decisions (more deterministic)
    "top_p": 0.8,
    "top_k": 20,
    "max_tokens": 10,      # Just need YES or NO
}

# System prompts define each model's personality and role
TEACHER_PROMPT = """You are Professor Maya, a Python programming teacher teaching Curious George and Handson Alex.

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

STUDENT1_PROMPT = """You are Curious George, a beginner learning Python with Professor Maya and Handson Alex.
You ask "why" questions about concepts. You want to understand the theory and purpose behind the code.
When Professor Maya shows code, ask questions like "Why do we use quotes?" or "What does this do?"
Keep responses brief (2-3 sentences)."""

STUDENT2_PROMPT = """You are Handson Alex, a beginner learning Python with Professor Maya and Curious George.
You learn by doing. When you see code, you want to try variations or ask what happens if you change it.
When Professor Maya shows code, ask questions like "What if I use numbers?" or share what you tried.
Keep responses brief (2-3 sentences)."""

# Conversation settings
MAX_TURNS = 20  # Total number of exchanges (increased for proper lesson flow)
INITIAL_TOPIC = "Let's start learning Python from the very beginning. Show us the first thing every programmer learns!"

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def call_ollama(model: str, messages: List[Dict[str, str]], config: Dict = None) -> str:
    """Send a message to Ollama using OpenAI library with configurable parameters"""
    if config is None:
        config = {"temperature": 0.7}  # Default fallback
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=config.get("temperature", 0.7),
            top_p=config.get("top_p", 0.9),
            max_tokens=config.get("max_tokens", 150),
            # Note: top_k not available in OpenAI API format, but some Ollama versions support it
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error calling {model}: {e}]"



def format_conversation(history: List[Dict[str, str]]) -> str:
    """Format conversation history as a readable string"""
    if not history:
        return "No conversation yet."
    
    lines = []
    for entry in history:
        lines.append(f"{entry['speaker']}: {entry['message']}")
    return "\n\n".join(lines)


def get_next_response(model: str, system_prompt: str, speaker_name: str, 
                      conversation_history: List[Dict[str, str]], config: Dict = None) -> str:
    """
    Get next response from a model using the reliable single-prompt pattern.
    System prompt defines who they are, user prompt contains full conversation.
    """
    conversation_text = format_conversation(conversation_history)
    
    if not conversation_history:
        # First message - teacher starts the topic
        user_prompt = f"""You are {speaker_name}.
The topic to discuss is: {INITIAL_TOPIC}

Start the conversation by introducing the topic and asking an opening question."""
    else:
        # Subsequent messages - include full conversation context
        user_prompt = f"""You are {speaker_name}.

The conversation so far is:
{conversation_text}

Now respond with what you would like to say next, as {speaker_name}. Be natural and conversational."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return call_ollama(model, messages, config)


def run_conversation():
    """Main conversation loop - simple sequential turn-taking"""
    
    # Initialize conversation history (shared context stored here)
    conversation_history = []
    
    # Define participants with their configs
    participants = [
        {"name": "Professor Maya", "model": TEACHER_MODEL, "prompt": TEACHER_PROMPT, "config": TEACHER_CONFIG},
        {"name": "Curious George", "model": STUDENT1_MODEL, "prompt": STUDENT1_PROMPT, "config": STUDENT1_CONFIG},
        {"name": "Handson Alex", "model": STUDENT2_MODEL, "prompt": STUDENT2_PROMPT, "config": STUDENT2_CONFIG},
    ]
    
    # Start the conversation
    print("\n" + "="*60)
    print("THREE-WAY CONVERSATION: PROFESSOR MAYA, CURIOUS GEORGE & HANDSON ALEX")
    print("="*60)
    print(f"\nTopic: {INITIAL_TOPIC}")
    print(f"Models: Professor Maya={TEACHER_MODEL}, Curious George={STUDENT1_MODEL}, Handson Alex={STUDENT2_MODEL}")
    print(f"Max turns: {MAX_TURNS}")
    print("\n" + "="*60)
    
    # Simple conversation loop - everyone takes turns in order
    turn = 0
    while turn < MAX_TURNS:
        # Who speaks this turn? Rotate through: 0, 1, 2, 0, 1, 2...
        participant = participants[turn % 3]
        
        print(f"\n[{participant['name']} is speaking...]")
        
        # Get their response
        response = get_next_response(
            model=participant["model"],
            system_prompt=participant["prompt"],
            speaker_name=participant["name"],
            conversation_history=conversation_history,
            config=participant["config"]
        )
        
        # Add to shared conversation history
        conversation_history.append({
            "speaker": participant["name"],
            "message": response
        })
        
        # Display
        print(f"\n{'='*60}")
        print(f"{participant['name'].upper()}:")
        print(f"{'-'*60}")
        print(response)
        
        turn += 1
    
    # Save conversation to file
    print("\n" + "="*60)
    print("CONVERSATION COMPLETE")
    print("="*60)
    
    with open("conversation_log.json", "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, indent=2, ensure_ascii=False)
    
    print("\nConversation saved to: conversation_log.json")
    print(f"Total exchanges: {len(conversation_history)}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    print("\nStarting Ollama conversation...")
    print("Make sure Ollama is running (ollama serve)")
    
    try:
        run_conversation()
    except KeyboardInterrupt:
        print("\n\nConversation interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == "__main__":
    main()
