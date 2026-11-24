"""Bersihkan GeoJSON USGS menjadi tabel siap analisis."""
import pandas as pd

KOLOM = [
    "id", "time_utc", "magnitude", "mag_type", "place", "latitude",
    "longitude", "depth_km", "tsunami", "alert", "significance", "url",
]


def to_dataframe(payload: dict) -> pd.DataFrame:
    rows = []
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        coords = list((feature.get("geometry") or {}).get("coordinates") or [])
        coords += [None, None, None]  # jaga-jaga kalau koordinat tidak lengkap
        time_ms = props.get("time")
        rows.append({
            "id": feature.get("id"),
            "time_utc": pd.to_datetime(time_ms, unit="ms", utc=True) if time_ms else pd.NaT,
            "magnitude": props.get("mag"),
            "mag_type": props.get("magType"),
            "place": props.get("place"),
            "latitude": coords[1],
            "longitude": coords[0],
            "depth_km": coords[2],
            "tsunami": props.get("tsunami"),
            "alert": props.get("alert"),
            "significance": props.get("sig"),
            "url": props.get("url"),
        })
    return pd.DataFrame(rows, columns=KOLOM)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Buang baris tanpa id/magnitude/waktu, koordinat mustahil, dan duplikat."""
    df = df.dropna(subset=["id", "magnitude", "time_utc"])
    df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)]
    df = df.drop_duplicates(subset="id").sort_values("time_utc", ascending=False) 
    return df.reset_index(drop=True)


def to_parquet_bytes(df: pd.DataFrame) -> bytes:
    return df.to_parquet(index=False)
