#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/claude')

from coordinator import Coordinator

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     FAMILY HEALTH INTELLIGENCE SYSTEM (Week 1 Prototype)      ║
║                    Powered by Nebius + NVIDIA                 ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def print_menu():
    print("""
COMMANDS:
  add-person <name> <relationship> <age>  -- Add a family member
  add-record <person> <type> <content>    -- Add a health record (type: medication, lab, condition, note)
  ask <person> <question>                 -- Ask a question about someone
  list-people                             -- Show all family members
  list-records <person>                   -- Show all records for someone
  demo                                    -- Run a demo
  help                                    -- Show this menu
  exit                                    -- Exit
    """)

def main():
    print_banner()
    coordinator = Coordinator()
    
    print("Welcome! Let's set up your family health records.")
    print("Type 'demo' to see a quick example, or 'help' for commands.\n")
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            
            if command == "help":
                print_menu()
            
            elif command == "exit":
                print("Goodbye!")
                break
            
            elif command == "demo":
                run_demo(coordinator)
            
            elif command == "add-person":
                # Parse: add-person <name> <relationship> <age>
                args = user_input[11:].strip().split()  # Remove "add-person "
                if len(args) >= 2:
                    name = args[0]
                    relationship = args[1]
                    age = int(args[2]) if len(args) > 2 else None
                    coordinator.add_person(name, relationship, age)
                else:
                    print("Usage: add-person <name> <relationship> [age]")
            
            elif command == "add-record":
                # Parse: add-record <person> <type> <content>
                rest = user_input[11:].strip()  # Remove "add-record "
                parts = rest.split(maxsplit=2)
                if len(parts) >= 3:
                    person = parts[0]
                    record_type = parts[1]
                    content = parts[2]
                    coordinator.add_record(person, record_type, content)
                else:
                    print("Usage: add-record <person> <type> <content>")
            
            elif command == "ask":
                # Parse: ask <person> <question>
                rest = user_input[4:].strip()  # Remove "ask "
                parts = rest.split(maxsplit=1)
                if len(parts) >= 2:
                    person = parts[0]
                    question = parts[1]
                    print("\n⏳ Processing query...\n")
                    result = coordinator.process_query(person, question)
                    print("\n" + "="*60)
                    print(result["final_answer"])
                    print("="*60)
                else:
                    print("Usage: ask <person> <question>")
            
            elif command == "list-people":
                coordinator.list_people()
            
            elif command == "list-records":
                if len(parts) > 1:
                    person = parts[1]
                    coordinator.list_records(person)
                else:
                    print("Usage: list-records <person>")
            
            else:
                print("Unknown command. Type 'help' for options.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def run_demo(coordinator):
    """Run a quick demo."""
    print("\n🎬 Running demo...\n")
    
    # Add a family member
    print("1. Adding family member 'Mom'...")
    coordinator.add_person("Mom", "Mother", 68, ["Hypertension", "Type 2 Diabetes"])
    
    # Add some records
    print("\n2. Adding health records...")
    coordinator.add_record("Mom", "medication", "Lisinopril 10mg daily for blood pressure")
    coordinator.add_record("Mom", "medication", "Metformin 500mg twice daily for diabetes")
    coordinator.add_record("Mom", "lab", "Blood glucose 145 mg/dL (fasting)")
    coordinator.add_record("Mom", "lab", "Blood pressure 138/88 mmHg")
    coordinator.add_record("Mom", "note", "Complained of dizziness yesterday evening")
    
    # Ask a question
    print("\n3. Asking a question...")
    question = "Mom mentioned feeling dizzy. Could it be related to her medications?"
    print(f"   Question: '{question}'\n")
    
    result = coordinator.process_query("Mom", question)
    
    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(result["final_answer"])
    print("="*60)
    
    print("\n✓ Demo complete! Now try your own queries with 'ask <person> <question>'")

if __name__ == "__main__":
    main()
