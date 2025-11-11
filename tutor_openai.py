"""
Three-way conversation using OpenAI API: Teacher and 2 Students
Learning program with token tracking and cost calculation
"""

import json
import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION - OpenAI Models
# ============================================================================

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# OpenAI Models - Using different models for different roles
TEACHER_MODEL = "gpt-4o"           # Most advanced - Best for teaching code
STUDENT1_MODEL = "o1-mini"         # Reasoning model - For thoughtful questions
STUDENT2_MODEL = "gpt-4o-mini"     # Mini model - Fast and economical

# Model pricing (per 1M tokens) - Updated as of Nov 2024
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},           # $2.50 / $10.00 per 1M tokens
    "o1-mini": {"input": 3.00, "output": 12.00},          # $3.00 / $12.00 per 1M tokens
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},     # $0.15 / $0.60 per 1M tokens
}

# Model parameters
TEACHER_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 150,
}

STUDENT1_CONFIG = {
    "temperature": 0.4,
    "max_tokens": 100,
}

STUDENT2_CONFIG = {
    "temperature": 0.9,
    "max_tokens": 100,
}

# System prompts - same as Ollama version
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
MAX_TURNS = 6  # Limited turns for cost control
INITIAL_TOPIC = "Let's start learning Python from the very beginning. Show us the first thing every programmer learns!"

# ============================================================================
# COST TRACKING
# ============================================================================

class TokenTracker:
    """Track tokens and costs for each interaction"""
    def __init__(self):
        self.interactions = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def add_interaction(self, model: str, input_tokens: int, output_tokens: int):
        """Record token usage for an interaction"""
        pricing = PRICING.get(model, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total = input_cost + output_cost
        
        self.interactions.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total
        })
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total
        
        return total
    
    def print_interaction_cost(self, model: str, speaker: str):
        """Print cost for the last interaction"""
        if self.interactions:
            last = self.interactions[-1]
            print(f"   [Tokens: {last['input_tokens']} in / {last['output_tokens']} out | Cost: ${last['cost']:.6f}]")
    
    def print_summary(self):
        """Print total cost summary"""
        print("\n" + "="*60)
        print("COST SUMMARY")
        print("="*60)
        print(f"Total Input Tokens:  {self.total_input_tokens:,}")
        print(f"Total Output Tokens: {self.total_output_tokens:,}")
        print(f"Total Tokens:        {self.total_input_tokens + self.total_output_tokens:,}")
        print(f"\nTotal Cost:          ${self.total_cost:.6f}")
        print("="*60)

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def call_openai(model: str, messages: List[Dict[str, str]], config: Dict, tracker: TokenTracker) -> str:
    """Send a message to OpenAI and track tokens/cost"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 150),
        )
        
        # Track token usage
        usage = response.usage
        tracker.add_interaction(model, usage.prompt_tokens, usage.completion_tokens)
        
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
                      conversation_history: List[Dict[str, str]], config: Dict, tracker: TokenTracker) -> str:
    """Get next response from a model using the single-prompt pattern"""
    conversation_text = format_conversation(conversation_history)
    
    if not conversation_history:
        user_prompt = f"""You are {speaker_name}.
The topic to discuss is: {INITIAL_TOPIC}

Start the conversation by introducing the topic and asking an opening question."""
    else:
        user_prompt = f"""You are {speaker_name}.

The conversation so far is:
{conversation_text}

Now respond with what you would like to say next, as {speaker_name}. Be natural and conversational."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return call_openai(model, messages, config, tracker)


def run_conversation():
    """Main conversation loop with token tracking"""
    
    # Initialize tracker and conversation history
    tracker = TokenTracker()
    conversation_history = []
    
    # Define participants with their configs
    participants = [
        {"name": "Professor Maya", "model": TEACHER_MODEL, "prompt": TEACHER_PROMPT, "config": TEACHER_CONFIG},
        {"name": "Curious George", "model": STUDENT1_MODEL, "prompt": STUDENT1_PROMPT, "config": STUDENT1_CONFIG},
        {"name": "Handson Alex", "model": STUDENT2_MODEL, "prompt": STUDENT2_PROMPT, "config": STUDENT2_CONFIG},
    ]
    
    # Start the conversation
    print("\n" + "="*60)
    print("THREE-WAY CONVERSATION WITH OPENAI MODELS")
    print("="*60)
    print(f"\nTopic: {INITIAL_TOPIC}")
    print(f"\nModels:")
    print(f"  Professor Maya → {TEACHER_MODEL}")
    print(f"  Curious George → {STUDENT1_MODEL}")
    print(f"  Handson Alex   → {STUDENT2_MODEL}")
    print(f"\nMax turns: {MAX_TURNS}")
    print("\n" + "="*60)
    
    # Simple conversation loop
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
            config=participant["config"],
            tracker=tracker
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
        tracker.print_interaction_cost(participant["model"], participant["name"])
        
        turn += 1
    
    # Print cost summary
    tracker.print_summary()
    
    # Save conversation to file
    print("\n" + "="*60)
    print("SAVING CONVERSATION")
    print("="*60)
    
    with open("conversation_log_openai.json", "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, indent=2, ensure_ascii=False)
    
    print("\nConversation saved to: conversation_log_openai.json")
    print(f"Total exchanges: {len(conversation_history)}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    print("\nStarting OpenAI conversation...")
    print("Make sure your OPENAI_API_KEY is set in .env file")
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-key-here":
        print("\n❌ ERROR: Please add your OpenAI API key to the .env file")
        print("   1. Open .env file")
        print("   2. Replace 'sk-your-key-here' with your actual API key")
        print("   3. Save the file and run again")
        return
    
    try:
        run_conversation()
    except KeyboardInterrupt:
        print("\n\nConversation interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == "__main__":
    main()
