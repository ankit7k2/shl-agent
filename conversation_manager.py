import json
import os
import re
from typing import List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "shl_catalog.json")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    catalog_data = json.load(f)


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower() if text else "").strip()


def normalize_name(text: str) -> str:
    return re.sub(r"[^a-z0-9+#]+", "", text.lower() if text else "")


catalog_by_normalized = {
    normalize_name(item["name"]): item
    for item in catalog_data
}

normalized_catalog_names = sorted(
    catalog_by_normalized.keys(),
    key=lambda value: len(value),
    reverse=True,
)

NAME_ALIASES = {
    "opq": "Occupational Personality Questionnaire (OPQ32r)",
    "opq32r": "Occupational Personality Questionnaire (OPQ32r)",
    "gsa": "Global Skills Assessment",
    "global skills assessment": "Global Skills Assessment",
}

KEY_LETTER = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Ability & Aptitude": "A",
    "Simulations": "S",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Assessment Exercises": "E",
}

AUTO_REQUIREMENT_ROLE_KEYWORDS = {
    "developer": ["technical"],
    "engineer": ["technical"],
    "programmer": ["technical"],
    "analyst": ["technical"],
}


def map_keys_to_test_type(keys: List[str], name: str = "") -> str:
    norm = normalize_name(name)
    overrides = {
        "occupationalpersonalityquestionaireopq32r": "P",
        "shlverifyinteractiveg+": "A",
        "shlverifyinteractivenumericalreasoning": "A,S",
        "contactcentercallsimulationnew": "S",
        "customerservicephonesimulation": "B,S",
        "entrylevelcustomerservretailcontactcenter": "P,C",
        "globalskillsdevelopmentreport": "D",
        "globalskillsassessment": "C,K",
        "graduatescenarios": "B",
        "dependabilityandsafetyinstrumentdsi": "P",
        "microsoftword365essentialsnew": "K,S",
        "microsoftexcel365new": "K,S",
        "microsoftword365new": "K,S",
    }
    if norm in overrides:
        return overrides[norm]
    letters = []
    seen = set()
    for key in keys or []:
        letter = KEY_LETTER.get(key)
        if letter and letter not in seen:
            letters.append(letter)
            seen.add(letter)
    return ",".join(letters) if letters else "K"


SENIORITY_PATTERNS = {
    "entry": ["entry-level", "entry level", "junior", "graduate", "new hire", "early career"],
    "mid": ["mid-level", "mid level", "mid", "experienced", "associate", "intermediate"],
    "senior": ["senior", "lead", "principal", "director", "executive", "manager", "head"],
}

SENIORITY_MAPPING = {
    "entry": ["Entry-Level", "Graduate"],
    "mid": ["Mid-Professional", "Professional Individual Contributor", "Supervisor"],
    "senior": ["Manager", "Director", "Executive", "Front Line Manager"],
}

YEARS_OF_EXPERIENCE = re.compile(r"\b(\d+)\s*(?:\+?\s*(?:years|yrs|year))\b")

REQUIREMENT_KEYWORDS = {
    "personality": ["Personality & Behavior"],
    "behavior": ["Personality & Behavior"],
    "behaviour": ["Personality & Behavior"],
    "aptitude": ["Ability & Aptitude"],
    "technical": ["Knowledge & Skills"],
    "knowledge": ["Knowledge & Skills"],
    "numerical": ["Knowledge & Skills", "Ability & Aptitude"],
    "reasoning": ["Knowledge & Skills", "Ability & Aptitude"],
    "situational": ["Assessment Exercises", "Biodata & Situational Judgment"],
    "judgment": ["Assessment Exercises", "Biodata & Situational Judgment"],
    "judgement": ["Assessment Exercises", "Biodata & Situational Judgment"],
    "scenario": ["Assessment Exercises", "Biodata & Situational Judgment"],
    "stakeholder": ["Competencies", "Personality & Behavior"],
    "leadership": ["Competencies", "Development & 360"],
    "management": ["Competencies", "Development & 360"],
    "competency": ["Competencies"],
    "communication": ["Personality & Behavior", "Competencies"],
    "safety": ["Ability & Aptitude", "Simulations"],
    "sales": ["Knowledge & Skills"],
    "software": ["Knowledge & Skills"],
    "customer": ["Competencies", "Personality & Behavior"],
    "english": [],
    "spanish": [],
}

