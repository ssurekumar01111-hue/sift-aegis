# Graph Validation Report

This report documents the evidence graph generated from real M57 investigation data.

## Graph Statistics

* **Node Count:** 32
* **Edge Count:** 44
* **Orphan Count:** 0

## Node Sample (First 20)

1. MEM-3908
2. pslist:PID:3908
3. self_correction:dll_verification:PID:3908
4. self_correction:process_reconfirmed
5. MEM-2160
6. pslist:PID:2160
7. self_correction:dll_verification:PID:2160
8. MAL-924-0x850000
9. malfind:PID:924
10. malfind:address:0x850000
11. malfind:protection:Vad
12. MAL-924-0xbd0000
13. malfind:address:0xbd0000
14. MAL-924-0x7f6f0000
15. malfind:address:0x7f6f0000
16. MAL-948-0x5c0000
17. malfind:PID:948
18. malfind:address:0x5c0000
19. MAL-948-0x20e90000
20. malfind:address:0x20e90000

## Edge Sample (First 20)

1. pslist:PID:3908 -> MEM-3908 (supports)
2. self_correction:dll_verification:PID:3908 -> MEM-3908 (supports)
3. self_correction:process_reconfirmed -> MEM-3908 (supports)
4. self_correction:dll_verification:PID:3908 -> MEM-3908 (supports)
5. self_correction:process_reconfirmed -> MEM-3908 (supports)
6. self_correction:dll_verification:PID:3908 -> MEM-3908 (supports)
7. self_correction:process_reconfirmed -> MEM-3908 (supports)
8. pslist:PID:2160 -> MEM-2160 (supports)
9. self_correction:dll_verification:PID:2160 -> MEM-2160 (supports)
10. self_correction:process_reconfirmed -> MEM-2160 (supports)
11. self_correction:dll_verification:PID:2160 -> MEM-2160 (supports)
12. self_correction:process_reconfirmed -> MEM-2160 (supports)
13. self_correction:dll_verification:PID:2160 -> MEM-2160 (supports)
14. self_correction:process_reconfirmed -> MEM-2160 (supports)
15. malfind:PID:924 -> MAL-924-0x850000 (supports)
16. malfind:address:0x850000 -> MAL-924-0x850000 (supports)
17. malfind:protection:Vad -> MAL-924-0x850000 (supports)
18. malfind:PID:924 -> MAL-924-0xbd0000 (supports)
19. malfind:address:0xbd0000 -> MAL-924-0xbd0000 (supports)
20. malfind:protection:Vad -> MAL-924-0xbd0000 (supports)

## Key Finding Relationships

### MEM-3908 Relationships
* Supported by: `pslist:PID:3908`, `self_correction:dll_verification:PID:3908`, `self_correction:process_reconfirmed`

### MEM-2160 Relationships
* Supported by: `pslist:PID:2160`, `self_correction:dll_verification:PID:2160`, `self_correction:process_reconfirmed`
