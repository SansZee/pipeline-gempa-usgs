"""Orkestrasi pipeline: ingest -> raw -> transform -> curated -> log."""
import json
import sys
import uuid
from datetime import datetime, timezone

from azure.storage.blob import BlobServiceClient

import config
from ingest import fetch_events, raw_path
from transform import clean, to_dataframe, to_parquet_bytes


def upload(container: str, path: str, data: bytes, content_type: str) -> None:
    client = BlobServiceClient.from_connection_string(config.require_connection_string())
    client.get_container_client(container).get_blob_client(path).upload_blob(
        data, overwrite=True, content_type=content_type
    )


def main() -> None:
    run_time = datetime.now(timezone.utc)
    run_id = f"{run_time:%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:6]}"
    status, rows, error = "failed", 0, None

    try:
        payload = fetch_events(run_time)
        upload(
            config.RAW_CONTAINER,
            raw_path(run_time),
            json.dumps(payload, ensure_ascii=False).encode(),
            "application/json",
        )

        df = clean(to_dataframe(payload))
        rows = len(df)
        curated_path = (
            f"{config.DATASET}/dt={run_time:%Y-%m-%d}/hour={run_time:%H}/"
            f"events-{run_id}.parquet"
        )
        upload(config.CURATED_CONTAINER, curated_path, to_parquet_bytes(df), "application/octet-stream")
        status = "success"
        print(f"{rows} gempa tersimpan di {curated_path}")
    except Exception as exc:  # pipeline tetap menulis log, lalu gagal keras
        error = f"{type(exc).__name__}: {exc}"
        print(error, file=sys.stderr)
    finally:
        log = {
            "run_id": run_id,
            "run_time_utc": run_time.isoformat(),
            "status": status,
            "rows": rows,
            "min_magnitude": config.MIN_MAGNITUDE,
            "window_hours": config.WINDOW_HOURS,
            "error": error,
        }
        try:
            upload(
                config.LOG_CONTAINER,
                f"{config.DATASET}/dt={run_time:%Y-%m-%d}/run-{run_id}.json",
                json.dumps(log, indent=2).encode(),
                "application/json",
            )
        except Exception as log_exc:
            print(f"Gagal menulis log: {log_exc}", file=sys.stderr)

    if status != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
