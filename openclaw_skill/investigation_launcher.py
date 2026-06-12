import subprocess
import os

def run_full_investigation():
    """
    Launches the SIFT-AEGIS autonomous investigation pipeline as a subprocess
    and returns the full output for the agent to narrate.
    """
    project_dir = "/home/sansforensics/sift-aegis"
    script = os.path.join(project_dir, "run_investigation.sh")

    result = subprocess.run(
        ["bash", script],
        capture_output=True,
        text=True,
        cwd=project_dir,
        timeout=600
    )

    output = result.stdout
    if result.returncode != 0:
        output += "\n\n[STDERR]\n" + result.stderr

    # Append benchmark results if present
    benchmark_path = os.path.join(project_dir, "benchmark", "benchmark_results.json")
    if os.path.exists(benchmark_path):
        with open(benchmark_path) as f:
            output += "\n\n=== BENCHMARK RESULTS ===\n" + f.read()

    return output

if __name__ == "__main__":
    print(run_full_investigation())
