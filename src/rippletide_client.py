"""
Rippletide Client supporting both SDK Agent Creation and Evaluation Agent Creation.

This module provides two client classes:
1. RippletideAgent - For creating full-featured SDK agents (like postgoux pattern)
2. RippletideEvalClient - For creating evaluation agents (like starter pattern)
"""
import uuid
import random
import requests
import httpx
from typing import Optional, Dict, Any, List, BinaryIO, Union
from pathlib import Path


class RippletideAgent:
    """
    Client for creating full-featured SDK agents with tool calls, user inputs, guardrails, etc.
    Based on postgoux/backend/src/agent/custom_agent/agent.py pattern.
    
    Args:
        api_key: API key for authenticated requests
        base_url: Base URL for the API (defaults to production SDK endpoint)
    """
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize the agent with API key and base URL."""
        self.api_key = api_key
        self.base_url = base_url or "https://agent.rippletide.com/api/sdk"
        self.headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        self.agent_id: Optional[str] = None
        self.conversation_id: str = str(uuid.uuid4())

    def create_agent(self, name: str, prompt: str) -> Dict[str, Any]:
        """Create a new agent via the Rippletide API."""
        url = f"{self.base_url}/agent"
        data = {"name": name, "prompt": prompt}

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        agent_data = response.json()
        self.agent_id = agent_data.get("id")
        return agent_data

    def setup_agent_knowledge(self, agent_id: str, config: dict) -> None:
        """Set up agent knowledge from configuration."""
        print("Setting up agent knowledge from config...")

        # Set up state predicate if provided
        if "state_predicate" in config and config["state_predicate"]:
            print("Setting up state predicate...")
            response = requests.put(
                f"{self.base_url}/state-predicate/{agent_id}",
                headers=self.headers,
                json={"state_predicate": config["state_predicate"]},
            )
            response.raise_for_status()
            print("State predicate configured")

        # Set up Q&A pairs if provided
        if "qa_pairs" in config and config["qa_pairs"]:
            print("Setting up Q&A pairs...")
            for qa in config["qa_pairs"]:
                qa_data = {"question": qa["question"], "answer": qa["answer"], "agent_id": agent_id}
                response = requests.post(f"{self.base_url}/q-and-a", headers=self.headers, json=qa_data)
                response.raise_for_status()
            print(f"{len(config['qa_pairs'])} Q&A pairs configured")

        # Set up user input collection if provided
        if "user_input_collection" in config and config["user_input_collection"]:
            print("Setting up user input collection...")
            user_inputs_url = f"{self.base_url}/agent/{agent_id}/user-inputs"

            response = requests.post(user_inputs_url, headers=self.headers, json=config["user_input_collection"])
            if response.status_code == 200:
                print("   [SUCCESS] User input collection configured successfully")
                for input_field in config["user_input_collection"]:
                    print(f"   - {input_field['label']}: {input_field['description']}")
            else:
                print(f"   [ERROR] Failed to configure user input collection: {response.status_code} - {response.text}")

            print(f"{len(config['user_input_collection'])} input fields configured")

        # Set up tool calls if provided
        if "tool_calls" in config and config["tool_calls"]:
            print("Setting up tool calls...")
            for tool_call in config["tool_calls"]:
                tool_call_data = {
                    "label": tool_call.get("label", "unnamed_tool_call"),
                    "description": tool_call.get("description", ""),
                    "api_call_config": tool_call.get("api_call_config", {}),
                    "required_user_inputs": tool_call.get("required_user_inputs", []),
                }

                tool_call_headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "x-rippletide-agent-id": str(agent_id),
                    "x-rippletide-conversation-id": str(self.conversation_id),
                }

                tool_call_url = f"{self.base_url}/add-tool-call"
                response = requests.post(tool_call_url, headers=tool_call_headers, json=tool_call_data)
                if response.status_code == 200:
                    print(f"   - Configured tool call: {tool_call_data['label']}")
                else:
                    print(f"   - Tool call endpoint returned {response.status_code}: {response.text}")
            print(f"{len(config['tool_calls'])} tool calls configured")

        # Set up format answer if provided
        if "format_answer" in config and config["format_answer"]:
            print("Setting up format answer...")
            format_answer_url = f"{self.base_url}/tool-calls/agent/{agent_id}/add-format-answer"
            format_answer_headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "x-rippletide-agent-id": str(agent_id),
                "x-rippletide-conversation-id": str(self.conversation_id),
            }
            response = requests.post(
                format_answer_url,
                headers=format_answer_headers,
                json={"format_answer": config["format_answer"]},
            )
            if response.status_code == 200:
                print(f"   [SUCCESS] Format answer configured: {config['format_answer'][:50]}...")
            else:
                print(f"   [ERROR] Failed to configure format answer: {response.status_code} - {response.text}")

        # Set up guardrails if provided
        if "guardrails" in config and config["guardrails"]:
            print("Setting up guardrail variables...")
            guardrail_url = f"{self.base_url}/tool-calls/agent/{agent_id}/add-guardrail-variable"
            guardrail_headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "x-rippletide-agent-id": str(agent_id),
                "x-rippletide-conversation-id": str(self.conversation_id),
            }
            for guardrail in config["guardrails"]:
                guardrail_data = {
                    "guardrail_variable_config": {
                        "label": guardrail.get("label", ""),
                        "description": guardrail.get("description", ""),
                    }
                }
                response = requests.post(guardrail_url, headers=guardrail_headers, json=guardrail_data)
                if response.status_code == 200:
                    print(f"   [SUCCESS] Guardrail variable configured: {guardrail.get('label', 'N/A')}")
                else:
                    print(f"   [ERROR] Failed to configure guardrail variable: {response.status_code} - {response.text}")
            print(f"{len(config['guardrails'])} guardrail variables configured")

        print("Agent knowledge setup complete!")

    def chat(self, message: str, conversation_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Send a message to the agent and get a response."""
        if not self.agent_id:
            raise ValueError("Agent must be created before chatting")

        url = f"{self.base_url}/chat/{self.agent_id}"
        conv_id = conversation_id or self.conversation_id

        chat_headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "x-rippletide-agent-id": str(self.agent_id),
            "x-rippletide-conversation-id": str(conv_id),
        }

        response = requests.post(
            url, headers=chat_headers, json={"user_message": message, "conversation_uuid": conv_id}
        )
        response.raise_for_status()
        return response.json()


