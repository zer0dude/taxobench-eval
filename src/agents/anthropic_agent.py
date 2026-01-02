import json
import os
from typing import Dict, Any
import anthropic
from .base import BaseAgent
from langsmith import traceable

class AnthropicAgent(BaseAgent):
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620"):
        super().__init__(model_name)
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _construct_system_prompt(self) -> str:
        prompt = self.system_prompt
        if self.few_shot_examples:
            prompt += "\n\nHere are some examples of the expected output format:\n"
            for example in self.few_shot_examples:
                 prompt += f"\nInput: {json.dumps(example['input'])}\nOutput: {json.dumps(example['output'])}\n"
        return prompt

    @traceable(run_type="llm", name="AnthropicAgent")
    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answers a question using Anthropic's Claude model.
        """
        user_prompt = (
            f"Context: {question_data.get('context_snippet')}\n"
            f"Question: {question_data.get('question_text')}\n"
            "Options:\n"
            f"A: {question_data['options']['A']}\n"
            f"B: {question_data['options']['B']}\n"
            f"C: {question_data['options']['C']}\n"
            f"D: {question_data['options']['D']}\n"
            "\nRemember to output valid JSON as per the schema."
        )

        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                system=self._construct_system_prompt(),
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract JSON from the response text
            content = message.content[0].text
            # Simple cleanup in case there are markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                 content = content.split("```")[1].strip()

            return json.loads(content)
        except Exception as e:
            return {
                "selected_option": "D",
                "required_facts": [],
                "legal_source": "None",
                "reasoning_logic": f"Error: {str(e)}"
            }
