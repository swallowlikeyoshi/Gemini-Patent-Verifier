import asyncio
import csv
import os
from grounding_test_mcp import main, PROMPT_3

async def run_evaluation():
    csv_path = "source/scripts.csv"
    results_path = "evaluation_results.md"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    # Load advertisement scripts from CSV
    ads = []
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ads.append(row)

    print(f"Loaded {len(ads)} advertisements for evaluation.")

    evaluation_report = [
        "# Advertisement Script Evaluation Results\n",
        f"- **Evaluation Date**: {os.popen('date').read().strip()}",
        f"- **Total Advertisements**: {len(ads)}\n",
        "---\n"
    ]

    for idx, ad in enumerate(ads, 1):
        title = ad['ad']
        is_hoax = ad['isHoax']
        script = ad['script']
        
        print(f"\n[{idx}/{len(ads)}] Evaluating: {title} (Target isHoax: {is_hoax})")
        
        try:
            # Call Gemini API via the main function in grounding_test_mcp.py
            analysis = await main(PROMPT_3, script)
        except Exception as e:
            analysis = f"Error during evaluation: {e}"
            print(f"Error evaluating {title}: {e}")
        
        # Append result to the report
        evaluation_report.append(f"## {idx}. {title}")
        evaluation_report.append(f"- **Target isHoax (0: Normal, 1: Hoax)**: {is_hoax}")
        evaluation_report.append(f"- **Gemini Analysis Result**:\n\n{analysis}\n")
        evaluation_report.append("---\n")

    # Save results to a markdown file
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("\n".join(evaluation_report))
    
    print(f"\nEvaluation process complete. Results saved to: {results_path}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())