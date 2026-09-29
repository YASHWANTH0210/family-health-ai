import sys
sys.path.insert(0, '/home/claude')

from agent import Agent
from memory import Memory

class MedicationManagerAgent(Agent):
    """Manages medications, tracks interactions, and alerts on refills."""
    
    def __init__(self):
        super().__init__("MedicationManager", model="ultra")  # Use Ultra for reasoning
        self.memory = Memory()
    
    def run(self, person_name, query):
        """
        Main entry point. Analyzes medication questions.
        Returns: {"answer": "...", "alerts": [...], "reasoning": "..."}
        """
        
        person = self.memory.get_person(person_name)
        if not person:
            return {"answer": f"Person '{person_name}' not found in memory.", "alerts": [], "reasoning": ""}
        
        person_id = person["id"]
        
        # Get all medications
        medications = self.memory.get_all_records(person_id, "medication")
        med_text = "\n".join([f"- {m['content']} (recorded {m['date']})" for m in medications])
        
        # Search for relevant info
        similar = self.memory.search_records(person_id, query, top_k=3)
        context = "\n".join([f"- {s['content']}" for s in similar])
        
        # Build reasoning prompt
        prompt = f"""You are a medication safety specialist. 
You are helping manage medications for {person_name} ({person['relationship']}, age {person['age']}).

Current medications:
{med_text if med_text else "No medications recorded yet."}

Relevant past records:
{context if context else "None found."}

User query: {query}

Think through this step by step:
1. What medications are involved?
2. Are there any known interactions?
3. What is the person's age and conditions?
4. Are there any safety concerns?

Provide a clear answer and list any alerts or concerns.

Format your response as:
ANSWER: [main answer]
ALERTS: [list any concerns, or "None"]
REASONING: [brief explanation of your logic]"""
        
        response = self.call_model(prompt, max_tokens=600)
        
        # Parse response
        answer = ""
        alerts = []
        reasoning = ""
        
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            if line.startswith("ANSWER:"):
                current_section = "answer"
                answer = line.replace("ANSWER:", "").strip()
            elif line.startswith("ALERTS:"):
                current_section = "alerts"
                alerts_text = line.replace("ALERTS:", "").strip()
                if alerts_text.lower() != "none":
                    alerts = [a.strip() for a in alerts_text.split(",")]
            elif line.startswith("REASONING:"):
                current_section = "reasoning"
                reasoning = line.replace("REASONING:", "").strip()
            elif current_section:
                if current_section == "answer":
                    answer += " " + line
                elif current_section == "alerts" and line.strip():
                    alerts.append(line.strip())
                elif current_section == "reasoning":
                    reasoning += " " + line
        
        return {
            "answer": answer.strip(),
            "alerts": alerts,
            "reasoning": reasoning.strip()
        }
    
    def check_interaction(self, person_name, drug1, drug2):
        """Check if two drugs interact."""
        prompt = f"""Do these two medications interact? Be specific.

Drug 1: {drug1}
Drug 2: {drug2}

List any known interactions or concerns, or say "No known interactions."

Answer:"""
        
        return self.call_model(prompt, max_tokens=300)
    
    def suggest_refills(self, person_name):
        """Suggest medications that might need refills soon."""
        person = self.memory.get_person(person_name)
        if not person:
            return []
        
        medications = self.memory.get_all_records(person["id"], "medication")
        
        if not medications:
            return []
        
        # For now, just list all medications (in a real system, track refill dates)
        return medications
