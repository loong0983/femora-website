# FEMORA — laman web (Bahasa Malaysia)

- `dist/`  → fail laman yang siap dimuat naik ke Hostinger (`public_html`)
- `config.json` → semua maklumat perniagaan (harga, WhatsApp, no. MAL, dll.)
- `build.py` → bina semula `dist/` selepas config.json diubah:  `python3 build.py`
- `img/` → letak gambar di sini (nama fail ikut PROMPT-GAMBAR.md), kemudian bina semula
- `PROMPT-GAMBAR.md` → prompt gambar untuk ChatGPT

Sebelum go-live: isi config.json, tukar `"draf": false`, jalankan `python3 build.py --ketat`.
