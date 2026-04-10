"""
Multi-language Technical Glossary for SOC Tutor.
Helps maintain consistency across ES, PT, and EN.
"""

TECHNICAL_GLOSSARY = {
    "Phishing": {
        "es": "Phishing",
        "pt": "Phishing",
        "en": "Phishing",
        "protect": True
    },
    "Lateral Movement": {
        "es": "Movimiento Lateral",
        "pt": "Movimentação Lateral",
        "en": "Lateral Movement",
        "protect": False
    },
    "Ransomware": {
        "es": "Ransomware",
        "pt": "Ransomware",
        "en": "Ransomware",
        "protect": True
    },
    "Endpoint Detection and Response": {
        "es": "Endpoint Detection and Response (EDR)",
        "pt": "Detecção e Resposta de Endpoint (EDR)",
        "en": "Endpoint Detection and Response (EDR)",
        "protect": False
    },
    "Indicators of Compromise": {
        "es": "Indicadores de Compromiso (IoCs)",
        "pt": "Indicadores de Comprometimento (IoCs)",
        "en": "Indicators of Compromise (IoCs)",
        "protect": False
    }
}

def get_glossary_prompt_fragment(language: str) -> str:
    """Returns a string to be injected in prompts to guide terminology."""
    fragment = "TECHNICAL TERMINOLOGY GUIDELINES:\n"
    for term, trans in TECHNICAL_GLOSSARY.items():
        if trans["protect"]:
            fragment += f"- Keep '{term}' as is.\n"
        else:
            fragment += f"- Use '{trans.get(language, term)}' for '{term}'.\n"
    return fragment
