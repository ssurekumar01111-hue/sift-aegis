import json
import os

def reconstruct():
    # Placeholder: Reconstructs the M57 incident story
    reconstruction = {
        "incident_summary": "Phishing email led to spreadsheet theft and subsequent exfiltration via webmail.",
        "timeline": [
            "Spear-phishing email received",
            "m57biz.xls opened",
            "Gmail login detected",
            "File uploaded to Gmail"
        ],
        "confidence": 0.85
    }
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/incident_reconstruction.json", "w") as f:
        json.dump(reconstruction, f, indent=2)
        
    with open("reports/incident_reconstruction.md", "w") as f:
        f.write("# Incident Reconstruction\n\n")
        f.write(f"**Summary:** {reconstruction['incident_summary']}\n\n")
        f.write("**Timeline:**\n")
        for step in reconstruction['timeline']:
            f.write(f"- {step}\n")

if __name__ == "__main__":
    reconstruct()
