"""Try the bill reader on a real photo (needs ANTHROPIC_API_KEY or `ant auth login`).

Usage: cd backend && uv run python -m scripts.try_bill path/to/bill.jpg [--analyse]

Prints what the AI read, the plausibility warnings, and with --analyse the waste check, the
plan before/after and the Bosnian board text for the sample club. The photo is sent to the Claude
API (and nowhere else); use a bill you are allowed to share, not a customer's.
"""

import json
import sys
from pathlib import Path

from app.services import advisor, bill_reader


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    reading = bill_reader.read_bill(Path(args[0]).read_bytes())
    print(json.dumps(reading.model_dump(), indent=2, ensure_ascii=False))
    for w in bill_reader.plausibility_warnings(reading):
        print("WARNING:", w)
    if "--analyse" in sys.argv:
        bill = {
            "kind": reading.kind,
            "period_year": reading.period_year,
            "period_month": reading.period_month,
            "kwh": reading.kwh_total,
            "amount_km": reading.amount_total_km,
            "unit_price_km_per_kwh": reading.unit_price_km_per_kwh,
            "litres": reading.litres,
            "fuel_type": reading.fuel_type if reading.fuel_type in ("diesel", "petrol") else None,
        }
        print("\n" + advisor.analyse_bill(None, bill)["board_text_bs"])


if __name__ == "__main__":
    main()
