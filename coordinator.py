import sys
sys.path.insert(0, '/home/claude')

from agents.router_agent import RouterAgent
from agents.medication_agent import MedicationManagerAgent
from agents.question_reasoner_agent import QuestionReasonerAgent
from memory import Memory

class Coordinator:
    """Orchestrates multiple agents to answer health queries."""
    
    def __init__(self):
        self.router = RouterAgent()
        self.medication_agent = MedicationManagerAgent()
        self.question_reasoner = QuestionReasonerAgent()
        self.memory = Memory()
    
    def process_query(self, person_name, user_input):
        """
        Process a user query by routing to appropriate agents.
        Returns: {"query": "...", "agents_used": [...], "results": {...}, "final_answer": "..."}
        """
        
        print(f"\n[COORDINATOR] Processing query for {person_name}: '{user_input}'")
        
        # Step 1: Route the query
        print("[COORDINATOR] Routing query...")
        routing_result = self.router.run(user_input, person_name)
        print(f"[COORDINATOR] Router decision: {routing_result}")
        
        agents_to_use = routing_result.get("agents", ["question_reasoner"])
        reasoning = routing_result.get("reasoning", "")
        urgency = routing_result.get("urgency", "low")
        
        # Step 2: Invoke agents
        print(f"[COORDINATOR] Invoking agents: {agents_to_use}")
        results = {}
        
        if "medication_manager" in agents_to_use:
            print("[MEDICATION_AGENT] Running...")
            med_result = self.medication_agent.run(person_name, user_input)
            results["medication_manager"] = med_result
            print(f"[MEDICATION_AGENT] Result: {med_result.get('answer', '')[:100]}...")
        
        if "question_reasoner" in agents_to_use:
            print("[QUESTION_REASONER] Running...")
            qa_result = self.question_reasoner.run(person_name, user_input)
            results["question_reasoner"] = qa_result
            print(f"[QUESTION_REASONER] Result: {qa_result.get('answer', '')[:100]}...")
        
        # Step 3: Synthesize results
        print("[COORDINATOR] Synthesizing results...")
        final_answer = self._synthesize(person_name, user_input, results, routing_result)
        
        return {
            "query": user_input,
            "agents_used": agents_to_use,
            "routing_reasoning": reasoning,
            "urgency": urgency,
            "detailed_results": results,
            "final_answer": final_answer
        }
    
    def _synthesize(self, person_name, query, agent_results, routing_info):
        """Combine results from multiple agents into a coherent answer."""
        
        # For now, simple synthesis
        # In production, we'd use another agent to synthesize
        
        synthesis = []
        
        if "medication_manager" in agent_results:
            med_result = agent_results["medication_manager"]
            synthesis.append(f"**Medication Info**: {med_result.get('answer', '')}")
            if med_result.get("alerts"):
                synthesis.append(f"⚠️ **Alerts**: {', '.join(med_result['alerts'])}")
        
        if "question_reasoner" in agent_results:
            qa_result = agent_results["question_reasoner"]
            synthesis.append(f"**Answer**: {qa_result.get('answer', '')}")
            if qa_result.get("confidence"):
                synthesis.append(f"*Confidence: {qa_result['confidence']}*")
        
        return "\n\n".join(synthesis)
    
    def add_person(self, name, relationship, age=None, conditions=None):
        """Add a family member to memory."""
        person_id = self.memory.add_person(name, relationship, age, conditions)
        if person_id:
            print(f"✓ Added {name} ({relationship}) to memory.")
            return person_id
        else:
            print(f"✗ {name} already exists in memory.")
            return None
    
    def add_record(self, person_name, record_type, content, date=None):
        """Add a health record."""
        person = self.memory.get_person(person_name)
        if not person:
            print(f"✗ Person '{person_name}' not found. Add them first.")
            return False
        
        self.memory.add_record(person["id"], record_type, content, date)
        print(f"✓ Added {record_type} for {person_name}.")
        return True
    
    def list_people(self):
        """List all family members."""
        # For now, print a simple message
        print("(Family member listing coming in expanded version)")
    
    def list_records(self, person_name):
        """List records for a person."""
        person = self.memory.get_person(person_name)
        if not person:
            print(f"✗ Person '{person_name}' not found.")
            return
        
        records = self.memory.get_all_records(person["id"])
        if records:
            print(f"\nRecords for {person_name}:")
            for r in records:
                print(f"  - [{r['type']}] {r['content'][:60]}... ({r['date']})")
        else:
            print(f"No records for {person_name}.")
