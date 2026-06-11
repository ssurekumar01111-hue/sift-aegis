import json

with open("/home/sansforensics/sift-aegis/real_browser_artifacts.json") as f:
    browser = json.load(f)

patent_keywords = ["wipo", "patent", "google.com/patents", "quantum",
                   "cryptography", "prior art", "nitroba", "m57"]

patent_urls = []
for item in browser:
    url = item.get("url", "").lower()
    if any(kw in url for kw in patent_keywords):
        patent_urls.append(item)

print(f"Total browser items: {len(browser)}")
print(f"Patent URLs found: {len(patent_urls)}")
print("Sample patent URLs:")
for u in patent_urls[:5]:
    print(" ", u.get("url", "")[:100])

print("\nSample raw browser items (first 3):")
for item in browser[:3]:
    print(" ", item)
