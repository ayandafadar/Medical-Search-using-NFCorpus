import re
from typing import Dict, Set

# Curated transparent dictionary of medical synonyms & abbreviations
MEDICAL_SYNONYMS: Dict[str, Set[str]] = {
    "hypertension": {"high blood pressure"},
    "hypotension": {"low blood pressure"},
    "myocardial infarction": {"heart attack"},
    "heart attack": {"myocardial infarction"},
    "diabetes": {"diabetes mellitus", "hyperglycemia"},
    "hyperglycemia": {"high blood sugar"},
    "hypoglycemia": {"low blood sugar"},
    "neoplasm": {"cancer", "tumor"},
    "cancer": {"neoplasm", "carcinoma"},
    "renal": {"kidney"},
    "hepatic": {"liver"},
    "hepato": {"liver"},
    "pulmonary": {"lung"},
    "cardiac": {"heart"},
    "cephalea": {"headache"},
    "analgesic": {"pain reliever", "painkiller"},
    "antipyretic": {"fever reducer"},
    "covid": {"coronavirus", "sars-cov-2"},
    "stroke": {"cerebrovascular accident"},
}


class MedicalExpansionService:
    """Modular service for expanding medical queries with verified synonyms."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def expand_query(self, query: str) -> str:
        """
        Expand a medical query by appending verified synonyms while keeping original terms intact.
        Returns expanded query string.
        """
        if not self.enabled or not query or not query.strip():
            return query.strip()

        original_query = query.strip()
        lower_query = original_query.lower()
        added_synonyms: Set[str] = set()

        # Check multi-word phrases first
        for phrase, synonyms in MEDICAL_SYNONYMS.items():
            if " " in phrase and phrase in lower_query:
                for syn in synonyms:
                    if syn not in lower_query:
                        added_synonyms.add(syn)

        # Check single word tokens
        words = re.findall(r"\b[a-zA-Z]{3,}\b", lower_query)
        for word in words:
            if word in MEDICAL_SYNONYMS:
                for syn in MEDICAL_SYNONYMS[word]:
                    if syn not in lower_query:
                        added_synonyms.add(syn)

        if not added_synonyms:
            return original_query

        expanded_str = f"{original_query} ({' OR '.join(sorted(list(added_synonyms)))})"
        return expanded_str
