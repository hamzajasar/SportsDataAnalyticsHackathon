from fastapi.testclient import TestClient

from app.main import app
from app.services.datasets import table_name

client = TestClient(app)


def test_list_datasets(sample_data_dir):
    ids = [d["id"] for d in client.get("/api/datasets").json()]
    assert ids == ["nested/Matches 2024.parquet", "teams.csv", "teams_excel.xlsx"]


def test_preview_and_sort(sample_data_dir):
    r = client.get(
        "/api/datasets/preview",
        params={"id": "nested/Matches 2024.parquet", "limit": 5, "sort": "match_id", "desc": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total_rows"] == 20
    assert body["rows"][0][0] == 20
    assert len(body["rows"]) == 5


def test_preview_handles_nulls_and_excel(sample_data_dir):
    rows = client.get("/api/datasets/preview", params={"id": "teams_excel.xlsx"}).json()["rows"]
    assert rows[3][1] is None


def test_summary(sample_data_dir):
    body = client.get("/api/datasets/summary", params={"id": "teams.csv"}).json()
    assert body["rows"] == 4
    cols = {c["name"]: c for c in body["columns"]}
    assert cols["team_id"]["likely_key"] is True
    assert cols["team_name"]["null_pct"] == 25.0


def test_unknown_and_traversal_rejected(sample_data_dir):
    for bad in ["nope.csv", "../raw/teams.csv", "/etc/passwd", "notes.txt"]:
        assert client.get("/api/datasets/preview", params={"id": bad}).status_code == 404
    r = client.get("/api/datasets/preview", params={"id": "teams.csv", "sort": "x; DROP"})
    assert r.status_code == 400


def test_table_name():
    assert table_name("nested/Matches 2024.parquet") == "nested_matches_2024"
    assert table_name("2024.csv") == "t_2024"
    assert table_name("transfermarkt/games.csv.gz") == "transfermarkt_games"


def test_gzip_csv_supported(sample_data_dir):
    import gzip

    raw = sample_data_dir / "raw"
    with gzip.open(raw / "games.csv.gz", "wt") as f:
        f.write("game_id,attendance\n1,500\n2,\n")
    assert "games.csv.gz" in [d["id"] for d in client.get("/api/datasets").json()]
    body = client.get("/api/datasets/summary", params={"id": "games.csv.gz"}).json()
    assert body["rows"] == 2


def test_profile_script(sample_data_dir, capsys):
    from scripts.profile_data import main

    main()
    out = capsys.readouterr().out
    assert "teams.csv" in out
    report = (sample_data_dir / "processed" / "_profile.md").read_text()
    assert "team_id" in report
    assert "teams.csv`.`team_id` → `teams_excel.xlsx`.`team_id` — 100% of values match" in report
    assert "`nested/Matches 2024.parquet`.`home_team_id` → `teams.csv`.`team_id`" in report
