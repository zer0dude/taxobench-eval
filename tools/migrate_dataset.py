import json
import os

DATASET_PATH = r"c:\Users\brian\Documents\bj-unipessoal\taxobench-eval\suites\TAXONOMY-MANUFACTURING-SCREEN-2026-V1\dataset.json"

def migrate():
    print(f"Loading dataset from {DATASET_PATH}")
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        ledger = item.get("ground_truth", {}).get("evidence_ledger", [])
        new_ledger = []
        for evidence in ledger:
            ev_type = evidence.get("evidence_type")
            
            # Common fields
            new_ev = {
                "evidence_type": ev_type,
                "source": evidence.get("source"),
                "quote_anchor": evidence.get("quote_anchor")
            }

            if ev_type == "internal_fact":
                # STRIP locator and version
                # No other fields needed
                pass

            elif ev_type == "external_source":
                # HANDLE locator
                old_loc = evidence.get("locator")
                new_loc_str = "N/A"
                
                if isinstance(old_loc, dict):
                    annex = old_loc.get("annex", "Annex I")
                    section = old_loc.get("section", "")
                    # Format: Annex I | Section 3.7
                    # Ignore subsection as per plan
                    new_loc_str = f"{annex} | Section {section}"
                elif isinstance(old_loc, str):
                    new_loc_str = old_loc # Keep if already string (unlikely based on view)
                
                new_ev["locator"] = new_loc_str

                # HANDLE version
                version = evidence.get("version")
                if not version:
                    version = "OJ L 442, 09.12.2021" # Default fallback
                new_ev["version"] = version

            new_ledger.append(new_ev)
        
        item["ground_truth"]["evidence_ledger"] = new_ledger

    print("Saving migrated dataset...")
    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Done!")

if __name__ == "__main__":
    migrate()
