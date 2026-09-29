import sys
sys.path.insert(0, '/home/claude')

from agent import Agent
from memory import Memory

class QuestionReasonerAgent(Agent):
    """Answers health questions by reasoning through available information."""
    
    def __init__(self):
        super().__init__("QuestionReasoner", model="ultra")  # Use Ultra for reasoning
        self.memory = Memory()
    
    def run(self, person_name, query):
        """
        Answer a health question by reasoning step by step.
        Returns: {"answer": "...", "sources": [...], "confidence": "high/medium/low"}
        """
        
        person = self.memory.get_person(person_name)
        if not person:
            return {
                "answer": f"Person '{person_name}' not found.",
                "sources": [],
                "confidence": "low"
            }
        
        person_id = person["id"]
        
        # Search all records for relevant information
        relevant_records = self.memory.search_records(person_id, query, top_k=5)
        
        context = "\n".join([
            f"- [{s['similarity']:.2f}] {s['content']}"
            for s in relevant_records
        ])
        
        # Get conditions
        conditions = ", ".join(person["conditions"]) if person["conditions"] else "None recorded"
        
        # Build reasoning prompt
        prompt = f"""You are a health information assistant helping understand medical information for {person_name}.

Person's profile:
- Relationship: {person['relationship']}
- Age: {person['age']}
- Known conditions: {conditions}

Relevant information from their health records:
{context if context else "No directly relevant records found."}

Question: {query}

Think through this step by step:
1. What information do we have about this person?
2. How does the question relate to their health profile?
3. What can we infer from their records?
4. What should we NOT assume?

Provide a thoughtful answer based ONLY on the available information.
If you don't have enough information, say so.

Format your response as:
ANSWER: [your answer]
SOURCES: [which records you used, or "None"]
CONFIDENCE: [high/medium/low - how confident are you?]"""
        
        response = self.call_model(prompt, max_tokens=600)
        
        # Parse response
        answer = ""
        sources = []
        confidence = "medium"
        
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            if line.startswith("ANSWER:"):
                current_section = "answer"
                answer = line.replace("ANSWER:", "").strip()
            elif line.startswith("SOURCES:"):
                current_section = "sources"
                sources_text = line.replace("SOURCES:", "").strip()
                if sources_text.lower() != "none":
                    sources = [s.strip() for s in sources_text.split(",")]
            elif line.startswith("CONFIDENCE:"):
                current_section = "confidence"
                conf_text = line.replace("CONFIDENCE:", "").strip().lower()
                if "high" in conf_text:
                    confidence = "high"
                elif "low" in conf_text:
                    confidence = "low"
                else:
                    confidence = "medium"
            elif current_section:
                if current_section == "answer":
                    answer += " " + line
                elif current_section == "sources" and line.strip() and not line.startswith("CONFIDENCE"):
                    sources.append(line.strip())
        
        return {
            "answer": answer.strip(),
            "sources": sources,
            "confidence": confidence
        }
