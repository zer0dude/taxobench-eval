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

    def get_attachments_text(self, question_id: str) -> str:
        """
        Retrieves text from all attachments associated with a specific question.
        Attachments are expected to be in: self.attachments_path / question_id / <files>
        """
        if not self.attachments_path:
            return ""

        target_dir = Path(self.attachments_path) / question_id
        if not target_dir.exists():
            return ""

        combined_text = []
        for file_path in target_dir.iterdir():
            if file_path.suffix.lower() == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    combined_text.append(f"--- Attachment: {file_path.name} ---\n{text}")
                except Exception as e:
                    combined_text.append(f"--- Attachment: {file_path.name} (Error reading PDF: {e}) ---")
            
            elif file_path.suffix.lower() == ".docx":
                try:
                    import docx
                    doc = docx.Document(file_path)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    combined_text.append(f"--- Attachment: {file_path.name} ---\n{text}")
                except Exception as e:
                    combined_text.append(f"--- Attachment: {file_path.name} (Error reading DOCX: {e}) ---")

        return "\n\n".join(combined_text)

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