class RippletideEvalClient:
    """
    Client for creating evaluation agents and evaluating responses.
    Based on starter/rippletide_client/client.py pattern.
    
    Args:
        session_id: Optional session ID for anonymous requests (will be auto-generated if not provided and no api_key)
        api_key: Optional API key for authenticated requests
        base_url: Base URL for the evaluation API (defaults to localhost:3001)
    """
    
    BASE_URL = "http://localhost:3001"

    def __init__(
        self,
        session_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.base_url = (base_url or self.BASE_URL).rstrip('/')
        self.api_key = api_key
        
        # Generate session_id if not provided and no api_key
        if not api_key and not session_id:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id
        
        self.session = requests.Session()
        
        # Set up headers
        if self.api_key:
            self.session.headers.update({
                'x-api-key': self.api_key
            })
        if self.session_id:
            self.session.headers.update({
                'X-Session-Id': self.session_id
            })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    def create_agent(
        self,
        name: str,
        seed: Optional[int] = None,
        num_nodes: int = 100,
        public_url: Optional[str] = None,
        advanced_payload: Optional[Dict[str, str]] = None,
        parent_agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new agent for evaluation.
        
        Args:
            name: Name of the agent
            seed: Seed value for the agent (default: random)
            num_nodes: Number of nodes for the agent (default: 100)
            public_url: Optional public URL for the agent
            advanced_payload: Optional advanced payload configuration
            parent_agent_id: Optional parent agent ID
            
        Returns:
            Dictionary containing the created agent data
        """
        endpoint = '/api/agents/anonymous' if self.session_id and not self.api_key else '/api/agents'
        
        if seed is None:
            seed = random.randint(0, 1000000)
        
        payload = {
            'name': name,
            'seed': seed,
            'numNodes': num_nodes,
            'label': 'eval'
        }
        
        if public_url is not None:
            payload['publicUrl'] = public_url
        if advanced_payload is not None:
            payload['advancedPayload'] = advanced_payload
        if parent_agent_id is not None:
            payload['parentAgentId'] = parent_agent_id
        
        response = self._make_request('POST', endpoint, json=payload)
        return response.json()
    
    def extract_questions_from_pdf(
        self,
        agent_id: str,
        pdf_path: Union[str, Path, BinaryIO]
    ) -> Dict[str, Any]:
        """
        Extract questions and expected answers from a PDF file.
        
        Args:
            agent_id: ID of the agent
            pdf_path: Path to the PDF file or file-like object
            
        Returns:
            Dictionary containing extraction results and Q&A pairs
        """
        endpoint = f'/api/agents/{agent_id}/upload-pdf'
        
        # Handle both file path and file-like object
        if isinstance(pdf_path, (str, Path)):
            with open(pdf_path, 'rb') as f:
                files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
                response = self._make_request('POST', endpoint, files=files)
        else:
            # Assume it's a file-like object
            files = {'file': ('document.pdf', pdf_path, 'application/pdf')}
            response = self._make_request('POST', endpoint, files=files)
        
        return response.json()
    
    def get_test_prompts(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all test prompts (questions and expected answers) for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of test prompts with question and expected answer
        """
        endpoint = f'/api/agents/{agent_id}/test-prompts'
        response = self._make_request('GET', endpoint)
        return response.json()
    
    def chat(
        self,
        agent_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a chat message to an agent and get a response.
        This generates the response internally without using the agent's public URL.
        
        Args:
            agent_id: ID of the agent
            message: Message to send to the agent
            
        Returns:
            Dictionary containing agent response, session ID, etc.
        """
        endpoint = f'/api/agents/{agent_id}/chat'
        payload = {'message': message}
        response = self._make_request('POST', endpoint, json=payload)
        return response.json()
    
    def evaluate(
        self,
        agent_id: str,
        question: str,
        expected_answer: Optional[str] = None,
        answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simple evaluation endpoint - evaluates a question and returns a report.
        
        Args:
            agent_id: ID of the agent
            question: The question to evaluate
            expected_answer: Optional expected answer (will use knowledge base if not provided)
            answer: Optional actual answer to evaluate (if provided, this answer will be evaluated instead of asking the agent)
            
        Returns:
            Dictionary containing evaluation report with label, justification, and facts
        """
        endpoint = f'/api/agents/{agent_id}/evaluate'
        payload = {'question': question}
        if expected_answer is not None:
            payload['expectedAnswer'] = expected_answer
        if answer is not None:
            payload['answer'] = answer
        
        response = self._make_request('POST', endpoint, json=payload)
        return response.json()
