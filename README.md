# TaxoBench Eval

**TaxoBench Eval** is a sophisticated benchmarking framework designed to evaluate Large Language Model types (Agents) on their ability to perform **EU Taxonomy** classification and eligibility screening.

It goes beyond simple "Right/Wrong" answers by rigorously evaluating the **evidence retrieval process**, distinguishing between internal factual recall and external legal citation accuracy.

## Key Features

*   **Granular Evaluation**: Uses custom `DeepEval` metrics to score:
    *   **MCQ Accuracy**: Did the agent pick the right classification?
    *   **Facts Correctness**: Did the agent correctly cite internal documents (Context)?
    *   **Legal Source Validity**: Did the agent cite the correct EU Regulation (ELI) and locator (Annex/Section)?
*   **Strict Hallucination Detection**: Implements a **"Core Verbatim"** check. Quotes are normalized and checked against ground truth; any core deviation results in a score of 0.
*   **Modular Test Suites**: Supports plug-and-play test suites (e.g., Manufacturing, Climate Change) defined via JSON/Markdown configuration.
*   **Multi-Agent Support**: Ready-to-use wrappers for **GPT-4o**, **GPT-5-Mini**, and **Arbor** (internal) agents.
*   **Detailed Reporting**: Generates JSON reports with score breakdowns for every question.

## Installation

Prerequisites:
- Python 3.10+
- Valid API Keys for the agents you intend to test (OPENAI_API_KEY, etc.)

```bash
git clone https://github.com/zer0dude/taxobench-eval.git
cd taxobench-eval
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory:

```ini
OPENAI_API_KEY=sk-...
# Add other keys as needed
```

## Usage

Run the benchmark using `src/main.py`. You must specify the **agent** and the **suite** directory.

```bash
python src/main.py --agent gpt-4o --suite suites/TAXONOMY-MANUFACTURING-SCREEN-2026-V1
```

### Available Arguments

- `--agent`: The agent to test. Options: `gpt-4o`, `gpt-5-mini`, `arbor` (mock).
- `--suite`: Path to the test suite directory containing `manifest.json` and `dataset.json`.

## Project Structure

```
taxobench-eval/
├── src/
│   ├── agents/          # Agent implementations (wrappers)
│   ├── core/            # Evaluator logic & metrics (DeepEval)
│   └── main.py          # Entry point
├── suites/              # Benchmark Test Suites
│   └── TAXONOMY-.../    # Example Suite
│       ├── dataset.json # Ground Truth (Questions & Evidence)
│       ├── schema.json  # Output constraint schema
│       └── instructions.md # System prompt instructions
├── results/             # Generated evaluation reports
├── tools/               # Utilities (e.g., dataset migration)
└── requirements.txt
```

## Evaluation Logic

The evaluator is designed to be **fair but rigorous**:

1.  **Normalization**: All text is normalized (case/punctuation ignored) before comparison.
2.  **Logic**:
    *   **Fact/Source Recall**: Missing critical evidence = **-5 points**.
    *   **Hallucination**: If the *core words* of a quote do not match the source verbatim = **Score 0** (Critical Fail).
    *   **Locators**: Loose matching allowed for legal locators (e.g., "Annex I | Section 3.7"), but active misleading info is penalized.
    *   **Boundaries**: Allow +/- 5 words tolerance for quote start/end.

## License

[MIT License](LICENSE)
