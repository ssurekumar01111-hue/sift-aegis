import json
import os
import re

class BenchmarkRunner:
    def __init__(self, investigation_results_path: str, ground_truth_path: str):
        self.results_path = investigation_results_path
        self.ground_truth_path = ground_truth_path
        self.results = self._load_json(self.results_path)
        self.ground_truth = self._load_json(self.ground_truth_path)

    def _load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _normalize_path(self, path):
        if not path or not isinstance(path, str):
            return ""
        # Lowercase, normalize slashes, and strip leading scenario prefixes
        p = path.lower().replace("\\", "/")
        if p.startswith("charlie/"):
            p = p[len("charlie/"):]
        return p.strip("/")

    def _get_filename(self, path):
        if not path:
            return ""
        fname = os.path.basename(path)
        if fname.lower().endswith(".lnk"):
            fname = fname[:-4]
        return fname.lower()

    def _extract_emails(self, text):
        if not text:
            return set()
        return set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text.lower()))

    def calculate_metrics(self):
        all_findings = self.results.get("findings", [])
        
        # Separate disk forensic findings from memory findings
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
        matched_gt_ids = set()
        
        print("\n--- Benchmark Match Report ---")
        
        for gt in self.ground_truth:
            gt_id = gt.get("id")
            gt_path = self._normalize_path(gt.get("artifact_path", ""))
            gt_fname = self._get_filename(gt_path)
            gt_keywords = [k.lower() for k in gt.get("keywords", [])]
            gt_emails = [e.lower() for e in gt.get("emails", [])]
            gt_subjects = [s.lower() for s in gt.get("subjects", [])]
            
            if not gt_path and not gt_keywords and not gt_emails:
                continue

            matched_by = []
            
            for f in disk_findings:
                f_id = f.get("finding_id")
                f_desc = f.get("description", "").lower()
                f_path = self._normalize_path(f.get("raw_data", {}).get("artifact_path", ""))
                f_fname = self._get_filename(f_path)
                f_text = str(f).lower()
                f_emails = self._extract_emails(f_text)
                
                is_match = False
                
                # 1. Path/Subset match
                if gt_path and f_path:
                    if gt_path in f_path or f_path in gt_path:
                        is_match = True
                
                # 2. Filename match (independent of path)
                if not is_match and gt_fname and f_fname:
                    if gt_fname == f_fname:
                        is_match = True
                
                # 3. Keyword match
                if not is_match and gt_keywords:
                    for k in gt_keywords:
                        if k in f_desc or k in f_text:
                            is_match = True
                            break
                
                # 4. Email match
                if not is_match and gt_emails:
                    for e in gt_emails:
                        if e in f_emails:
                            is_match = True
                            break
                            
                # 5. Subject match
                if not is_match and gt_subjects:
                    for s in gt_subjects:
                        if s in f_text:
                            is_match = True
                            break

                # 6. Check supporting evidence
                if not is_match:
                    for ev in f.get("supporting_evidence", []):
                        if isinstance(ev, str):
                            ev_lower = ev.lower()
                            if ":" in ev_lower:
                                parts = ev_lower.split(":", 1)
                                if len(parts) > 1:
                                    ep = self._normalize_path(parts[1])
                                    ef = self._get_filename(ep)
                                    if gt_path and ep and (gt_path in ep or ep in gt_path):
                                        is_match = True
                                        break
                                    if gt_fname and ef and gt_fname == ef:
                                        is_match = True
                                        break
                            
                            # Check keywords/emails in supporting evidence text too
                            if not is_match and gt_keywords:
                                for k in gt_keywords:
                                    if k in ev_lower:
                                        is_match = True
                                        break
                            if not is_match and gt_emails:
                                for e in gt_emails:
                                    if e in ev_lower:
                                        is_match = True
                                        break

                if is_match:
                    matched_by.append(f_id)
            
            if matched_by:
                tp += 1
                matched_findings.update(matched_by)
                matched_gt_ids.add(gt_id)
                print(f"[TP] GT Item {gt_id} matched by: {', '.join(matched_by)}")
            else:
                print(f"[FN] GT Item {gt_id} UNMATCHED")
                
        print("------------------------------\n")
        
        # FP = disk findings that matched nothing in GT
        fp = len(disk_findings) - len(matched_findings)
        # Ensure non-negative
        fp = max(0, fp)
        fn = len(self.ground_truth) - len(matched_gt_ids)
        
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
    gt_path = "benchmark/ground_truth_charlie.json"
    runner = BenchmarkRunner("investigation_results.json", gt_path)
    metrics = runner.calculate_metrics()
    
    with open("reports/accuracy_report.md", "w") as f:
        f.write("# Accuracy Report\n\n")
        for k, v in metrics.items():
            f.write(f"- {k.replace('_', ' ').title()}: {v}\n")
    
    print(f"Benchmark Metrics calculated: {metrics}")

if __name__ == "__main__":
    run_benchmark()
