import sys
import os

# Add root directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from benchmark.benchmark_runner import run_benchmark

if __name__ == "__main__":
    run_benchmark()
