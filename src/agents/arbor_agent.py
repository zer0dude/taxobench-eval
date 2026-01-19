import json
import random
from typing import Dict, Any
from .base import BaseAgent

class ArborAgent(BaseAgent):
    """
    A mock agent simulating the 'Arbor' multi-agent microservice.
    """
    def __init__(self, model_name: str = "arbor-mock-v1"):
        super().__init__(model_name)

    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        # Mock logic matching new schema
        return {
            "selected_option": "A",
            "evidence_ledger": [
                {
                    "evidence_type": "internal_fact",
                    "source": "context_snippet",
                    "quote_anchor": "Factory identifies as cement manufacturer... NACE code C23.51 linked to cement"
                },
                {
                    "evidence_type": "external_source",
                    "source": "ELI:reg_del/2021/2139/oj",
                    "locator": "Annex I | Section 3.7",
                    "version": "OJ L 442, 09.12.2021",
                    "quote_anchor": "Manufacture of cement clinker... associated with NACE code C23.51"
                }
            ],
            "reasoning_logic": "Mock reasoning: The activity clearly falls under manufacture of cement as per the NACE code provided in the context and confirmed by the attachments."
        }