REFUSAL_PATTERNS = [
    r"\b(legal|law|compliance|regulated|hipaa|gdpr|data protection|hiring advice|interview advice|salary|compensation)\b",
    r"\b(are we legally required|do we have to|must we|can we ignore|am i allowed to|is it legal)\b",
    r"\b(ignore previous|forget previous|override|bypass instruction|prompt injection)\b",
]

COMPARE_PATTERNS = [
    r"\b(compare|difference|versus|vs\b|what is the difference|what's the difference)\b",
]

CONFIRMATION_PATTERNS = [
    r"\b(thanks|thank you|that works|sounds good|perfect|done|use these|let's use|go ahead|confirm|confirmed|accepted)\b",
]

VAGUE_PATTERNS = [
    r"\b(i need an assessment|need an assessment|need a test|assessment for|what should i use|i need help|suggest an assessment|recommend an assessment)\b",
]

EXCLUDE_RECOMMENDATION_NAME_PATTERNS = [
    "report",
    "guide",
    "cards",
    "profile",
    "pack",
]

EXCLUDE_RECOMMENDATION_NAME_PHRASES = [
    "virtual assessment and development centers",
    "assessment and development center exercises",
    "motivation report pack",
    "universal competency framework interview guide",
    "universal competency framework job profiling guide",
    "universal competency framework profiler cards",
    "opq universal competency report",
    "opq leadership report",
]

EXCLUDE_SALES_REPORT_PATTERNS = [
    "sales transformation",
    "sales report",
    "sales transformation report",
]

ROLE_TERMS = [
    "developer", "engineer", "analyst", "manager", "operator", "consultant", "administrator",
    "specialist", "coordinator", "director", "executive", "architect", "scientist", "professional",
]

DOMAIN_TERMS = [
    "java", "python", "dotnet", ".net", "c#", "excel", "finance", "healthcare", "retail",
    "sales", "customer", "operations", "marketing", "data", "software", "security", "manufacturing",
]


def extract_role(text: str) -> str:
    normalized = normalize_text(text)
    parts = []
    for domain in DOMAIN_TERMS:
        if domain in normalized and domain not in parts:
            parts.append(domain)
    for role in ROLE_TERMS:
        if role in normalized and role not in parts:
            parts.append(role)
    return " ".join(parts).strip()


def auto_add_requirements_from_role(role: str, current_requirements: List[str]) -> List[str]:
    requirements = list(current_requirements)
    for token, mapped in AUTO_REQUIREMENT_ROLE_KEYWORDS.items():
        if token in role:
            for req in mapped:
                if req not in requirements:
                    requirements.append(req)
    return requirements


def match_seniority(text: str) -> str:
    normalized = normalize_text(text)
    for level, patterns in SENIORITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in normalized:
                return level
    years_match = YEARS_OF_EXPERIENCE.search(normalized)
    if years_match:
        years = int(years_match.group(1))
        if years <= 2:
            return "entry"
        if years <= 5:
            return "mid"
        return "senior"
    return ""


def extract_requirements(text: str) -> List[str]:
    normalized = normalize_text(text)
    requirements = []
    for keyword in REQUIREMENT_KEYWORDS:
        if keyword in normalized:
            requirements.append(keyword)
    return list(dict.fromkeys(requirements))


def extract_languages(text: str) -> List[str]:
    normalized = normalize_text(text)
    return [language for token, language in {"spanish": "Spanish", "english": "English"}.items() if token in normalized]


