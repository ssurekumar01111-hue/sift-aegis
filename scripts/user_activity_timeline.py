import json
import datetime

def build_timeline():
    events = []
    
    # Load browser artifacts
    with open("real_browser_artifacts.json") as f:
        browser = json.load(f)
    for item in browser:
        if item.get("last_visit_date") and not item.get("error"):
            events.append({
                "timestamp": item["last_visit_date"],
                "event_type": "BROWSER_VISIT",
                "description": f"Visited: {item['url'][:100]}",
                "artifact_source": item["source_file"],
                "confidence": 0.95
            })
    
    # Load email artifacts
    with open("real_email_artifacts.json") as f:
        emails = json.load(f)
    for item in emails:
        if item.get("date") and not item.get("error"):
            event_type = "EMAIL_SENT" if item["mailbox"] == "Sent" else "EMAIL_RECEIVED"
            events.append({
                "timestamp": item["date"],
                "event_type": event_type,
                "description": f"{event_type}: {item['subject']} | From: {item['from']} | To: {item['to']}",
                "artifact_source": item["source_file"],
                "confidence": 0.95
            })
    
    # Load document artifacts
    with open("real_document_artifacts.json") as f:
        docs = json.load(f)
    for item in docs:
        if item.get("modified") and not item.get("error"):
            events.append({
                "timestamp": item["modified"],
                "event_type": "FILE_ACCESS",
                "description": f"File accessed: {item['file_name']}",
                "artifact_source": item.get("source_file", item.get("file_path", "")),
                "confidence": 0.90
            })
    
    # Sort by timestamp
    events.sort(key=lambda x: str(x["timestamp"]))
    
    return events

if __name__ == "__main__":
    timeline = build_timeline()
    with open("real_user_activity_timeline.json", "w") as f:
        json.dump(timeline, f, indent=2)
    print(f"Timeline built: {len(timeline)} events")
    print("\nKey events (emails only):")
    for e in timeline:
        if "EMAIL" in e["event_type"]:
            print(f"  {e['timestamp']} | {e['description'][:120]}")
