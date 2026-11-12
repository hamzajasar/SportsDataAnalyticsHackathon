from app.services import datasets
from app.services.datasets import table_name


def test_table_name():
    assert table_name("nested/Matches 2024.parquet") == "nested_matches_2024"
    assert table_name("2024.csv") == "t_2024"
    assert table_name("transfermarkt/games.csv.gz") == "transfermarkt_games"


def test_gzip_csv_supported(sample_data_dir):
    import gzip

    raw = sample_data_dir / "raw"
    with gzip.open(raw / "games.csv.gz", "wt") as f:
        f.write("game_id,attendance" + chr(10) + "1,500" + chr(10) + "2," + chr(10))
    assert "games.csv.gz" in [d.id for d in datasets.list_datasets()]
    assert datasets.summarize("games.csv.gz")["rows"] == 2


def test_profile_script(sample_data_dir, capsys):
    from scripts.profile_data import main

    main()
    out = capsys.readouterr().out
    assert "teams.csv" in out
    report = (sample_data_dir / "processed" / "_profile.md").read_text()
    assert "team_id" in report
    assert "teams.csv`.`team_id` → `teams_excel.xlsx`.`team_id` — 100% of values match" in report
    assert "`nested/Matches 2024.parquet`.`home_team_id` → `teams.csv`.`team_id`" in report