def contains_refusal_signal(text: str) -> bool:
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized) for pattern in REFUSAL_PATTERNS)


def is_comparison_request(text: str) -> bool:
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized) for pattern in COMPARE_PATTERNS)


def is_confirmation(text: str) -> bool:
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized) for pattern in CONFIRMATION_PATTERNS)


def find_catalog_names(text: str) -> List[str]:
    normalized = normalize_text(text)
    found = []
    for alias, canonical in NAME_ALIASES.items():
        if alias in normalized and normalize_name(canonical) in catalog_by_normalized:
            found.append(normalize_name(canonical))
    for name in normalized_catalog_names:
        if name in normalize_name(text):
            found.append(name)
    return list(dict.fromkeys(found))


def compare_items(names: List[str]) -> str:
    items = [catalog_by_normalized[name] for name in names if name in catalog_by_normalized]
    if len(items) < 2:
        return "I can compare SHL assessments if you provide two exact catalog names or common abbreviations like OPQ and GSA."
    left, right = items[0], items[1]
    left_type = map_keys_to_test_type(left.get("keys", []), left["name"])
    right_type = map_keys_to_test_type(right.get("keys", []), right["name"])
    left_keys = ", ".join(left.get("keys", [])) or "no specific category"
    right_keys = ", ".join(right.get("keys", [])) or "no specific category"
    return (
        f"{left['name']} is a SHL assessment that maps to {left_type} and focuses on {left_keys}. "
        f"Catalog description: {left['description']} "
        f"In contrast, {right['name']} maps to {right_type} and focuses on {right_keys}. "
        f"Catalog description: {right['description']}"
    )


def is_recommendable(item: dict) -> bool:
    name = normalize_text(item.get("name", ""))
    if any(phrase in name for phrase in EXCLUDE_RECOMMENDATION_NAME_PHRASES):
        return False
    if any(pattern in name for pattern in EXCLUDE_RECOMMENDATION_NAME_PATTERNS):
        return False
    return True


def is_sales_report(item: dict) -> bool:
    name = normalize_text(item.get("name", ""))
    return any(pattern in name for pattern in EXCLUDE_SALES_REPORT_PATTERNS)


def build_context(messages: List[dict]) -> dict:
    context = {
        "role": "",
        "seniority": "",
        "requirements": [],
        "languages": [],
        "exclusions": [],
    }
    for message in messages:
        if message.get("role") != "user":
            continue
        text = message.get("content", "")
        if not context["role"]:
            role_text = extract_role(text)
            if role_text:
                context["role"] = role_text
        if not context["seniority"]:
            seniority = match_seniority(text)
            if seniority:
                context["seniority"] = seniority
        context["requirements"].extend(extract_requirements(text))
        context["languages"].extend(extract_languages(text))
        exclusions = re.findall(r"\bno\s+(personality|aptitude|technical|leadership|situational|numerical|sales|management|behavior)\b", normalize_text(text))
        context["exclusions"].extend(exclusions)
    context["requirements"] = list(dict.fromkeys(context["requirements"]))
    if context["role"]:
        context["requirements"] = auto_add_requirements_from_role(context["role"], context["requirements"])
    context["languages"] = list(dict.fromkeys(context["languages"]))
    context["exclusions"] = list(dict.fromkeys(context["exclusions"]))
    return context


