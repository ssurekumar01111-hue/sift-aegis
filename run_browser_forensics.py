import sqlite3
import json

db_path = "/mnt/charlie/Documents and Settings/Charlie/Application Data/Mozilla/Firefox/Profiles/2usvf7i1.default/places.sqlite"

results = []
try:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT url, title, visit_count, last_visit_date
        FROM moz_places
        WHERE visit_count > 0
        ORDER BY last_visit_date DESC
        LIMIT 100
    """)
    rows = cursor.fetchall()
    for row in rows:
        results.append({
            "url": row[0],
            "title": row[1],
            "visit_count": row[2],
            "last_visit_date": row[3],
            "artifact_type": "URL_HISTORY",
            "source_file": db_path
        })
    conn.close()
    print(f"Extracted {len(results)} URLs")
except Exception as e:
    print(f"Error: {e}")

with open("/home/sansforensics/sift-aegis/real_browser_artifacts.json", "w") as f:
    json.dump(results, f, indent=2)

print("Saved to real_browser_artifacts.json")
print("\nTop 10 URLs:")
for r in results[:10]:
    print(f"  {r['url']}")
