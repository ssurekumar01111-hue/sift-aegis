import sys
import os

# Add root directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from replay_engine import ReplayEngine

def run_generate():
    engine = ReplayEngine('/home/sansforensics/sift-aegis/investigation_results.json', '/home/sansforensics/sift-aegis/audit/audit_trail.jsonl')
    engine.export_replay('MEM-3908')
    engine.export_replay('MEM-2160')
    print("Replays for MEM-3908 and MEM-2160 generated.")

if __name__ == "__main__":
    run_generate()
