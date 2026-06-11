import json
import os

def generate_timeline():
    # Placeholder: In real usage, this aggregates audit logs (email, browser, doc)
    timeline = [
        {"time": "08:41:00", "event": "Email received", "artifact": "Urgent: Patent Review"},
        {"time": "08:43:00", "event": "Attachment opened", "artifact": "m57biz.xls"},
        {"time": "08:51:00", "event": "Gmail login", "artifact": "https://mail.google.com"},
        {"time": "08:53:00", "event": "File upload", "artifact": "m57biz.xls"}
    ]
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/user_activity_timeline.json", "w") as f:
        json.dump({"timeline": timeline}, f, indent=2)
        
    with open("reports/user_activity_timeline.md", "w") as f:
        f.write("# User Activity Timeline\n\n")
        for entry in timeline:
            f.write(f"- {entry['time']} {entry['event']}: {entry['artifact']}\n")

if __name__ == "__main__":
    generate_timeline()
