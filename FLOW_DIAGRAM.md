# Program Flow Diagram

## Overview: Three-Way AI Conversation System

```
┌─────────────────────────────────────────────────────────────────┐
│                         PROGRAM START                            │
│                         main()                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INITIALIZATION PHASE                          │
│                                                                  │
│  1. Load Configuration Constants:                               │
│     • TEACHER_MODEL = "llama3.2:latest"                         │
│     • STUDENT1_MODEL = "llama3.2:1b"                            │
│     • STUDENT2_MODEL = "gemma3:1b"                              │
│                                                                  │
│  2. Load Model Configs (temperature, top_p, max_tokens):        │
│     • TEACHER_CONFIG = {temp: 0.7, max_tokens: 150}            │
│     • STUDENT1_CONFIG = {temp: 0.4, max_tokens: 100}           │
│     • STUDENT2_CONFIG = {temp: 0.9, max_tokens: 100}           │
│                                                                  │
│  3. Load System Prompts (personality definitions):              │
│     • TEACHER_PROMPT = "You are Professor Maya..."             │
│     • STUDENT1_PROMPT = "You are Curious George..."            │
│     • STUDENT2_PROMPT = "You are Handson Alex..."              │
│                                                                  │
│  4. Initialize OpenAI Client:                                   │
│     • client → points to http://localhost:11434/v1             │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   run_conversation()                             │
│                   SETUP PHASE                                    │
│                                                                  │
│  Create empty conversation_history = []                         │
│     ↓                                                            │
│  This will store: [{speaker: "name", message: "text"}, ...]     │
│                                                                  │
│  Create participants list:                                      │
│     participants = [                                            │
│       {                                                          │
│         name: "Professor Maya",                                 │
│         model: "llama3.2:latest",                               │
│         prompt: TEACHER_PROMPT,                                 │
│         config: TEACHER_CONFIG                                  │
│       },                                                         │
│       {                                                          │
│         name: "Curious George",                                 │
│         model: "llama3.2:1b",                                   │
│         prompt: STUDENT1_PROMPT,                                │
│         config: STUDENT1_CONFIG                                 │
│       },                                                         │
│       {                                                          │
│         name: "Handson Alex",                                   │
│         model: "gemma3:1b",                                     │
│         prompt: STUDENT2_PROMPT,                                │
│         config: STUDENT2_CONFIG                                 │
│       }                                                          │
│     ]                                                            │
│                                                                  │
│  Initialize loop variables:                                     │
│     • turn = 0                                                  │
│     • MAX_TURNS = 20                                            │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN CONVERSATION LOOP                        │
│                    while turn < MAX_TURNS:                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 1: Determine Who Speaks                           │    │
│  │                                                         │    │
│  │   participant = participants[turn % 3]                 │    │
│  │                                                         │    │
│  │   Turn Rotation:                                       │    │
│  │   • turn=0  → 0%3=0 → Professor Maya                  │    │
│  │   • turn=1  → 1%3=1 → Curious George                  │    │
│  │   • turn=2  → 2%3=2 → Handson Alex                    │    │
│  │   • turn=3  → 3%3=0 → Professor Maya (repeats)        │    │
│  │   • turn=4  → 4%3=1 → Curious George                  │    │
│  │   • ...and so on                                       │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 2: Get Response from Selected Participant        │    │
│  │         get_next_response()                            │    │
│  │                                                         │    │
│  │   Input Parameters:                                    │    │
│  │   • model = participant["model"]                       │    │
│  │   • system_prompt = participant["prompt"]              │    │
│  │   • speaker_name = participant["name"]                 │    │
│  │   • conversation_history = [all previous messages]     │    │
│  │   • config = participant["config"]                     │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 2a: Format Conversation History                  │    │
│  │          format_conversation()                         │    │
│  │                                                         │    │
│  │   Takes: conversation_history list                     │    │
│  │   Returns: Formatted string                            │    │
│  │                                                         │    │
│  │   Example Output:                                      │    │
│  │   "Professor Maya: Let's learn print()                │    │
│  │                                                         │    │
│  │    Curious George: Why do we use quotes?              │    │
│  │                                                         │    │
│  │    Handson Alex: What if I try numbers?"              │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 2b: Build Prompt for Current Speaker             │    │
│  │                                                         │    │
│  │   If first turn (no history):                          │    │
│  │     user_prompt = "You are {speaker_name}.             │    │
│  │                   Topic: {INITIAL_TOPIC}               │    │
│  │                   Start the conversation..."           │    │
│  │                                                         │    │
│  │   If subsequent turns:                                 │    │
│  │     user_prompt = "You are {speaker_name}.             │    │
│  │                   Conversation so far:                 │    │
│  │                   {formatted_history}                  │    │
│  │                   Now respond as {speaker_name}"       │    │
│  │                                                         │    │
│  │   Build messages array:                                │    │
│  │   messages = [                                         │    │
│  │     {role: "system", content: system_prompt},          │    │
│  │     {role: "user", content: user_prompt}               │    │
│  │   ]                                                     │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 2c: Call Ollama API                              │    │
│  │          call_ollama()                                 │    │
│  │                                                         │    │
│  │   API Request:                                         │    │
│  │   • Endpoint: http://localhost:11434/v1/chat          │    │
│  │   • Model: participant's model name                    │    │
│  │   • Messages: [system_prompt, user_prompt]             │    │
│  │   • Config: {temperature, top_p, max_tokens}           │    │
│  │                                                         │    │
│  │   ┌──────────────────────────────────────┐             │    │
│  │   │   OLLAMA SERVER PROCESSES REQUEST    │             │    │
│  │   │   - Loads specified model            │             │    │
│  │   │   - Applies temperature/top_p        │             │    │
│  │   │   - Generates response               │             │    │
│  │   └──────────────────────────────────────┘             │    │
│  │                                                         │    │
│  │   Returns: response text string                        │    │
│  │   Example: "Great question! The print() function..."   │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 3: Store Response in Conversation History        │    │
│  │                                                         │    │
│  │   conversation_history.append({                        │    │
│  │     "speaker": participant["name"],                    │    │
│  │     "message": response                                │    │
│  │   })                                                    │    │
│  │                                                         │    │
│  │   Now conversation_history has grown by 1 entry        │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 4: Display Response to User                      │    │
│  │                                                         │    │
│  │   print("="*60)                                        │    │
│  │   print(participant["name"].upper())                   │    │
│  │   print("-"*60)                                        │    │
│  │   print(response)                                      │    │
│  │                                                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ STEP 5: Increment Turn Counter                        │    │
│  │                                                         │    │
│  │   turn += 1                                            │    │
│  │                                                         │    │
│  │   Loop back to STEP 1 if turn < MAX_TURNS             │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONVERSATION COMPLETE                         │
│                                                                  │
│  Save to File:                                                  │
│    conversation_log.json = [                                    │
│      {speaker: "Professor Maya", message: "..."},               │
│      {speaker: "Curious George", message: "..."},               │
│      {speaker: "Handson Alex", message: "..."},                 │
│      ... (all 20 turns saved)                                   │
│    ]                                                             │
│                                                                  │
│  Print Statistics:                                              │
│    • Total exchanges: len(conversation_history)                 │
│    • File saved: conversation_log.json                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Variables & Their Journey

### 1. **Configuration Variables (Static - Set at Program Start)**

```
TEACHER_MODEL, STUDENT1_MODEL, STUDENT2_MODEL
├─> Define which Ollama models to use
└─> Never change during execution

