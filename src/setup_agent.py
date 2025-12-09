#!/usr/bin/env python3
"""
Rippletide Agent Setup Script

Creates an SDK agent, extracts questions from a PDF, asks the agent each question,
and evaluates the answers using the eval client.

Usage:
    uv run src/setup_agent.py agent_config.json --pdf knowledge.pdf
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rippletide_client import RippletideAgent, RippletideEvalClient

# Hardcoded API key - update this with your API key from https://eval.rippletide.com
RIPPLETIDE_API_KEY = ""
# URL for evaluation API
RIPPLETIDE_EVAL_BASE_URL = "https://rippletide-backend.azurewebsites.net"

def load_config_file(file_path: Path) -> Any:
    """Load and parse a JSON configuration file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup Rippletide Agent and Evaluate")
    parser.add_argument(
        "config",
        type=str,
        help="Path to agent configuration JSON file"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to PDF file for extracting questions and adding to eval agent knowledge base"
    )
    
    args = parser.parse_args()
    
    if RIPPLETIDE_API_KEY == "":
        print("Error: API key not configured. Please update RIPPLETIDE_API_KEY in setup_agent.py", file=sys.stderr)
        sys.exit(1)
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    config = load_config_file(config_path)
    
    # Step 1: Create SDK agent using RippletideAgent
    print("=" * 60)
    print("Step 1: Creating SDK Agent")
    print("=" * 60)
    
    agent = RippletideAgent(RIPPLETIDE_API_KEY, None)
    agent_prompt = config.get("agent_purpose", "You are a helpful assistant.")
    agent_name = config.get("agent_name", "rippletide-agent")
    
    agent_data = agent.create_agent(name=agent_name, prompt=agent_prompt)
    agent_id = agent_data["id"]
    print(f"Created SDK agent with ID: {agent_id}")
    
    # Setup agent knowledge
    agent.setup_agent_knowledge(agent_id, config)
    print(f"Agent knowledge configured successfully")
    
    # Step 2: Create eval agent and extract questions from PDF
    print("\n" + "=" * 60)
    print("Step 2: Creating Evaluation Agent and Extracting Questions from PDF")
    print("=" * 60)
    
    eval_client = RippletideEvalClient(api_key=RIPPLETIDE_API_KEY, base_url=RIPPLETIDE_EVAL_BASE_URL)
    
    # Create an eval agent for evaluation
    eval_agent = eval_client.create_agent(name="Evaluation Agent")
    eval_agent_id = eval_agent['id']
    print(f"Created evaluation agent with ID: {eval_agent_id}")
    
    # Extract questions from PDF
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    print(f"\nExtracting questions from PDF: {pdf_path}")
    result = eval_client.extract_questions_from_pdf(
        agent_id=eval_agent_id,
        pdf_path=str(pdf_path)
    )
    
    # Debug: print the result structure
    print(f"PDF extraction result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    # Try different possible keys for Q&A pairs
    qa_pairs = result.get('qaPairs', result.get('qa_pairs', result.get('questions', [])))
    
    # If still empty, try to get test prompts from the agent
    if not qa_pairs:
        print("No Q&A pairs found in extraction result, trying to get test prompts...")
        try:
            test_prompts = eval_client.get_test_prompts(eval_agent_id)
            if test_prompts:
                qa_pairs = test_prompts
                print(f"Found {len(qa_pairs)} test prompts from agent")
        except Exception as e:
            print(f"Could not get test prompts: {e}")
    
    print(f"Extracted {len(qa_pairs)} Q&A pairs from PDF")
    
    if not qa_pairs:
        print("Error: No Q&A pairs extracted from PDF", file=sys.stderr)
        print(f"Full extraction result: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    
    # Step 3: Ask SDK agent the first question and evaluate
    print("\n" + "=" * 60)
    print("Step 3: Asking SDK Agent First Question and Evaluating Answer")
    print("=" * 60)
    
    # Get only the first question
    if not qa_pairs:
        print("Error: No Q&A pairs available", file=sys.stderr)
        sys.exit(1)
    
    qa_pair = qa_pairs[0]
    
    # Try different possible keys for question and answer
    question = qa_pair.get('question', qa_pair.get('prompt', ''))
    expected_answer = qa_pair.get('answer', qa_pair.get('expectedAnswer', qa_pair.get('expected_answer', '')))
    
    if not question:
        print("Error: No question found in first Q&A pair", file=sys.stderr)
        print(f"  Available keys: {list(qa_pair.keys())}")
        sys.exit(1)
    
    print(f"\nQuestion: {question}")
    if expected_answer:
        print(f"Expected Answer: {expected_answer}")
    
    # Ask the SDK agent
    response = agent.chat(question)
    if response is None:
        print("Error: No response from agent", file=sys.stderr)
        sys.exit(1)
    agent_answer = response.get("answer", "No answer provided")
    print(f"Agent Answer: {agent_answer}")
    
    # Evaluate the answer
    try:
        report = eval_client.evaluate(
            agent_id=eval_agent_id,
            question=question,
            expected_answer=expected_answer if expected_answer else None,
            answer=agent_answer
        )
    except Exception as e:
        print(f"Error evaluating answer: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nEvaluation Label: {report.get('label', 'N/A')}")
    print(f"Evaluation Justification: {report.get('justification', 'N/A')}")
    
    # Step 4: Print evaluation report
    print("\n" + "=" * 60)
    print("Step 4: Evaluation Report")
    print("=" * 60)
    print(f"SDK Agent ID: {agent_id}")
    print(f"Evaluation Agent ID: {eval_agent_id}")
    print(f"\nQuestion: {question}")
    print(f"Agent Answer: {agent_answer}")
    if expected_answer:
        print(f"Expected Answer: {expected_answer}")
    print(f"\nEvaluation Report:")
    print(json.dumps(report, indent=2))
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"SDK Agent ID: {agent_id}")

if __name__ == "__main__":
    main()

