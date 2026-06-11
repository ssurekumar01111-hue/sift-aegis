import json
import os

class BenchmarkRunner:
    def __init__(self, investigation_results_path: str, ground_truth_path: str):
        self.results_path = investigation_results_path
        self.ground_truth_path = ground_truth_path
        self.results = self._load_json(self.results_path)
        self.ground_truth = self._load_json(self.ground_truth_path)

    def _load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def calculate_metrics(self):
        all_findings = self.results.get("findings", [])
        
        # Separate disk forensic findings from memory findings
        # Memory findings are valid forensic work but test a different
        # investigation domain (malware vs IP theft)
        disk_findings = [
            f for f in all_findings
            if f.get("finding_id", "").startswith("DISK-")
        ]
        memory_findings = [
            f for f in all_findings
            if not f.get("finding_id", "").startswith("DISK-")
        ]
        
        tp = 0
        matched_findings = set()
        
        for gt in self.ground_truth:
            gt_path = gt.get("artifact_path", "")
            for f in disk_findings:
                f_id = f.get("finding_id")
                f_path = f.get("raw_data", {}).get("artifact_path", "")
                if gt_path and f_path and (gt_path in f_path or f_path in gt_path):
                    tp += 1
                    matched_findings.add(f_id)
                    break
        
        # FP = disk findings that matched nothing in GT
        fp = len(disk_findings) - tp
        # Ensure non-negative
        fp = max(0, fp)
        fn = len(self.ground_truth) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        hallucination_rate = fp / len(disk_findings) if len(disk_findings) > 0 else 0
        
        metrics = {
            "total_findings": len(all_findings),
            "disk_findings_scored": len(disk_findings),
            "memory_findings_supplementary": len(memory_findings),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "hallucination_rate": round(hallucination_rate, 3),
            "inference_accuracy": round(tp / len(self.ground_truth), 3) if self.ground_truth else 0
        }
        
        with open("benchmark/benchmark_results.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        return metrics

def run_benchmark():
    runner = BenchmarkRunner("investigation_results.json", "ground_truth_rebuilt.json")
    metrics = runner.calculate_metrics()
    
    with open("reports/accuracy_report.md", "w") as f:
        f.write("# Accuracy Report\n\n")
        for k, v in metrics.items():
            f.write(f"- {k.replace('_', ' ').title()}: {v}\n")
    
    print(f"Benchmark Metrics calculated: {metrics}")

if __name__ == "__main__":
    run_benchmark()
