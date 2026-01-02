import json
import os
from typing import Dict, Any, List

class SuiteLoader:
    def __init__(self, suite_path: str):
        self.suite_path = suite_path
        self.manifest_path = os.path.join(suite_path, "manifest.json")
        
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")

    def load_suite(self) -> Dict[str, Any]:
        """
        Loads all components of the suite based on the manifest.
        """
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        components = manifest.get("components", {})
        
        # Load Instructions
        instructions_file = components.get("instructions")
        if instructions_file:
            with open(os.path.join(self.suite_path, instructions_file), 'r', encoding='utf-8') as f:
                instructions = f.read()
        else:
            instructions = ""

        # Load Schema
        schema_file = components.get("output_schema")
        if schema_file:
            with open(os.path.join(self.suite_path, schema_file), 'r', encoding='utf-8') as f:
                output_schema = json.load(f)
        else:
            output_schema = {}

        # Load Examples
        examples_file = components.get("few_shot_examples")
        if examples_file:
            with open(os.path.join(self.suite_path, examples_file), 'r', encoding='utf-8') as f:
                few_shot_examples = json.load(f)
        else:
            few_shot_examples = []

        # Load Dataset
        dataset_file = components.get("test_dataset")
        if dataset_file:
            with open(os.path.join(self.suite_path, dataset_file), 'r', encoding='utf-8') as f:
                test_dataset = json.load(f)
        else:
            test_dataset = []

        # Attachments Path
        attachments_dir = components.get("attachments", "attachments")
        attachments_path = os.path.join(self.suite_path, attachments_dir)
        if not os.path.exists(attachments_path):
             # Ensure it exists if defined in manifest, or just provide path
             os.makedirs(attachments_path, exist_ok=True)

        return {
            "manifest": manifest,
            "instructions": instructions,
            "output_schema": output_schema,
            "few_shot_examples": few_shot_examples,
            "test_dataset": test_dataset,
            "attachments_path": attachments_path
        }
