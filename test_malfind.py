import sys, os
os.environ['CASES_DIR'] = '/home/sansforensics/cases/m57'
sys.path.insert(0, 'mcp_server')
from server import get_malfind
result = get_malfind('charlie-2009-11-17.mddramimage')
print('Malfind entries:', result.get('total_count', 0))
print('Suspicious PIDs:', result.get('suspicious_pids', []))
for e in result.get('entries', [])[:5]:
    print(f"  PID {e['pid']}: {e['process_name']} @ {e['address']} protection={e['protection']}")
