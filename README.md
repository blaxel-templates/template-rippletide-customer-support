# Customer Support Agent - Rippletide

<p align="center">
  <img style="border-radius:10px" src=".github/assets/cover.png" alt="Rippletide x Blaxel" width="90%"/>
</p>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Rippletide](https://img.shields.io/badge/Rippletide-powered-brightgreen.svg)](https://rippletide.com/)
[![AI Agents](https://img.shields.io/badge/AI-Agents-orange.svg)](https://rippletide.com/)

</div>

An intelligent customer support agent powered by Rippletide's enterprise-grade AI platform. This agent delivers 24/7 assistance with instant, accurate responses to customer inquiries while reducing ticket volume and response times.

This template shows how to integrate Rippletide's Decision Database and AI agents with Blaxel to create an autonomous customer support system that handles customer inquiries with high reliability, compliance, and full auditability.

## 📑 Table of Contents

- [Customer Support Agent - Rippletide](#customer-support-agent---rippletide)
  - [📑 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🚀 Quick Start](#-quick-start)
  - [📋 Prerequisites](#-prerequisites)
  - [💻 Installation](#-installation)
  - [⚙️ Configuration](#️-configuration)
    - [Step 1: Get Your Rippletide API Key](#step-1-get-your-rippletide-api-key)
    - [Step 2: Customize Your Knowledge Base](#step-2-customize-your-knowledge-base)
    - [Step 3: Run the Setup Script](#step-3-run-the-setup-script)
    - [Step 4: Add Agent ID to Environment](#step-4-add-agent-id-to-environment)
  - [🔧 Usage](#-usage)
    - [Running Locally](#running-locally)
    - [Testing](#testing)
    - [Deployment](#deployment)
  - [📁 Project Structure](#-project-structure)
  - [❓ Troubleshooting](#-troubleshooting)
    - [Common Issues](#common-issues)
  - [👥 Contributing](#-contributing)
  - [🆘 Support](#-support)
  - [📄 License](#-license)

## ✨ Features

- **24/7 Customer Support**: Always-on AI agent providing instant assistance to customers
- **Enterprise-Grade Reliability**: Built on Rippletide's Decision Database with <1% hallucination rate
- **Knowledge Base Integration**: Unified hypergraph database for consistent, accurate responses
- **Multi-Channel Support**: Handle customer inquiries across various communication channels
- **Full Auditability**: Complete tracking and logging of all agent decisions and interactions
- **GDPR Compliant**: Built-in data protection and privacy compliance
- **Scalable Architecture**: Handle high volumes of customer inquiries efficiently

## 🚀 Quick Start

For those who want to get up and running quickly:

```bash
# Clone the repository
git clone https://github.com/blaxel-ai/template-rippletide-customer-support.git

# Navigate to the project directory
cd template-rippletide-customer-support

# Install dependencies
uv sync

# Configure environment variables
cp .env-sample .env
# Add your BLAXEL_API_KEY to .env . You can get one from https://app.blaxel.ai/profile/security

# Customize your knowledge base (optional)
# Edit files in knowledge-base/ folder

# Run setup to create your agent in Rippletide
uv run src/setup.py
# This will output an Agent ID - add it to your .env file

# Start the server
bl serve --hotreload

# In another terminal, test the agent
bl chat --local template-rippletide-customer-support
```

## 📋 Prerequisites

- **Python:** 3.10 or later
- **[UV](https://github.com/astral-sh/uv):** An extremely fast Python package and project manager, written in Rust
- **Blaxel Platform Setup:** Complete Blaxel setup by following the [quickstart guide](https://docs.blaxel.ai/Get-started#quickstart)
  - **[Blaxel CLI](https://docs.blaxel.ai/Get-started):** Ensure you have the Blaxel CLI installed. If not, install it globally:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/blaxel-ai/toolkit/main/install.sh | BINDIR=/usr/local/bin sudo -E sh
    ```
  - **Blaxel login:** Login to Blaxel platform
    ```bash
    bl login
    ```

## 💻 Installation

**Clone the repository and install dependencies:**

```bash
git clone https://github.com/blaxel-ai/template-rippletide-customer-support.git
cd template-rippletide-customer-support
uv sync
```

## ⚙️ Configuration

### Step 1: Get Your Rippletide API Key

Contact [patrick@rippletide.com](mailto:patrick@rippletide.com) or [yann@rippletide.com](mailto:yann@rippletide.com) to get your Rippletide API key.

Once you have your API key, create a `.env` file in the project root:

```env
BLAXEL_API_KEY=your-api-key-here
```

### Step 2: Customize Your Knowledge Base

The `knowledge-base/` folder contains sample customer support data. Customize these files for your business:

- **tags.json** - Categories for organizing your knowledge (e.g., "shipping_delivery", "returns_refunds")
- **qanda.json** - Question-answer pairs that form your agent's knowledge base
- **state_predicate.json** - Conversation flow and decision tree

See the [knowledge-base/README.md](knowledge-base/README.md) for detailed information on customizing each file.

### Step 3: Run the Setup Script

The setup script will create your agent in Rippletide with all the configurations from the knowledge-base folder:

```bash
uv run src/setup.py
```

The script will:
1. ✅ Create a customer support agent in Rippletide
2. ✅ Set up all tags from tags.json
3. ✅ Add Q&A pairs from qanda.json (with tag associations)
4. ✅ Set up conversation flow from state_predicate.json
5. ✅ Provide you with an Agent ID

### Step 4: Add Agent ID to Environment

After running the setup script, add the generated Agent ID to your `.env` file:

```env
BLAXEL_API_KEY=your-api-key-here
RIPPLETIDE_AGENT_ID=your-agent-id-here
```

## 🔧 Usage

### Running Locally

Start the development server with hot reloading:

```bash
bl serve --hotreload
```

For production run:

```bash
bl serve
```

_Note:_ The development server automatically restarts when you make changes to the source code.

### Testing

You can test your customer support agent locally:

```bash
# Using the Blaxel CLI chat interface
bl chat --local template-rippletide-customer-support
```

Example customer support queries you can test:

```
I haven't received my order confirmation email. Can you help?
```

```
What is your return policy for products purchased online?
```

```
How can I track my order?
```

```
I need to update my billing address. How do I do that?
```

You can also run it directly with specific input:

```bash
bl run agent rippletide-support-agent --local --data '{"inputs": "What are your business hours?"}'
```

### Deployment

When you are ready to deploy your customer support agent:

```bash
bl deploy
```

This command uses your code and the configuration files under the `.blaxel` directory to deploy your customer support agent on the Blaxel platform. Once deployed, your agent will be available to handle customer inquiries through your configured channels.

## 📁 Project Structure

- **src/main.py** - Application entry point and FastAPI server setup
- **src/agent.py** - Core customer support agent implementation with Rippletide API integration
- **src/setup.py** - Setup script to create and configure your Rippletide agent
- **src/middleware.py** - Request/response middleware and error handling
- **knowledge-base/** - Customer support knowledge base configuration
  - **tags.json** - Category tags for organizing knowledge
  - **qanda.json** - Question-answer pairs for the knowledge base
  - **state_predicate.json** - Conversation flow configuration
  - **README.md** - Knowledge base customization guide
- **pyproject.toml** - UV package manager configuration with dependencies
- **blaxel.toml** - Blaxel deployment configuration
- **.env-sample** - Environment variables template
- **LICENSE** - MIT license file

## ❓ Troubleshooting

## Documentation
See the [Rippletide Getting Started guide](https://sdk.rippletide.com/documentation/get_started/) for more information

### Common Issues

1. **Setup Script Issues**:
   - Ensure `BLAXEL_API_KEY` is set in your `.env` file before running `setup.py`
   - Check that all JSON files in `knowledge-base/` are valid (use a JSON validator)
   - If setup fails partially, you may need to delete the agent in Rippletide and run setup again
   - Review the colored console output for specific error messages

2. **Rippletide Integration Issues**:
   - Verify your Rippletide API key is valid and active
   - Ensure your agent ID is correct and the agent is properly configured
   - Check that your knowledge base is populated with relevant information
   - Review the Rippletide dashboard for agent status and logs
   - Confirm API endpoint connectivity: `https://agent.rippletide.com/api/sdk`

3. **Blaxel Platform Issues**:
   - Ensure you're logged in to your workspace: `bl login`
   - Verify models are available: `bl get models`
   - Check that functions exist: `bl get functions`
   - Review Blaxel logs for deployment or runtime errors

4. **Agent Response Issues**:
   - Verify your agent's system prompt is clear and specific
   - Check knowledge base coverage for common customer queries
   - Monitor response accuracy and hallucination metrics in Rippletide dashboard

5. **Python Environment Issues**:
   - Make sure you have Python 3.10+
   - Try `uv sync --upgrade` to update dependencies
   - Check for conflicting package versions
   - Verify virtual environment activation with UV
   - Ensure all required environment variables are set

6. **Conversation Context Issues**:
   - Check that conversation UUIDs are being properly tracked
   - Verify conversation history is maintained across messages
   - Review conversation flow in Rippletide dashboard

For more help, please [submit an issue](https://github.com/blaxel-ai/template-rippletide-customer-support/issues) on GitHub.

## 👥 Contributing

Contributions are welcome! Here's how you can contribute:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Submit** a Pull Request

Please make sure to update tests as appropriate and follow the code style of the project.

## 🆘 Support

If you need help with this template:

- [Submit an issue](https://github.com/blaxel-ai/template-rippletide-customer-support/issues) for bug reports or feature requests
- Visit the [Blaxel Documentation](https://docs.blaxel.ai) for platform guidance
- Check the [Rippletide Documentation](https://doc.rippletide.com/) for agent configuration help
- Visit the [Rippletide Help Center](https://help.rippletide.com/en/) for support articles
- Join our [Discord Community](https://discord.gg/G3NqzUPcHP) for real-time assistance

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
