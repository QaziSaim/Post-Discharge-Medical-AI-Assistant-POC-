from patient_lookup import load_patient_data, find_patient_by_name
import random

def generate_followup_instructions(report):
    return [
        f"Are u taking your medications as prescribed: {', '.join(report['medications'])}?",
        f"Are u following your dietary restrictions: {report['dietary_restrictions']}?",
        f"Have u noticed any warning signs like {report['warning_signs']}?",
        f"Have u scheduled your follow-up: {report['follow_up']}?"
    ]

def is_medical_query(user_input):
    medical_keywords = ["pain", "swelling", "urine", "dizzy", "blood", "symptoms", "medicine", "medication", "side effects"]
    return any(word in user_input.lower() for word in medical_keywords)

def run_receptionist():
    data = load_patient_data("patient_reports.json")

    print("Receptionist Agent: Hello! I'm your AI care assistant. What's your name?")
    name = input("You: ")

    result = find_patient_by_name(name, data)

    if isinstance(result, str):
        print(f"Receptionist Agent: {result}")
        return
    
    if isinstance(result, list):
        print("Multiple patients found. Please be more specfic.")
        return
    
    report = result

    print(f"\nReceptionist Agent: Hi {report['patient_name']}! i found your discharge report.")
    print(f"Diagnosis: {report['primary_diagnosis']}")
    print("Let me ask u few questions about your recovery:\n")

    questions = generate_followup_instructions(report)
    for q in questions:
        print(q)
        answer = input("You: ")

        if is_medical_query(answer):
            print("Following your concern to our Clinical AI Agent....\n")
            return answer
        
        print("\nThank you for checking in! You seem to be on the right track.")

if __name__ == "__main__":
    run_receptionist()