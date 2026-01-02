from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import json

class BaseAgent(ABC):
    """
    Abstract Base Class for TaxoBench Agents.
    Enforces a common interface for all model implementations.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.system_prompt = ""
        self.output_schema = {}
        self.few_shot_examples = []
        self.attachments_path = None

    def set_suite_context(self, instructions: str, output_schema: Dict[str, Any], few_shot_examples: list, attachments_path: str = None):
        """Sets the context for the agent from the test suite."""
        self.system_prompt = instructions
        self.output_schema = output_schema
        self.few_shot_examples = few_shot_examples
        self.attachments_path = attachments_path

    @abstractmethod
    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single question and returns the answer.
        
        Args:
            question_data: The dictionary containing the question, context, options, etc.
            
        Returns:
            A dictionary containing the agent's response, expected to have keys:
            - 'selected_option' (str): "A", "B", "C", or "D"
            - 'required_facts' (List[str]): Technical facts used.
            - 'legal_source' (str): The legal citation.
            - 'reasoning_logic' (str): Explanation.
        """
        pass
