import json

from main import ask_question


# -----------------------------------
# LOAD BENCHMARKS
# -----------------------------------

with open(
    "benchmark_queries.json",
    "r",
    encoding="utf-8"
) as f:

    benchmarks = json.load(f)


# -----------------------------------
# REPORT FILE
# -----------------------------------

report = open(
    "benchmark_report.txt",
    "w",
    encoding="utf-8"
)

report.write(
    "ARCHAI BENCHMARK REPORT\n"
)

report.write(
    "=" * 80 + "\n\n"
)


# -----------------------------------
# STATS
# -----------------------------------

total = 0
passed = 0


print("\nRUNNING BENCHMARKS...\n")


# -----------------------------------
# TEST LOOP
# -----------------------------------

for query, expected_count in benchmarks.items():

    total += 1

    try:

        result = ask_question(query)

        actual_count = len(result)

        difference = abs(
            actual_count - expected_count
        )

        # -----------------------------------
        # PASS IF DIFFERENCE <= 1
        # -----------------------------------

        if difference <= 1:

            status = "PASS"
            passed += 1

        else:

            status = "FAIL"

        print(
            f"{query}"
        )

        print(
            f"Expected : {expected_count}"
        )

        print(
            f"Actual   : {actual_count}"
        )

        print(
            f"Status   : {status}"
        )

        print(
            "-" * 40
        )

        report.write(
            f"Query: {query}\n"
        )

        report.write(
            f"Expected Count : {expected_count}\n"
        )

        report.write(
            f"Actual Count   : {actual_count}\n"
        )

        report.write(
            f"Difference     : {difference}\n"
        )

        report.write(
            f"Status         : {status}\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

    except Exception as e:

        report.write(
            f"Query: {query}\n"
        )

        report.write(
            f"ERROR: {e}\n"
        )

        report.write(
            "-" * 60 + "\n"
        )


# -----------------------------------
# FINAL ACCURACY
# -----------------------------------

accuracy = (
    passed / total
) * 100 if total > 0 else 0


report.write("\n")
report.write("=" * 80 + "\n")

report.write(
    f"Passed   : {passed}\n"
)

report.write(
    f"Total    : {total}\n"
)

report.write(
    f"Accuracy : {accuracy:.2f}%\n"
)

report.close()


print("\n")
print("=" * 80)
print(f"Passed   : {passed}")
print(f"Total    : {total}")
print(f"Accuracy : {accuracy:.2f}%")
print("=" * 80)

print(
    "\nBenchmark report saved to benchmark_report.txt"
)