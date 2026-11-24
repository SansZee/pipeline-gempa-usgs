# Pipeline Ingesti Gempa USGS

Mengambil gempa M2.5+ dari USGS tiap 6 jam, menyimpan respons mentah (JSON) dan
hasil bersih (Parquet) ke Azure Blob Storage, serta log setiap run.

## Alur

```
GitHub Actions (cron) -> ingest.py -> raw/*.json
                                   -> transform.py -> curated/*.parquet
                                   -> logs/*.json
```

## Struktur

| File | Fungsi |
|---|---|
| `config.py` | env, nama container, ambang magnitude |
| `ingest.py` | ambil GeoJSON USGS (retry 3x) + path raw |
| `transform.py` | flatten GeoJSON -> DataFrame, validasi, dedupe |
| `main.py` | orkestrasi + upload + log run |
| `tests/test_transform.py` | test CI (tanpa Azure) |
| `.github/workflows/ci.yml` | pytest di setiap PR |
| `.github/workflows/ingest.yml` | cron 6 jam + tombol manual |

## Jalankan lokal

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AZURE_STORAGE_CONNECTION_STRING="..."
python main.py
pytest -q
```

`MIN_MAGNITUDE` (default 2.5) dan `WINDOW_HOURS` (default 12) bisa diubah lewat env.

## Data di Azure

```
raw/usgs-gempa/dt=YYYY-MM-DD/hour=HH/events-<UTC>.json
curated/usgs-gempa/dt=YYYY-MM-DD/hour=HH/events-<run_id>.parquet
logs/usgs-gempa/dt=YYYY-MM-DD/run-<run_id>.json
```

Setiap run menulis partisi sendiri, jadi data lama tidak tertimpa. `id` gempa
dipakai untuk dedupe saat query lintas partisi.

flag flag
