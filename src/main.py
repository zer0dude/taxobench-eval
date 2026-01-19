import argparse
import os
import sys
import json
import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add src to path to ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.loader import SuiteLoader
from src.core.evaluator import Evaluator
from src.agents.gpt_4o_agent import GPT4oAgent
from src.agents.gpt_5_mini_agent import GPT5MiniAgent
from src.agents.arbor_agent import ArborAgent

# Load environment variables
load_dotenv()

def get_agent(agent_name: str):
    if agent_name == "gpt-4o":
        return GPT4oAgent()
    elif agent_name == "gpt-5-mini":
        return GPT5MiniAgent()
    elif agent_name == "arbor":
        return ArborAgent()
    else:
        raise ValueError(f"Unknown agent: {agent_name}")


def main():
    parser = argparse.ArgumentParser(description="TaxoBench Eval - Benchmark Rig")
    parser.add_argument("--agent", type=str, required=True, choices=["gpt-4o", "gpt-5-mini", "arbor"], help="The agent to benchmark")
    parser.add_argument("--suite", type=str, required=True, help="Path to the test suite directory (e.g., suites/TAXONOMY-MANUFACTURING-SCREEN-2026-V1)")
    args = parser.parse_args()

    print(f"🚀 Starting TaxoBench Eval")
    print(f"   Agent: {args.agent}")
    print(f"   Suite: {args.suite}")
    
    # Load Suite
    try:
        loader = SuiteLoader(args.suite)
        suite_data = loader.load_suite()
        manifest = suite_data["manifest"]
        dataset = suite_data["test_dataset"]
        print(f"   Suite Loaded: {manifest.get('suite_name', 'Unknown')}")
        print(f"   Questions: {len(dataset)}")
    except Exception as e:
        print(f"❌ Error loading suite: {e}")
        return

    # Initialize Agent
    try:
        agent = get_agent(args.agent)
        # Set Dynamic Context
        agent.set_suite_context(
            instructions=suite_data["instructions"],
            output_schema=suite_data["output_schema"],
            few_shot_examples=suite_data["few_shot_examples"],
            attachments_path=suite_data["attachments_path"]
        )
    except ValueError as e:
        print(f"❌ Error initializing agent: {e}")
        return

    evaluator = Evaluator()
    
    results = []
    
    # Execution Loop
    for i, case in enumerate(dataset):
        print(f"\nEvaluating Question {i+1}/{len(dataset)}: {case['question_id']}")
        
        # Run Agent
        try:
            response = agent.answer_question(case)
        except Exception as e:
            print(f"  Example Failed: {e}")
            response = {"selected_option": "ERROR", "required_facts": [], "legal_source": "None"}

        # Prepare Expected Output from Ground Truth Ledger
        ground_truth = case["ground_truth"]
        
        # Metrics Calculation
        # 1. MCQ Binary Check
        is_option_correct = response.get("selected_option") == ground_truth["correct_option"]
        
        # 2. DeepEval (Facts & Source)
        expected_eval_data = {
            "selected_option": ground_truth["correct_option"],
            "evidence_ledger": ground_truth.get("evidence_ledger", [])
        }
        
        eval_metrics = evaluator.evaluate(
            actual_output=response,
            expected_output=expected_eval_data
        )
        
        results.append({
            "id": case["question_id"],
            "correct_option": is_option_correct,
            "mcq_score": eval_metrics["mcq_score"],
            "mcq_reason": eval_metrics["mcq_reason"],
            "facts_score": eval_metrics["facts_score"],
            "facts_reason": eval_metrics["facts_reason"],
            "source_score": eval_metrics["source_score"],
            "source_reason": eval_metrics["source_reason"],
            "agent_response": response,
            "ground_truth": ground_truth
        })
        
        print(f"  MCQ: {'✅' if is_option_correct else '❌'}")
        if not is_option_correct:
             print(f"  MCQ Reason: {eval_metrics['mcq_reason']}")
        print(f"  Facts Score: {eval_metrics['facts_score']:.2f}")
        print(f"  Source Score: {eval_metrics['source_score']:.2f}")

    # Summary Report
    print("\n" + "="*70)
    print("📊 TAXOBENCH EVAL RESULTS SUMMARY")
    print("="*70)
    print(f"{'Question ID':<20} | {'MCQ':<6} | {'Facts':<6} | {'Source':<6}")
    print("-" * 60)
    
    total_mcq = 0
    total_facts = 0
    total_source = 0
    
    for res in results:
        mcq_icon = '✅' if res['correct_option'] else '❌'
        print(f"{res['id']:<20} | {mcq_icon:<6} | {res['facts_score']:.2f}   | {res['source_score']:.2f}")
        
        if res['correct_option']: total_mcq += 1
        total_facts += res['facts_score']
        total_source += res['source_score']
            
    num = len(results) or 1
    accuracy = (total_mcq / num) * 100
    avg_facts = total_facts / num
    avg_source = total_source / num
    
    print("="*70)
    print(f"MCQ Accuracy:      {accuracy:.1f}%")
    print(f"Avg Facts Score:   {avg_facts:.2f}")
    print(f"Avg Source Score:  {avg_source:.2f}")
    print("="*70)

    # Save Results
    suite_id = manifest.get("suite_id", "unknown_suite")
    results_dir = os.path.join("results", suite_id)
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{results_dir}/results_{args.agent}_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {filename}")

if __name__ == "__main__":
    main()