TEACHER_CONFIG, STUDENT1_CONFIG, STUDENT2_CONFIG
├─> Control model behavior (temperature, tokens, etc.)
└─> Never change during execution

TEACHER_PROMPT, STUDENT1_PROMPT, STUDENT2_PROMPT
├─> Define each participant's personality and role
└─> Never change during execution

MAX_TURNS = 20
├─> Controls how long conversation runs
└─> Never changes during execution

INITIAL_TOPIC
├─> Starting question for the conversation
└─> Used only in first turn
```

### 2. **Dynamic Variables (Change During Execution)**

```
conversation_history = []
├─> START: Empty list
├─> AFTER TURN 1: [{speaker: "Professor Maya", message: "..."}]
├─> AFTER TURN 2: [{...Maya...}, {speaker: "Curious George", message: "..."}]
├─> AFTER TURN 3: [{...Maya...}, {...George...}, {speaker: "Handson Alex", message: "..."}]
├─> GROWS by 1 entry each turn
└─> FINAL: 20 entries (one per turn)

turn = 0
├─> START: 0
├─> INCREMENTS: 0 → 1 → 2 → 3 → ... → 19
└─> Controls loop and determines who speaks (turn % 3)

participant
├─> CHANGES every turn via: participants[turn % 3]
├─> TURN 0: {name: "Professor Maya", model: "llama3.2:latest", ...}
├─> TURN 1: {name: "Curious George", model: "llama3.2:1b", ...}
├─> TURN 2: {name: "Handson Alex", model: "gemma3:1b", ...}
└─> TURN 3: Back to Professor Maya (cycles)

