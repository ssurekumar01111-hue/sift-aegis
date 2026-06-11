#!/bin/bash
echo "=============================================="
echo "SIFT-AEGIS Autonomous DFIR Investigation"
echo "Find Evil Hackathon 2026"
echo "=============================================="
echo ""
echo "Evidence: charlie-2009-11-17 (M57-Patents)"
echo "Agent: OpenClaw + Gemini 3.1 Flash-Lite"
echo "MCP Server: 6 read-only typed forensic tools"
echo ""

if [ ! -f "/home/sansforensics/cases/m57/charlie-2009-11-17.mddramimage" ]; then
    echo "ERROR: Memory image not found."
    echo "Download with:"
    echo "  cd ~/cases/m57"
    echo "  aws s3 cp s3://digitalcorpora/corpora/scenarios/2009-m57-patents/ram/charlie-2009-11-17.mddramimage.zip . --no-sign-request"
    echo "  unzip charlie-2009-11-17.mddramimage.zip"
    exit 1
fi

echo "[*] Evidence integrity check..."
sha256sum /home/sansforensics/cases/m57/charlie-2009-11-17.mddramimage

echo ""
echo "[*] Starting autonomous investigation..."
echo ""

cd /home/sansforensics/sift-aegis
python3 sift_aegis.py

echo ""
echo "[*] Investigation complete."
echo "[*] Report:    /home/sansforensics/sift-aegis/reports/dfir_report.txt"
echo "[*] Audit log: /home/sansforensics/sift-aegis/audit/audit_trail.jsonl"
echo ""
echo "To launch OpenClaw interactive agent:"
echo "  cd ~/sift-aegis && openclaw start"
echo "  Then type: Investigate the M57-Patents case"
