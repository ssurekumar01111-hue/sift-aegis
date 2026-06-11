import sys
import os
import json

# Add root directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from attack_chain_engine import AttackChainEngine

def run_reconstruct():
    engine = AttackChainEngine('graph/evidence_graph.json')
    result = engine.reconstruct()
    print("Attack chain generated.")
    print(f"Confidence: {result['confidence']}")

if __name__ == "__main__":
    run_reconstruct()
