import json
import csv
import os
import sys

# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

#from llm.main import ask_question
from llm.graph import run_query
from llm.main import ask_question_llm
from metrics import (
    precision,
    recall,
    f1_score,
    exact_match,
    count_match,
    missing_sites,
    extra_sites,
    common_sites,
)

# --------------------------------------------------
# LOAD BENCHMARKS
# --------------------------------------------------

benchmark_file = os.path.join(
    os.path.dirname(__file__),
    "benchmark_cases.json"
)

with open(benchmark_file, "r", encoding="utf-8") as f:
    benchmarks = json.load(f)

# --------------------------------------------------
# REPORT FILES
# --------------------------------------------------

txt_path = os.path.join(
    os.path.dirname(__file__),
    "benchmark_report_llm.txt"
)

csv_path = os.path.join(
    os.path.dirname(__file__),
    "benchmark_report_llm.csv"
)

txt_report = open(
    txt_path,
    "w",
    encoding="utf-8"
)

csv_report = open(
    csv_path,
    "w",
    newline="",
    encoding="utf-8"
)

writer = csv.writer(csv_report)

writer.writerow([
    "Benchmark",
    "Question",
    "Expected Count",
    "Returned Count",
    "Correct",
    "Missing",
    "Extra",
    "Precision",
    "Recall",
    "F1",
    "Exact Match",
    "Count Match"
])

# --------------------------------------------------
# OVERALL METRICS
# --------------------------------------------------

total_queries = len(benchmarks)

total_precision = 0
total_recall = 0
total_f1 = 0

exact_matches = 0
count_matches = 0

txt_report.write("=" * 100 + "\n")
txt_report.write("ARCHAI BENCHMARK REPORT\n")
txt_report.write("=" * 100 + "\n\n")

# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

for benchmark in benchmarks:

    name = benchmark["name"]
    question = benchmark["query"]
    neo4j_query = benchmark["neo4j_query"]

    print(f"\nRunning Benchmark : {name}")

    # ----------------------------------------
    # Expected Result
    # ----------------------------------------

    expected_result = run_query(neo4j_query)

    expected_sites = set()

    for row in expected_result:

        if row.get("site_name"):
            expected_sites.add(row["site_name"])

    # ----------------------------------------
    # LLM Result
    # ----------------------------------------

    predicted_result, generated_cypher = ask_question_llm(
    question,
    verbose=False,
    return_cypher=True
)

    predicted_sites = set()

    for row in predicted_result:

        if row.get("site_name"):
            predicted_sites.add(row["site_name"])

    # ----------------------------------------
    # Metrics
    # ----------------------------------------

    p = precision(expected_sites, predicted_sites)
    r = recall(expected_sites, predicted_sites)
    f1 = f1_score(expected_sites, predicted_sites)

    em = exact_match(expected_sites, predicted_sites)
    cm = count_match(expected_sites, predicted_sites)

    if em:
        exact_matches += 1

    if cm:
        count_matches += 1

    total_precision += p
    total_recall += r
    total_f1 += f1

    missing = missing_sites(
        expected_sites,
        predicted_sites
    )

    extra = extra_sites(
        expected_sites,
        predicted_sites
    )

    correct = common_sites(
        expected_sites,
        predicted_sites
    )

    # ----------------------------------------
    # TXT REPORT
    # ----------------------------------------

    txt_report.write("=" * 100 + "\n")

    txt_report.write(f"Benchmark : {name}\n")
    txt_report.write(f"Question  : {question}\n\n")
    txt_report.write("Generated Cypher\n")
    txt_report.write("-" * 30 + "\n")
    txt_report.write(generated_cypher)
    txt_report.write("\n\n")

    txt_report.write(
        f"Expected Count : {len(expected_sites)}\n"
    )

    txt_report.write(
        f"Returned Count : {len(predicted_sites)}\n\n"
    )

    txt_report.write(
        f"Precision : {p*100:.2f}%\n"
    )

    txt_report.write(
        f"Recall    : {r*100:.2f}%\n"
    )

    txt_report.write(
        f"F1 Score  : {f1*100:.2f}%\n\n"
    )

    txt_report.write(
        f"Exact Match : {em}\n"
    )

    txt_report.write(
        f"Count Match : {cm}\n\n"
    )

    txt_report.write("Correct Sites\n")
    txt_report.write("-" * 30 + "\n")

    if correct:

        for site in correct:

            txt_report.write(f"✓ {site}\n")

    else:

        txt_report.write("None\n")

    txt_report.write("\n")

    txt_report.write("Missing Sites\n")
    txt_report.write("-" * 30 + "\n")

    if missing:

        for site in missing:

            txt_report.write(f"✗ {site}\n")

    else:

        txt_report.write("None\n")

    txt_report.write("\n")

    txt_report.write("Extra Sites\n")
    txt_report.write("-" * 30 + "\n")

    if extra:

        for site in extra:

            txt_report.write(f"+ {site}\n")

    else:

        txt_report.write("None\n")

    txt_report.write("\n")
        # ----------------------------------------
    # CSV REPORT
    # ----------------------------------------

    writer.writerow([
        name,
        question,
        len(expected_sites),
        len(predicted_sites),
        len(correct),
        len(missing),
        len(extra),
        round(p * 100, 2),
        round(r * 100, 2),
        round(f1 * 100, 2),
        em,
        cm
    ])