response
├─> TEMPORARY: Generated fresh each turn
├─> Contains the text returned from Ollama
└─> Gets appended to conversation_history
```

### 3. **Function Flow Variables**

```
get_next_response() receives:
├─> model: String (e.g., "llama3.2:latest")
├─> system_prompt: String (personality definition)
├─> speaker_name: String (e.g., "Professor Maya")
├─> conversation_history: List (all previous messages)
└─> config: Dict (temperature, max_tokens, etc.)

format_conversation() receives:
├─> conversation_history: List of dicts
└─> Returns: Single formatted string

call_ollama() receives:
├─> model: String
├─> messages: List of {role, content} dicts
├─> config: Dict
└─> Returns: Response text string
```

---

## Data Flow Example (First 3 Turns)

### Turn 0: Professor Maya Speaks

```
INPUT:
  turn = 0
  participant = participants[0] = Professor Maya
  conversation_history = []
  
PROCESSING:
  1. format_conversation([]) → "No conversation yet."
  2. Build user_prompt with INITIAL_TOPIC
  3. messages = [
       {role: "system", content: "You are Professor Maya..."},
       {role: "user", content: "Topic: Let's start learning Python..."}
     ]
  4. call_ollama("llama3.2:latest", messages, TEACHER_CONFIG)
  5. Ollama returns: "Hello class! Let's begin with print('Hello, World!'). Can you tell me what this code might do?"

OUTPUT:
  conversation_history = [
    {speaker: "Professor Maya", message: "Hello class! Let's begin..."}
  ]
  turn = 1
```

### Turn 1: Curious George Speaks

```
INPUT:
  turn = 1
  participant = participants[1] = Curious George
  conversation_history = [{...Maya's message...}]
  
PROCESSING:
  1. format_conversation(history) → "Professor Maya: Hello class! Let's begin..."
  2. Build user_prompt with formatted history
  3. messages = [
       {role: "system", content: "You are Curious George..."},
       {role: "user", content: "Conversation so far: Professor Maya: Hello class!..."}
     ]
  4. call_ollama("llama3.2:1b", messages, STUDENT1_CONFIG)
  5. Ollama returns: "Why do we need the quotes around Hello, World? What happens without them?"

OUTPUT:
  conversation_history = [
    {speaker: "Professor Maya", message: "Hello class!..."},
    {speaker: "Curious George", message: "Why do we need quotes..."}
  ]
  turn = 2
```

### Turn 2: Handson Alex Speaks

```
INPUT:
  turn = 2
  participant = participants[2] = Handson Alex
  conversation_history = [{...Maya...}, {...George...}]
  
PROCESSING:
  1. format_conversation(history) → "Professor Maya: ...\n\nCurious George: ..."
  2. Build user_prompt with full formatted history
  3. messages = [
       {role: "system", content: "You are Handson Alex..."},
       {role: "user", content: "Conversation so far: [both previous messages]"}
     ]
  4. call_ollama("gemma3:1b", messages, STUDENT2_CONFIG)
  5. Ollama returns: "Can I try print(12345) without quotes? I want to see what happens with numbers!"

OUTPUT:
  conversation_history = [
    {speaker: "Professor Maya", message: "..."},
    {speaker: "Curious George", message: "..."},
    {speaker: "Handson Alex", message: "Can I try print(12345)..."}
  ]
  turn = 3
```

**Pattern repeats** with turn % 3 cycling through participants until turn reaches MAX_TURNS (20).

---

## Critical Insights

1. **Shared Context**: All participants see the FULL conversation history each turn, creating coherent dialogue.

2. **Stateless Models**: Each API call is independent. Context is maintained by passing the entire history each time.

3. **Round-Robin Fairness**: `turn % 3` ensures everyone gets equal speaking opportunities.

4. **Growing History**: `conversation_history` grows linearly, which can impact token usage in later turns.

5. **Configuration Isolation**: Each participant has their own config, allowing different personalities through temperature/token settings.
