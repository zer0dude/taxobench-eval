import json
import os
from typing import Dict, Any
from openai import OpenAI
from .base import BaseAgent
from langsmith import traceable

class GPT4oAgent(BaseAgent):
    def __init__(self, model_name: str = "gpt-4o"):
        super().__init__(model_name)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _construct_system_prompt(self) -> str:
        prompt = self.system_prompt
        if self.few_shot_examples:
            prompt += "\n\nHere are some examples of the expected output format:\n"
            for example in self.few_shot_examples:
                 prompt += f"\nInput: {json.dumps(example['input'])}\nOutput: {json.dumps(example['output'])}\n"
        return prompt

    @traceable(run_type="llm", name="GPT4oAgent")
    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answers a question using OpenAI's GPT-4o model.
        """
        attachments_text = self.get_attachments_text(question_data.get('question_id'))
        
        user_prompt = (
            f"Context: {question_data.get('context_snippet')}\n"
            f"Attachments: {attachments_text}\n"
            f"Question: {question_data.get('question_text')}\n"
            "Options:\n"
            f"A: {question_data['options']['A']}\n"
            f"B: {question_data['options']['B']}\n"
            f"C: {question_data['options']['C']}\n"
            f"D: {question_data['options']['D']}\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self._construct_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )

            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {
                "selected_option": "E", # Defaulting to E/Error on crash to not break pipeline
                "required_facts": [],
                "legal_source": "None",
                "reasoning_logic": f"Error: {str(e)}"
            }
