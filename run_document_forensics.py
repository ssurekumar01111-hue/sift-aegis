import os
import struct
import datetime
import json

results = []

def parse_lnk_timestamps(fpath):
    try:
        with open(fpath, "rb") as f:
            data = f.read(100)
        if len(data) >= 76 and data[0:4] == b'\x4C\x00\x00\x00':
            def parse_filetime(b):
                val = struct.unpack_from('<Q', b)[0]
                if val == 0:
                    return None
                return str(datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=val//10))
            return {
                "file_name": os.path.basename(fpath),
                "file_path": fpath,
                "file_type": "LNK",
                "created": parse_filetime(data[28:36]),
                "modified": parse_filetime(data[36:44]),
                "accessed": parse_filetime(data[44:52]),
                "source_file": fpath
            }
    except Exception as e:
        return {"file_name": os.path.basename(fpath), "error": str(e), "source_file": fpath}

# Parse confirmed LNK files
lnk_files = [
    "/mnt/charlie/Documents and Settings/Charlie/Recent/M57biz.lnk",
    "/home/sansforensics/sift-aegis/M57biz.lnk"
]

for lnk in lnk_files:
    if os.path.exists(lnk):
        result = parse_lnk_timestamps(lnk)
        results.append(result)
        print(f"LNK: {result}")

# Scan Recent folder for all LNK files
recent_dir = "/mnt/charlie/Documents and Settings/Charlie/Recent"
if os.path.exists(recent_dir):
    for fname in os.listdir(recent_dir):
        if fname.lower().endswith(".lnk"):
            fpath = os.path.join(recent_dir, fname)
            result = parse_lnk_timestamps(fpath)
            results.append(result)

# Scan My Documents
mydocs = "/mnt/charlie/Documents and Settings/Charlie/My Documents"
if os.path.exists(mydocs):
    for root, dirs, files in os.walk(mydocs):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                stat = os.stat(fpath)
                results.append({
                    "file_name": fname,
                    "file_path": fpath,
                    "file_type": os.path.splitext(fname)[1].upper(),
                    "size_bytes": stat.st_size,
                    "modified": str(datetime.datetime.fromtimestamp(stat.st_mtime)),
                    "source_file": fpath
                })
            except Exception as e:
                results.append({"file_name": fname, "error": str(e)})

# Save
with open("/home/sansforensics/sift-aegis/real_document_artifacts.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nTotal document artifacts: {len(results)}")
print("\nAll files found:")
for r in results:
    if "error" not in r:
        print(f"  [{r.get('file_type','?')}] {r.get('file_name')} | Modified: {r.get('modified','?')} | Path: {r.get('file_path')}")
