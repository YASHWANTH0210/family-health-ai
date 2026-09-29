import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class Agent:
    """Base class for all agents."""
    
    def __init__(self, name, model="nano"):
        self.name = name
        self.api_key = os.getenv("NEBIUS_API_KEY")
        self.endpoint = os.getenv("NEBIUS_API_ENDPOINT")
        
        if model == "nano":
            self.model = os.getenv("NEMOTRON_NANO")
        elif model == "ultra":
            self.model = os.getenv("NEMOTRON_ULTRA")
        else:
            self.model = model
        
        if not self.api_key:
            raise ValueError("NEBIUS_API_KEY not set in .env file")
    
    def call_model(self, prompt, max_tokens=500):
        """Call Nemotron model via Nebius API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            if "content" in data and len(data["content"]) > 0:
                return data["content"][0].get("text", "")
            else:
                return f"Error: Unexpected response format: {data}"
        
        except requests.exceptions.RequestException as e:
            return f"Error calling Nebius API: {str(e)}"
    
    def run(self, input_data):
        """Agents override this method."""
        raise NotImplementedError("Subclasses must implement run()")
    
    def think(self, question):
        """Helper: ask the model to think through something step by step."""
        prompt = f"""Think through the following step by step. Show your reasoning:

{question}

Answer:"""
        return self.call_model(prompt, max_tokens=800)
