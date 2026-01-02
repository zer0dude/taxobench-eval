from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

class FactsCorrectnessMetric(GEval):
    def __init__(self):
        evaluation_criteria = (
            "Evaluate 'actual_output' (internal_facts) vs 'expected_output' (internal_facts).\n"
            "Pre-processing: IGNORE all punctuation, casing, and spacing. ALLOW +/- 5 words shift in quote start/end.\n"
            "Internal Facts have NO locator or version. Only Source and Quote.\n"
            "Score steps:\n"
            "1. **Hallucination (Critical):** Check the *Core* of the quote (excluding boundary words). VERBATIM match required.\n"
            "   - IF CORE WORDS DIFFER -> SCORE 0 (Immediate Fail).\n"
            "2. **Completeness (Critical):** Deduct 5 points if any crucial fact is missing.\n"
            "3. **Minor Issues:**\n"
            "   - **Boundaries/Formatting:** Deduct 1-2 points for messy bounds or bad formatting.\n"
            "   - **Precision:** Deduct 1 point if there are extensive irrelevant extra facts.\n\n"
            "Score 10: Perfect recall, verbatim core match.\n"
            "Score 8-9: Valid facts/quotes but with messy boundaries.\n"
            "Score 5: Missing key facts.\n"
            "Score 0: Hallucinated core words OR Missing ALL facts."
        )
        super().__init__(
            name="Facts Correctness",
            criteria=evaluation_criteria,
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            evaluation_steps=[
                "Step 1: Normalize text.",
                "Step 2 (Hallucination): Check 'Core' words of actual quotes against Context. IF DIFFER -> SCORE 0.",
                "Step 3 (Recall): Check if expected fact cores are found. If missing -> -5 points.",
                "Step 4 (Minor): Check boundaries.",
                "Step 5: Assign Final Score."
            ],
            model="gpt-4o"
        )

class LegalSourceMetric(GEval):
    def __init__(self):
        evaluation_criteria = (
            "Evaluate 'actual_output' (external_sources) vs 'expected_output' (external_sources).\n"
            "Pre-processing: IGNORE all punctuation, casing, and spacing.\n"
            "Fields Required: Source, Locator (Annex | Section), Version, Quote.\n"
            "Score steps:\n"
            "1. **Hallucination (Critical):** Check the *Core* of the quote. The sequence of words MUST match the Regulation VERBATIM.\n"
            "   - IF CORE WORDS DIFFER -> SCORE 0 (Immediate Fail).\n"
            "2. **Completeness (Critical):** Deduct 5 points if any expected source is missing.\n"
            "3. **Minor Issues:**\n"
            "   - **Locator:** Should be 'Annex | Section'. If semantic match (findable) -> 0 Penalty. If missing/misleading -> Max -1 point.\n"
            "   - **Version:** Should be present. If missing -> Max -1 point.\n"
            "   - **Boundaries:** Deviations in start/end of quote -> Max -2 points.\n"
            "4. **Precision:** Deduct 1 point for extra/irrelevant sources.\n\n"
            "Score 10: Perfect recall, verbatim core match, correct schema.\n"
            "Score 8-9: Correct content but locators/version slightly imperfect.\n"
            "Score 5: Missing key sources.\n"
            "Score 0: Hallucinated core words OR Missing ALL sources."
        )
        super().__init__(
            name="Legal Source Correctness",
            criteria=evaluation_criteria,
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            evaluation_steps=[
                "Step 1: Normalize text.",
                "Step 2 (Hallucination): Check 'Core' words of actual quotes against Regulation. IF DIFFER -> SCORE 0.",
                "Step 3 (Recall): Check if expected sources are found. If missing -> -5 points.",
                "Step 4 (Minor Issues): Validates Locator ('Annex|Section') and Version. Deduct max 1-2 points for non-critical schema issues.",
                "Step 5: Assign Final Score."
            ],
            model="gpt-4o"
        )

class Evaluator:
    def __init__(self):
        self.facts_metric = FactsCorrectnessMetric()
        self.source_metric = LegalSourceMetric()

    def evaluate(self, actual_output: dict, expected_output: dict) -> dict:
        """
        Runs the evaluation for a single case.
        Returns a dictionary with scores.
        """
        # Prepare content strings for G-Eval (it expects strings)
        
        # 1. MCQ Metric (Deterministic)
        actual_opt = actual_output.get("selected_option", "").strip().upper()
        expected_opt = expected_output.get("selected_option", "").strip().upper()
        
        if actual_opt == expected_opt:
            mcq_score = 1.0
            mcq_reason = f"The selected option '{actual_opt}' matches the ground truth."
        else:
            mcq_score = 0.0
            mcq_reason = f"The selected option '{actual_opt}' does not match the ground truth '{expected_opt}'."

        # Filter evidence for metrics
        actual_ledger = actual_output.get("evidence_ledger", [])
        expected_ledger = expected_output.get("evidence_ledger", [])

        # For Facts Metric (Context Snippets / internal_fact)
        facts_actual = str([item for item in actual_ledger if item.get("evidence_type") == "internal_fact"])
        facts_expected = str([item for item in expected_ledger if item.get("evidence_type") == "internal_fact"])
        
        test_case_facts = LLMTestCase(
            input="Evaluate these facts.", # Dummy input
            actual_output=facts_actual,
            expected_output=facts_expected
        )
        self.facts_metric.measure(test_case_facts)
        
        # For Source Metric (Legal Citations / external_source)
        source_actual = str([item for item in actual_ledger if item.get("evidence_type") == "external_source"])
        source_expected = str([item for item in expected_ledger if item.get("evidence_type") == "external_source"])
        
        test_case_source = LLMTestCase(
            input="Evaluate this legal citation.", # Dummy input
            actual_output=source_actual,
            expected_output=source_expected
        )
        self.source_metric.measure(test_case_source)
        
        return {
            "mcq_score": mcq_score,
            "mcq_reason": mcq_reason,
            "facts_score": self.facts_metric.score,
            "facts_reason": self.facts_metric.reason,
            "source_score": self.source_metric.score,
            "source_reason": self.source_metric.reason
        }
