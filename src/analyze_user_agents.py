# src/analyze_user_agents.py
# Usage: python src/analyze_user_agents.py --input logs/splits --output out
from __future__ import annotations
from pathlib import Path
import argparse
import re
import polars as pl
from user_agents import parse as ua_parse

RE_UA = re.compile(r"\[UserAgent:\s*(?P<ua>.+?)\]")

def find_log_files(input_dir: Path) -> list[Path]:
    return [p for p in input_dir.rglob("*.log") if p.is_file()]

def parse_first_line_ua(p: Path) -> dict | None:
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            line = f.readline().strip()
        if not line:
            return None
        m = RE_UA.search(line)
        if not m:
            return None
        raw = m.group("ua")
        ua = ua_parse(raw)
        date = p.parent.name           # YYYY-MM-DD (mapnaam)
        user_id = p.stem               # bestandsnaam zonder .log
        # Normaliseer een paar namen
        browser_family = ua.browser.family or ""
        if browser_family == "Edg":
            browser_family = "Microsoft Edge"

        # Fix Windows 11 detection issue - Windows 11 also reports as NT 10.0
        os_string = f"{ua.os.family or ''} {ua.os.version_string or ''}".strip()
        if os_string == "Windows 10":
            os_string = "Windows 10/11"
        
        return {
            "date": date,
            "user_id": user_id,
            "raw_user_agent": raw,
            "browser": f"{browser_family} {ua.browser.version_string or ''}".strip(),
            "os": os_string,
            "device": (ua.device.family or "Unknown"),
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_touch_capable": ua.is_touch_capable,
            "is_pc": ua.is_pc,
            "is_bot": ua.is_bot
        }
    except Exception:
        return None

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="logs/splits", help="Folder with day/user split logs")
    ap.add_argument("--output", default="out", help="Output folder for CSV")
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    files = find_log_files(inp)
    for p in files:
        rec = parse_first_line_ua(p)
        if rec:
            rows.append(rec)

    if rows:
        df = pl.DataFrame(rows)
        # Dedup binnen (date,user_id) voor het geval van dubbele files
        df = df.unique(subset=["date", "user_id"], keep="first")
    else:
        df = pl.DataFrame(schema={
            "date": pl.Utf8, "user_id": pl.Utf8, "raw_user_agent": pl.Utf8,
            "browser": pl.Utf8, "os": pl.Utf8, "device": pl.Utf8,
            "is_mobile": pl.Boolean, "is_tablet": pl.Boolean,
            "is_touch_capable": pl.Boolean, "is_pc": pl.Boolean, "is_bot": pl.Boolean
        })

    df.write_csv(out / "user_agents.csv")
    # Een paar simpele aggregaten alvast
    if df.height > 0:
        (df.group_by(["date","browser"])
           .agg(pl.n_unique("user_id").alias("users_count"))
           .write_csv(out / "agg_browsers_by_date.csv"))
        (df.group_by(["date","os"])
           .agg(pl.n_unique("user_id").alias("users_count"))
           .write_csv(out / "agg_os_by_date.csv"))
        (df.group_by(["date","device"])
           .agg(pl.n_unique("user_id").alias("users_count"))
           .write_csv(out / "agg_devices_by_date.csv"))
    else:
        # lege bestanden met headers
        pl.DataFrame({"date":[], "browser":[], "users_count":[]}).write_csv(out / "agg_browsers_by_date.csv")
        pl.DataFrame({"date":[], "os":[], "users_count":[]}).write_csv(out / "agg_os_by_date.csv")
        pl.DataFrame({"date":[], "device":[], "users_count":[]}).write_csv(out / "agg_devices_by_date.csv")

    print(f"Scanned files: {len(files)} | Exported rows: {df.height} -> {out/'user_agents.csv'}")

if __name__ == "__main__":
    main()
