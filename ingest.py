"""Ambil gempa terbaru dari USGS dan tentukan path penyimpanan raw."""
import time
from datetime import datetime, timedelta

import requests

import config

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def fetch_events(run_time: datetime) -> dict:
    """Ambil GeoJSON gempa dalam jendela WINDOW_HOURS terakhir, retry 3x."""
    params = {
        "format": "geojson",
        "starttime": (run_time - timedelta(hours=config.WINDOW_HOURS)).strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": run_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "minmagnitude": config.MIN_MAGNITUDE,
        "orderby": "time",
    }
    error = None
    for attempt in range(3):
        try:
            response = requests.get(USGS_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            error = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Gagal mengambil data USGS setelah 3 percobaan: {error}")


def raw_path(run_time: datetime) -> str:
    return (
        f"{config.DATASET}/dt={run_time:%Y-%m-%d}/hour={run_time:%H}/"
        f"events-{run_time:%Y%m%dT%H%M%SZ}.json"
    )
