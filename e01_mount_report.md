# E01 Mount and Enumeration Report

E01 image `/home/sansforensics/cases/m57/charlie-2009-12-11.E01` was successfully verified and accessed using `mmls` and `fls`.

## Filesystem Enumeration
The filesystem was enumerated using `fls -o 63 -r`. Artifacts matching the requested extensions (.pst, .ost, .eml, .mbox, .xls, .xlsx, .doc, .docx, .pdf, .db, .sqlite) were searched for.

## Summary of Findings
- **m57biz.xls:** NOT FOUND as a file. A shortcut `M57biz.lnk` exists.
- **Email:** Thunderbird profiles were found in `Documents and Settings/Charlie/Application Data/Thunderbird/Profiles/4zy34x9h.default/Mail/`. The `Inbox` files were examined but contain no actionable email content indicating phishing.
- **Browser:** Browser history (Firefox `cookies.sqlite` and `formhistory.sqlite`) was successfully extracted and queried. Relevant activity identified includes Google searches and visits to `.mailboxes.m57.biz`.
- **Phishing:** Specific email artifacts for phishing (Alison Smith, etc.) were NOT FOUND in the M57 case files present on this image.

## Commands Executed
1. `mmls /home/sansforensics/cases/m57/charlie-2009-12-11.E01`
2. `fls -o 63 -r /home/sansforensics/cases/m57/charlie-2009-12-11.E01`
3. `icat -o 63 /home/sansforensics/cases/m57/charlie-2009-12-11.E01 <inode> > <output>`
4. `sqlite3 <db> "SELECT * FROM <table_name>;"`
