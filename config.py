"""Konfigurasi pipeline. Semua nilai bisa diubah lewat environment variable."""
import os

CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
RAW_CONTAINER = "raw"
CURATED_CONTAINER = "curated"
LOG_CONTAINER = "logs"
DATASET = "usgs-gempa"
MIN_MAGNITUDE = float(os.environ.get("MIN_MAGNITUDE", "2.5"))
WINDOW_HOURS = int(os.environ.get("WINDOW_HOURS", "12"))


def require_connection_string() -> str:
    if not CONNECTION_STRING:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING belum diset")
    return CONNECTION_STRING
