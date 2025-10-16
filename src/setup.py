#!/usr/bin/env python3
"""
Rippletide Customer Support Agent Setup Script

This script creates and configures a customer support agent in Rippletide
by reading configuration files from the knowledge-base folder.

Based on: https://sdk.rippletide.com/documentation/get_started/
"""

import os
import sys
import json
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
from typing import Any

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_info(message: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

def log_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def log_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def log_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def log_header(message: str):
    """Print header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{message}")
    print(f"{'='*60}{Colors.ENDC}\n")

def load_config_file(file_path: Path) -> Any:
    """Load and parse a JSON configuration file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_error(f"Configuration file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON in {file_path}: {e}")
        sys.exit(1)

async def main():
    """Main setup function"""
    log_header("🚀 Rippletide Customer Support Agent Setup")

    # Load environment variables
    log_info("Loading environment variables from .env file...")
    load_dotenv()

    # Get API key
    api_key = os.getenv("BLAXEL_API_KEY")
    if not api_key:
        log_error("BLAXEL_API_KEY not found in .env file")
        log_warning("Please add your Blaxel API key to the .env file")
        log_warning("You can get one from https://app.blaxel.ai/profile/security")
        sys.exit(1)

    log_success("API key loaded successfully")

    # Setup API connection
    BASE_URL = os.getenv("BASE_URL", "https://agent.rippletide.com/api/sdk")
    headers = {
        "X-Blaxel-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Define paths
    kb_dir = Path(__file__).parent.parent / "knowledge-base"

    log_info(f"Reading configuration files from: {kb_dir}")

    # Load all configuration files
    tags_config = load_config_file(kb_dir / "tags.json")
    qanda_config = load_config_file(kb_dir / "qanda.json")
    state_predicate_config = load_config_file(kb_dir / "state_predicate.json")

    log_success("All configuration files loaded successfully")

    # Step 1: Create Agent
    log_header("📋 Step 1: Creating Customer Support Agent")

    agent_prompt = """You are a professional customer support agent. Your role is to help customers with their inquiries, answer questions about products and services, and resolve issues efficiently and empathetically.

Guidelines:
- Always be polite, helpful, and professional
- Listen carefully to understand the customer's needs
- Use only information from your knowledge base to provide accurate answers
- If you cannot help with something, escalate to a human agent
- Confirm understanding before providing solutions
- Provide clear next steps and set appropriate expectations"""

    log_info("Creating agent with system prompt...")
    print(f"{Colors.OKCYAN}Agent Prompt:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{agent_prompt[:200]}...{Colors.ENDC}\n")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/agent",
                headers=headers,
                json={
                    "name": "customer-support-agent",
                    "prompt": agent_prompt
                }
            )
            response.raise_for_status()
            agent = response.json()
            agent_id = agent["id"]
            log_success(f"Agent created successfully! Agent ID: {agent_id}")
        except httpx.HTTPStatusError as e:
            log_error(f"Failed to create agent: {e}")
            log_error(f"Response: {e.response.text}")
            sys.exit(1)
        except httpx.RequestError as e:
            log_error(f"Failed to create agent: {e}")
            sys.exit(1)

        # Step 2: Create Tags
        log_header(f"🏷️  Step 2: Creating Tags ({len(tags_config)} tags)")

        tag_ids = {}

        # First, fetch existing tags
        log_info("Checking for existing tags...")
        try:
            response = await client.get(f"{BASE_URL}/tag", headers=headers)
            if response.status_code == 200 and response.json():
                existing_tags = response.json().get("tags", [])
                tag_ids = {t['name']: t['id'] for t in existing_tags}
                if tag_ids:
                    log_info(f"Found {len(tag_ids)} existing tags")
        except httpx.RequestError:
            pass

        for tag in tags_config:
            tag_name = tag["name"]
            tag_description = tag["description"]

            if tag_name in tag_ids:
                log_warning(f"Tag '{tag_name}' already exists, skipping...")
                continue

            log_info(f"Creating tag: {tag_name}")
            try:
                response = await client.post(
                    f"{BASE_URL}/tag",
                    headers=headers,
                    json={
                        "name": tag_name,
                        "description": tag_description
                    }
                )
                response.raise_for_status()
                tag_ids[tag_name] = response.json()["id"]
                log_success(f"✓ {tag_name}")
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                log_error(f"Failed to create tag '{tag_name}': {e}")

        log_success(f"Tags setup complete! Created {len(tag_ids)} tags")

        # Step 3: Create Q&A Knowledge Base
        log_header(f"📚 Step 3: Creating Knowledge Base ({len(qanda_config)} Q&A pairs)")

        qanda_count = 0
        for qanda in qanda_config:
            question = qanda["question"]
            answer = qanda["answer"]
            qanda_tags = qanda.get("tags", [])

            log_info(f"Adding Q&A: {question[:50]}...")

            try:
                # Create Q&A
                response = await client.post(
                    f"{BASE_URL}/q-and-a",
                    headers=headers,
                    json={
                        "question": question,
                        "answer": answer,
                        "agent_id": agent_id
                    }
                )
                response.raise_for_status()
                qanda_id = response.json()["id"]

                # Link Q&A to tags
                for tag_name in qanda_tags:
                    if tag_name in tag_ids:
                        await client.post(
                            f"{BASE_URL}/q-and-a-tag",
                            headers=headers,
                            json={
                                "q_and_a_id": qanda_id,
                                "tag_id": tag_ids[tag_name]
                            }
                        )

                qanda_count += 1
                log_success(f"✓ Added with {len(qanda_tags)} tags")
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                log_error(f"Failed to create Q&A: {e}")

        log_success(f"Knowledge base setup complete! Added {qanda_count} Q&A pairs")

        # Step 4: Setup State Predicate
        log_header("🔀 Step 4: Configuring Conversation Flow (State Predicate)")

        log_info("Setting up conversation flow and decision tree...")

        try:
            response = await client.put(
                f"{BASE_URL}/state-predicate/{agent_id}",
                headers=headers,
                json={"state_predicate": state_predicate_config}
            )
            response.raise_for_status()
            log_success("Conversation flow configured successfully!")
        except httpx.HTTPStatusError as e:
            log_error(f"Failed to setup state predicate: {e}")
            log_error(f"Response: {e.response.text}")
        except httpx.RequestError as e:
            log_error(f"Failed to setup state predicate: {e}")

    # Final Summary
    log_header("🎉 Setup Complete!")

    print(f"{Colors.OKGREEN}{Colors.BOLD}Your Rippletide Customer Support Agent has been created successfully!{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}Summary:{Colors.ENDC}")
    print(f"  • Agent ID: {Colors.BOLD}{agent_id}{Colors.ENDC}")
    print(f"  • Tags: {len(tag_ids)}")
    print(f"  • Q&A Pairs: {qanda_count}")
    print(f"  • State Flow: Configured\n")

    print(f"{Colors.WARNING}{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"{Colors.WARNING}1. Add the Agent ID to your .env file:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   RIPPLETIDE_AGENT_ID={agent_id}{Colors.ENDC}\n")

    print(f"{Colors.WARNING}2. Start the agent with Blaxel:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   bl serve --hotreload{Colors.ENDC}\n")

    print(f"{Colors.WARNING}3. Test your agent locally:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   bl chat --local template-rippletide-customer-support{Colors.ENDC}\n")

    print(f"{Colors.WARNING}4. When ready, deploy to production:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   bl deploy{Colors.ENDC}\n")

    print(f"{Colors.OKGREEN}For more information, visit:{Colors.ENDC}")
    print(f"{Colors.OKBLUE}  • Rippletide Docs: https://sdk.rippletide.com/documentation/get_started/{Colors.ENDC}")
    print(f"{Colors.OKBLUE}  • Blaxel Docs: https://docs.blaxel.ai{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

