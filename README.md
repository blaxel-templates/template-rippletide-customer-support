# Customer Support Agent - Rippletide

<p align="center">
  <img style="border-radius:10px" src="cover.png" alt="Rippletide x Blaxel" width="90%"/>
</p>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Rippletide](https://img.shields.io/badge/Rippletide-powered-brightgreen.svg)](https://rippletide.com/)
[![AI Agents](https://img.shields.io/badge/AI-Agents-orange.svg)](https://rippletide.com/)

</div>

An intelligent customer support agent powered by Rippletide's enterprise-grade AI platform and deployed on Blaxel. Use this template to create an SDK agent, extract questions from a PDF, evaluate answers, and ship a production-ready endpoint with near-zero hallucinations.

## 📑 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📋 Prerequisites](#-prerequisites)
- [💻 Installation](#-installation)
- [🔧 Usage](#-usage)
- [📁 Project Structure](#-project-structure)
- [❓ Troubleshooting](#-troubleshooting)

## ✨ Features

- 🤖 **SDK Agent Creation** – Build governed Rippletide agents programmatically
- 📄 **PDF Question Extraction** – Pull questions/answers from PDFs for evaluation
- ✅ **Answer Evaluation** – Score outputs against expected answers with reports
- 🔧 **Rich Configuration** – Q&A pairs, tool calls, guardrails, user inputs, state rules
- 🚀 **Blaxel Deployment** – One-command deploy to a secure, low-latency runtime
- 🔐 **Environment-Based Secrets** – `.env`-driven API keys and agent IDs
- 🛡️ **Reliability & Safety** – Rippletide validation/authorization for <1% hallucinations
- 🌐 **Production Endpoint** – Hosted HTTPS inference endpoint ready for your apps

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/blaxel-ai/template-rippletide-customer-support.git

# Navigate to the project directory
cd template-rippletide-customer-support

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and add your RIPPLETIDE_API_KEY (and later RIPPLETIDE_AGENT_ID)

# Create SDK agent configuration
cp agent_config.json.example agent_config.json

# Run setup to create your agent in Rippletide and evaluate it
uv run src/setup_agent.py agent_config.json --pdf knowledge.pdf
# This will output an Agent ID - add it to your .env file as RIPPLETIDE_AGENT_ID

# Start the server
bl serve --hotreload

# In another terminal, test the agent
bl chat --local template-rippletide-customer-support

# Deploy to Blaxel (optional, when ready)
bl deploy
```

## 📋 Prerequisites

- **Python:** 3.10 or later
- **[UV](https://github.com/astral-sh/uv):** An extremely fast Python package and project manager, written in Rust
- **Git** (to clone the template)
- **Rippletide API Key:** Get it from [https://eval.rippletide.com](https://eval.rippletide.com) → Settings.
- **Blaxel Account & CLI:** Follow the [quickstart guide](https://docs.blaxel.ai/Get-started#quickstart).
  - Install CLI:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/blaxel-ai/toolkit/main/install.sh | BINDIR=/usr/local/bin sudo -E sh
    ```
  - Login:
    ```bash
    bl login
    ```
- Optional: Basic JSON knowledge, REST API familiarity

## 💻 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/blaxel-ai/template-rippletide-customer-support.git
   cd template-rippletide-customer-support
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   RIPPLETIDE_API_KEY=your-api-key-here
   RIPPLETIDE_AGENT_ID=your-agent-id-here
   ```

4. **Configure your agent:**
   ```bash
   cp agent_config.json.example agent_config.json
   # Edit agent_config.json with your configuration (optional)
   ```

## 🔧 Usage

### Configure your environment

1) Get your API key: [https://eval.rippletide.com](https://eval.rippletide.com) → Settings → Generate key  
2) Add it to `.env`: `RIPPLETIDE_API_KEY=your-api-key`  
3) Run setup (below) and add the emitted Agent ID to `.env`: `RIPPLETIDE_AGENT_ID=your-agent-id`

### Understand `agent_config.json`

- `agent_purpose`: Main prompt describing the agent’s role
- `qa_pairs`: Ground-truth Q&A for knowledge
- `guardrails`: Rules/constraints for safe answers
- `tool_calls`: External API calls the agent can trigger
- `user_input_collection`: Inputs to gather from users
- `format_answer`: Response formatting instructions
- `state_predicate`: Rules for ending/transitioning conversations

Edit `agent_config.json` to customize behavior.

### Create and evaluate your Rippletide agent

```bash
cp agent_config.json.example agent_config.json
# (Optional) customize the file

uv run src/setup_agent.py agent_config.json --pdf knowledge.pdf
```

This script:
1) Loads your configuration  
2) Creates a new SDK agent in Rippletide  
3) Configures Q&A, tool calls, guardrails, user inputs  
4) Creates an evaluation agent  
5) Extracts questions/expected answers from the PDF  
6) Asks the SDK agent the first question  
7) Evaluates the answer vs. the expected answer  
8) Prints the evaluation report and outputs an Agent ID

### Run locally with Blaxel

```bash
bl serve --hotreload
bl chat --local template-rippletide-customer-support
```

### Deploy to production

```bash
bl deploy
```

Blaxel will build and deploy your project and expose a hosted endpoint, e.g.:
`https://run.blaxel.ai/{YOUR-WORKSPACE}/agents/{YOUR-AGENT}`

### Call your deployed agent

```bash
curl -X POST https://run.blaxel.ai/YOUR-WORKSPACE/agents/YOUR-AGENT \
  -H "Content-Type: application/json" \
  -H 'X-Blaxel-Authorization: Bearer YOUR-TOKEN' \
  -H 'X-Blaxel-Workspace: YOUR-WORKSPACE' \
  -d '{
    "message": "Hi, I need help with my recent order.",
    "user_id": "customer_123"
  }'
```

Request flow: input → LLM intent → Rippletide validation/authorization → safe action → runtime execution → response.

### Extend your agent

Use `agent_config.json` to add:
- Multi-step workflows, eligibility checks, refunds, troubleshooting trees
- Multi-language support, routing (tier 1 → tier 2), escalation rules
- Form-filling and state-aware conversations

### Code Examples

#### Example 1: Simple SDK Agent

```python
from src.rippletide_client import RippletideAgent
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize
agent = RippletideAgent(api_key=os.getenv("RIPPLETIDE_API_KEY"))

# Create agent
agent_data = agent.create_agent(
    name="Toy Agent",
    prompt="You are a helpful assistant that answers questions about toys."
)

# Simple config
config = {
    "agent_purpose": "Answer questions about toys",
    "qa_pairs": [
        {
            "question": "What is a teddy bear?",
            "answer": "A teddy bear is a soft toy bear, typically made of fabric and filled with stuffing."
        }
    ],
    "state_predicate": {
        "question_to_evaluate": "I cannot answer that.",
        "re_evaluate": True,
        "transition_kind": "end"
    }
}

# Setup knowledge
agent.setup_agent_knowledge(agent_data["id"], config)

# Chat
response = agent.chat("What is a teddy bear?")
print(response["answer"])
```

#### Example 2: SDK Agent with Tool Calls

```python
from src.rippletide_client import RippletideAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = RippletideAgent(api_key=os.getenv("RIPPLETIDE_API_KEY"))
agent_data = agent.create_agent(
    name="Order Status Agent",
    prompt="You help customers check their order status."
)

config = {
    "agent_purpose": "Help customers track orders",
    "qa_pairs": [],
    "tool_calls": [
        {
            "label": "get_order_status",
            "description": "Get order status by order ID",
            "api_call_config": {
                "url": "https://api.example.com/orders/{{order_id}}",
                "method": "GET",
                "headers": {"x-api-key": "your-key"},
                "body": {}
            },
            "required_user_inputs": ["order_id"]
        }
    ],
    "user_input_collection": [
        {
            "label": "order_id",
            "description": "Order number (alphanumeric)"
        }
    ],
    "guardrails": [
        {
            "label": "privacy",
            "description": "Never share customer data"
        }
    ],
    "format_answer": "Start with 'Hello! ' and end with 'Is there anything else?'",
    "state_predicate": {
        "question_to_evaluate": "I cannot help with that.",
        "re_evaluate": True,
        "transition_kind": "end"
    }
}

agent.setup_agent_knowledge(agent_data["id"], config)
response = agent.chat("What's the status of order 12345?")
```

#### Example 3: Creating and Evaluating an Agent with PDF

```python
from src.rippletide_client import RippletideAgent, RippletideEvalClient
import os
from dotenv import load_dotenv

load_dotenv()

# Step 1: Create SDK agent
agent = RippletideAgent(api_key=os.getenv("RIPPLETIDE_API_KEY"))
agent_data = agent.create_agent(
    name="Customer Support Agent",
    prompt="You are a helpful customer support agent."
)

config = {
    "agent_purpose": "Help customers with their inquiries",
    "qa_pairs": [
        {
            "question": "What are your business hours?",
            "answer": "Monday through Friday, 9 AM to 6 PM EST"
        }
    ]
}

agent.setup_agent_knowledge(agent_data["id"], config)

# Step 2: Create eval agent and extract questions from PDF
eval_client = RippletideEvalClient(
    api_key=os.getenv("RIPPLETIDE_API_KEY"),
    base_url="https://rippletide-backend.azurewebsites.net"
)

eval_agent = eval_client.create_agent(name="Evaluation Agent")
result = eval_client.extract_questions_from_pdf(
    agent_id=eval_agent['id'],
    pdf_path="knowledge.pdf"
)

qa_pairs = result.get('qaPairs', [])

# Step 3: Ask the first question and evaluate
if qa_pairs:
    qa_pair = qa_pairs[0]
    question = qa_pair.get('question', qa_pair.get('prompt', ''))
    expected_answer = qa_pair.get('answer', qa_pair.get('expectedAnswer', ''))
    
    # Ask the SDK agent
    response = agent.chat(question)
    agent_answer = response.get("answer", "") if response else ""
    
    # Evaluate the answer
    report = eval_client.evaluate(
        agent_id=eval_agent['id'],
        question=question,
        expected_answer=expected_answer if expected_answer else None,
        answer=agent_answer
    )
    
    print(f"Question: {question}")
    print(f"Label: {report['label']}")
    print(f"Justification: {report['justification']}")
```

## 📁 Project Structure

```
blaxel-rippletide/
├── src/
│   ├── rippletide_client.py   # RippletideAgent & RippletideEvalClient
│   ├── setup_agent.py          # Unified agent setup and evaluation script
│   ├── agent.py                # FastAPI agent endpoint
│   ├── main.py                 # FastAPI app
│   └── middleware.py           # Request middleware
├── agent_config.json.example   # Agent config template
├── .env.example                # Environment variables template
├── pyproject.toml              # Python project configuration
├── blaxel.toml                 # Blaxel configuration
├── cover.png                   # README cover image
├── icon.png                    # Branding asset
├── icon-dark.png               # Branding asset
└── README.md
```

## ❓ Troubleshooting

### API key / agent ID
- Ensure `.env` exists with `RIPPLETIDE_API_KEY` and `RIPPLETIDE_AGENT_ID`.
- Re-run setup to regenerate the Agent ID if needed:
  ```bash
  uv run src/setup_agent.py agent_config.json --pdf knowledge.pdf
  ```

### Agent fails to create
- Confirm `RIPPLETIDE_API_KEY` is set and valid.
- Verify the PDF path is correct and readable.

### No questions extracted from PDF
- Make sure the PDF has extractable Q&A pairs.
- Check the `--pdf` path.
- The script will fallback to test prompts if extraction is empty.

### Blaxel CLI issues
- `bl: command not found` → install the CLI (see Prerequisites) and run `bl login`.
- Deploy errors → retry `bl auth login`, then `bl deploy`.

### Endpoint errors
- Test locally first: `bl serve --hotreload` and `bl chat --local template-rippletide-customer-support`.
- Check that `.env` is populated and the server port is free.

### Import errors (e.g., `dotenv`)
- Install deps: `uv sync` (python-dotenv is included in `pyproject.toml`).

## Support

- [Rippletide Docs](https://docs.rippletide.com/)
- [Blaxel Docs](https://docs.blaxel.ai)

## License

MIT License - see [LICENSE](LICENSE) file for details.
