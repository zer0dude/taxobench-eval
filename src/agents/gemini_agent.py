import json
import os
from typing import Dict, Any
from google import genai
from google.genai import types
from .base import BaseAgent
from langsmith import traceable

class GeminiAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initializes the Gemini agent using the new google-genai SDK.
        """
        super().__init__(model_name)
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def _construct_system_prompt(self) -> str:
        prompt = self.system_prompt
        if self.few_shot_examples:
            prompt += "\n\nHere are some examples of the expected output format:\n"
            for example in self.few_shot_examples:
                 prompt += f"\nInput: {json.dumps(example['input'])}\nOutput: {json.dumps(example['output'])}\n"
        return prompt

    @traceable(run_type="llm", name="GeminiAgent")
    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answers a question using Google's Gemini model.
        """
        user_prompt = (
            f"{self._construct_system_prompt()}\n\n"
            f"Context: {question_data.get('context_snippet')}\n"
            f"Context: {question_data.get('context_snippet')}\n"
            f"Question: {question_data.get('question_text')}\n"
            "Options:\n"
            f"A: {question_data['options']['A']}\n"
            f"B: {question_data['options']['B']}\n"
            f"C: {question_data['options']['C']}\n"
            f"D: {question_data['options']['D']}\n"
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=self.output_schema # Passing the schema directly to Gemini
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
             return {
                "selected_option": "D",
                "required_facts": [],
                "legal_source": "None",
                "reasoning_logic": f"Error: {str(e)}"
            }