def score_item(item: dict, context: dict) -> int:
    if not is_recommendable(item):
        return -999
    score = 0
    item_text = normalize_text(" ".join([
        item.get("name", ""),
        item.get("description", ""),
        " ".join(item.get("keys", [])),
        " ".join(item.get("job_levels", [])),
    ]))
    if context["languages"]:
        item_languages = [lang.lower() for lang in item.get("languages", [])]
        if not any(lang.lower() in item_languages for lang in context["languages"]):
            return -999
        score += 10
    if context["seniority"]:
        senior_levels = [level.lower() for level in SENIORITY_MAPPING.get(context["seniority"], [])]
        if any(level.lower() in normalize_text(" ".join(item.get("job_levels", []))) for level in senior_levels):
            score += 25
    if context["role"]:
        for token in context["role"].split():
            if token and token in item_text:
                score += 10
    category_match = False
    for requirement in context["requirements"]:
        mapped = REQUIREMENT_KEYWORDS.get(requirement, [])
        if mapped and any(category in item.get("keys", []) for category in mapped):
            category_match = True
            score += 20
        if requirement in item_text:
            category_match = True
            score += 10
    if context["requirements"] and not category_match:
        score -= 5
    if item.get("keys") and category_match:
        score += 5
    if any(exclusion in normalize_text(" ".join(item.get("keys", []))) for exclusion in context["exclusions"]):
        return -999
    if is_sales_report(item) and "sales" not in context["requirements"]:
        score -= 20
    return score


def build_shortlist(context: dict) -> List[dict]:
    scored = []
    for item in catalog_data:
        score = score_item(item, context)
        if score >= 0:
            scored.append((score, item))
    if not scored:
        return []
    scored.sort(key=lambda pair: (pair[0], pair[1].get("name", "")), reverse=True)
    recommendations = []
    for _, item in scored:
        if len(recommendations) >= 10:
            break
        recommendations.append({
            "name": item["name"],
            "url": item["link"],
            "test_type": map_keys_to_test_type(item.get("keys", []), item["name"]),
        })
    return recommendations


def handle_chat(messages: List[dict]) -> dict:
    user_texts = [msg["content"] for msg in messages if msg.get("role") == "user"]
    last_user_text = user_texts[-1] if user_texts else ""

    if contains_refusal_signal(last_user_text):
        return {
            "reply": "I can only answer questions about SHL assessments in the catalog. For legal or compliance questions, please consult your legal team.",
            "recommendations": [],
            "end_of_conversation": False,
        }

    if is_comparison_request(last_user_text):
        names = find_catalog_names(last_user_text)
        if len(names) >= 2:
            return {
                "reply": compare_items(names[:2]),
                "recommendations": [],
                "end_of_conversation": False,
            }

    context = build_context(messages)

    missing = []
    if not context["role"]:
        missing.append("role")
    if not context["seniority"]:
        missing.append("seniority")
    if not context["requirements"]:
        missing.append("assessment type")

    if missing:
        prompts = []
        if "role" in missing:
            prompts.append("What role are you hiring for, including domain or specialty?")
        if "seniority" in missing:
            prompts.append("What seniority level is the role? For example: entry-level, mid-level, or senior.")
        if "assessment type" in missing:
            prompts.append("What type of assessment do you need? For example: technical knowledge, personality, situational judgment, or stakeholder skills.")
        return {
            "reply": " ".join(prompts),
            "recommendations": [],
            "end_of_conversation": False,
        }

    recommendations = build_shortlist(context)
    if not recommendations:
        return {
            "reply": "I reviewed the SHL catalog but I need a bit more detail to provide a grounded shortlist. Please clarify the role, seniority, or assessment type.",
            "recommendations": [],
            "end_of_conversation": False,
        }

    if is_confirmation(last_user_text):
        return {
            "reply": "Great, I’ve locked in the recommended SHL assessments for your request.",
            "recommendations": recommendations,
            "end_of_conversation": True,
        }

    role_desc = f"a {context['seniority']} {context['role']}" if context['role'] and context['seniority'] else "your request"
    requirement_desc = f" with {', '.join(context['requirements'])}" if context['requirements'] else ""
    count = len(recommendations)
    item_label = "assessment" if count == 1 else "assessments"
    return {
        "reply": f"Got it. Here are {count} {item_label} that fit {role_desc}{requirement_desc}.",
        "recommendations": recommendations,
        "end_of_conversation": False,
    }
