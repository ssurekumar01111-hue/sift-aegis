#!/usr/bin/env python3
"""
SIFT-AEGIS — Autonomous Evidence Guardian and Incident Synthesizer
Main entry point for Find Evil hackathon submission.
Usage: python3 sift_aegis.py
"""

import sys
import os

def main():
    print("""
███████╗██╗███████╗████████╗      █████╗ ███████╗ ██████╗ ██╗███████╗
██╔════╝██║██╔════╝╚══██╔══╝     ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝
███████╗██║█████╗     ██║        ███████║█████╗  ██║  ███╗██║███████╗
╚════██║██║██╔══╝     ██║        ██╔══██║██╔══╝  ██║   ██║██║╚════██║
███████║██║██║        ██║        ██║  ██║███████╗╚██████╔╝██║███████║
╚══════╝╚═╝╚═╝        ╚═╝        ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝
    Autonomous Evidence Guardian and Incident Synthesizer
    Find Evil Hackathon 2026
    """)
    
    # Run investigation
    from orchestrator import SIFTAEGISOrchestrator
    orchestrator = SIFTAEGISOrchestrator()
    results = orchestrator.investigate()
    
    # Generate report
    from reports.report_generator import generate_report
    generate_report(
        "/home/sansforensics/sift-aegis/investigation_results.json",
        "/home/sansforensics/sift-aegis/reports/dfir_report.txt"
    )
    
    print("\nSIFT-AEGIS investigation complete.")
    print("Report saved to: /home/sansforensics/sift-aegis/reports/dfir_report.txt")
    print("Audit log saved to: /home/sansforensics/sift-aegis/investigation_results.json")

if __name__ == "__main__":
    main()
