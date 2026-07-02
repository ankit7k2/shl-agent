import traceback
import sys
import dotenv
dotenv.load_dotenv(override=True)

from conversation_manager import generate_llm_response

messages = [
    {
        "role": "user",
        "content": (
            "We're hiring bilingual healthcare admin staff in South Texas. "
            "They handle patient records and need to be assessed in Spanish. "
            "HIPAA compliance is critical. What assessments work?"
        )
    },
    {
        "role": "assistant",
        "content": (
            "We have HIPAA (Security), Medical Terminology (New), "
            "Microsoft Word 365 - Essentials (New) in English, "
            "and DSI and OPQ32r in Spanish. Which works better?"
        )
    },
    {
        "role": "user",
        "content": (
            "Are we legally required under HIPAA to test all staff "
            "who touch patient records? And does this SHL test satisfy that requirement?"
        )
    }
]

try:
    r = generate_llm_response(messages)
    print("SUCCESS:", r)
except Exception as e:
    print("ERROR:")
    traceback.print_exc()
