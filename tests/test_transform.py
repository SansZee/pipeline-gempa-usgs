"""Test murni (tanpa Azure) yang dijalankan CI di setiap pull request."""
from transform import KOLOM, clean, to_dataframe


def feature(fid="a1", mag=5.2, lat=-3.0, lon=120.0, depth=10.0, time=1732000000000):
    return {
        "id": fid,
        "properties": {
            "time": time, "mag": mag, "magType": "mb", "place": "Test",
            "tsunami": 0, "alert": None, "sig": 400, "url": "https://contoh",
        },
        "geometry": {"coordinates": [lon, lat, depth]},
    }


def payload(*features):
    return {"features": list(features)}


def test_kolom_lengkap_dan_koordinat_benar():
    df = to_dataframe(payload(feature()))
    assert list(df.columns) == KOLOM
    assert df.loc[0, "latitude"] == -3.0
    assert df.loc[0, "longitude"] == 120.0
    assert df.loc[0, "time_utc"].tzinfo is not None


def test_koordinat_mustahil_dibuang():
    df = clean(to_dataframe(payload(feature(fid="ok"), feature(fid="rusak", lat=999))))
    assert list(df["id"]) == ["ok"]


def test_id_duplikat_dibuang():
    df = clean(to_dataframe(payload(feature(), feature())))
    assert len(df) == 1


def test_magnitude_kosong_dibuang():
    df = clean(to_dataframe(payload(feature(fid="ok"), feature(fid="kosong", mag=None))))
    assert list(df["id"]) == ["ok"]
