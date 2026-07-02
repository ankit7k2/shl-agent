import dotenv
import os
from conversation_manager import handle_chat

# Load environment variables
dotenv.load_dotenv(override=True)

def run_test_scenario(title, messages):
    print("=" * 60)
    print(f"SCENARIO: {title}")
    print("=" * 60)
    for msg in messages:
        print(f"[{msg['role'].upper()}]: {msg['content']}")
    print("-" * 60)
    
    response = handle_chat(messages)
    
    print(f"[REPLY]:\n{response.get('reply')}")
    print(f"[RECOMMENDATIONS]: {response.get('recommendations')}")
    print(f"[END OF CONVERSATION]: {response.get('end_of_conversation')}")
    print("\n")
    return response

# Test 1: Vague query (Clarify)
run_test_scenario(
    "Vague Query - Senior Leadership",
    [
        {"role": "user", "content": "We need a solution for senior leadership."}
    ]
)

# Test 2: Comparison
run_test_scenario(
    "Comparison - DSI vs Safety & Dependability 8.0",
    [
        {"role": "user", "content": "We're hiring plant operators for a chemical facility. Safety is absolute top priority. What do you recommend?"},
        {"role": "assistant", "content": "I recommend Dependability and Safety Instrument (DSI) and Manufac. & Indust. - Safety & Dependability 8.0, and Workplace Health and Safety (New)."},
        {"role": "user", "content": "What's the difference between the DSI and the Safety & Dependability 8.0?"}
    ]
)

# Test 3: Refusal / Staying in scope
run_test_scenario(
    "Out of Scope - HIPAA Legal Compliance",
    [
        {"role": "user", "content": "We're hiring bilingual healthcare admin staff in South Texas — they handle patient records and need to be assessed in Spanish. HIPAA compliance is critical. What assessments work?"},
        {"role": "assistant", "content": "We have HIPAA (Security), Medical Terminology (New), Microsoft Word 365 - Essentials (New) in English, and DSI and OPQ32r in Spanish. Which works better?"},
        {"role": "user", "content": "Are we legally required under HIPAA to test all staff who touch patient records? And does this SHL test satisfy that requirement?"}
    ]
)

# Test 4: Refinement
run_test_scenario(
    "Refinement - Adding Situational Judgement for Graduates",
    [
        {"role": "user", "content": "Hiring graduate financial analysts. We need numerical reasoning and a finance knowledge test."},
        {"role": "assistant", "content": "For graduate-level financial analysts, I recommend:\n1. SHL Verify Interactive – Numerical Reasoning\n2. Financial Accounting (New)\n3. Basic Statistics (New)\n4. Occupational Personality Questionnaire OPQ32r"},
        {"role": "user", "content": "Good. Can you also add a situational judgement element — work-context decision making for graduates?"}
    ]
)