# ==========================================================
# FINAL SUMMARY
# ==========================================================

avg_precision = total_precision / total_queries
avg_recall = total_recall / total_queries
avg_f1 = total_f1 / total_queries

# We use Average F1 as the overall retrieval performance
overall_retrieval_score = avg_f1 * 100

txt_report.write("=" * 100 + "\n")
txt_report.write("OVERALL EVALUATION METRICS\n")
txt_report.write("=" * 100 + "\n\n")

txt_report.write(f"Total Benchmark Queries : {total_queries}\n\n")

txt_report.write(
    f"Average Precision       : {avg_precision*100:.2f}%\n"
)

txt_report.write(
    f"Average Recall          : {avg_recall*100:.2f}%\n"
)

txt_report.write(
    f"Average F1 Score        : {avg_f1*100:.2f}%\n\n"
)

txt_report.write(
    f"Exact Matches           : {exact_matches}/{total_queries}\n"
)

txt_report.write(
    f"Count Matches           : {count_matches}/{total_queries}\n\n"
)

txt_report.write(
    f"Overall Retrieval Performance : {overall_retrieval_score:.2f}%\n"
)

txt_report.write("\n")

txt_report.write("=" * 100 + "\n")
txt_report.write("METRIC DEFINITIONS\n")
txt_report.write("=" * 100 + "\n\n")

txt_report.write(
    "Precision : Percentage of retrieved sites that are correct.\n"
)

txt_report.write(
    "Recall    : Percentage of expected sites successfully retrieved.\n"
)

txt_report.write(
    "F1 Score  : Harmonic mean of Precision and Recall.\n"
)

txt_report.write(
    "Exact Match : Returned site set exactly matches Neo4j ground truth.\n"
)

txt_report.write(
    "Count Match : Returned the same number of sites as Neo4j.\n"
)

txt_report.close()
csv_report.close()

# ==========================================================
# CONSOLE OUTPUT
# ==========================================================

print("\n")
print("=" * 100)
print("ARCHAI BENCHMARK COMPLETE")
print("=" * 100)

print(f"Total Benchmark Queries     : {total_queries}")

print(
    f"Average Precision           : {avg_precision*100:.2f}%"
)

print(
    f"Average Recall              : {avg_recall*100:.2f}%"
)

print(
    f"Average F1 Score            : {avg_f1*100:.2f}%"
)

print(
    f"Exact Matches               : {exact_matches}/{total_queries}"
)

print(
    f"Count Matches               : {count_matches}/{total_queries}"
)

print(
    f"Overall Retrieval Performance : {overall_retrieval_score:.2f}%"
)

print("=" * 100)

print("\nGenerated Files:")
print(f"  • {txt_path}")
print(f"  • {csv_path}")