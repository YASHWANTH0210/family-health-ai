import sys
sys.path.insert(0, '/home/claude')

from agent import Agent
import json

class RouterAgent(Agent):
    """Routes user queries to appropriate sub-agents."""
    
    def __init__(self):
        super().__init__("Router", model="nano")
    
    def run(self, user_input, person_name):
        """
        Analyze user input and decide which agents to invoke.
        Returns: {"agents": ["medication_manager", "appointment_scheduler"], "reasoning": "..."}
        """
        
        prompt = f"""You are a router that directs health queries to specialized agents.

User is asking about: {person_name}
Query: {user_input}

Available agents:
1. medication_manager - handles medications, drug interactions, side effects, refills
2. appointment_scheduler - manages doctor appointments, follow-ups, schedules
3. health_trend_analyzer - analyzes patterns over time, spot trends
4. question_reasoner - answers general health questions by reasoning

Output a JSON response with:
{{"agents": ["agent1", "agent2"], "reasoning": "why these agents", "urgency": "low/medium/high"}}

Only include agents that are relevant. Don't include all agents."""
        
        response = self.call_model(prompt, max_tokens=300)
        
        # Parse response
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return result
            else:
                return {
                    "agents": ["question_reasoner"],
                    "reasoning": "Could not parse routing, defaulting to question_reasoner",
                    "urgency": "low"
                }
        except json.JSONDecodeError:
            return {
                "agents": ["question_reasoner"],
                "reasoning": "JSON parse error, defaulting to question_reasoner",
                "urgency": "low"
            }
