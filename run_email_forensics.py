import mailbox
import json

mailboxes = {
    "Inbox": "/mnt/charlie/Documents and Settings/Charlie/Application Data/Thunderbird/Profiles/4zy34x9h.default/Mail/Local Folders/Inbox",
    "Sent": "/mnt/charlie/Documents and Settings/Charlie/Application Data/Thunderbird/Profiles/4zy34x9h.default/Mail/Local Folders/Sent"
}

results = []
for mbox_name, mbox_path in mailboxes.items():
    try:
        mbox = mailbox.mbox(mbox_path)
        count = 0
        for msg in mbox:
            payload = msg.get_payload(decode=False)
            body_preview = ""
            if isinstance(payload, str):
                body_preview = payload[:300]
            results.append({
                "subject": msg.get("subject", ""),
                "from": msg.get("from", ""),
                "to": msg.get("to", ""),
                "date": msg.get("date", ""),
                "mailbox": mbox_name,
                "source_file": mbox_path,
                "body_preview": body_preview
            })
            count += 1
        mbox.close()
        print(f"{mbox_name}: {count} messages parsed")
    except Exception as e:
        print(f"Error on {mbox_name}: {e}")

with open("/home/sansforensics/sift-aegis/real_email_artifacts.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nTotal messages: {len(results)}")
print("\nAll emails:")
for r in results:
    print(f"  [{r['mailbox']}] {r['date']} | From: {r['from']} | To: {r['to']} | Subject: {r['subject']}")
