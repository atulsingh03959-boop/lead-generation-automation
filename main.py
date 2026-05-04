from __future__ import annotations

import argparse
import time
from pathlib import Path

import schedule

from src_py.lead_automation import collect_public_leads, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lead generation automation")
    parser.add_argument("--run-once", action="store_true", help="Run pipeline once")
    parser.add_argument("--schedule", action="store_true", help="Run pipeline daily")
    parser.add_argument(
        "--time",
        default="09:00",
        help="Daily run time in HH:MM format for --schedule mode",
    )
    parser.add_argument(
        "--input",
        default="data/source_leads.csv",
        help="Path to source CSV",
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Collect fresh leads from a public dataset API before processing",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Number of leads to collect from public source when --collect is used",
    )
    parser.add_argument(
        "--output",
        default="data/lead_output.xlsx",
        help="Path to output Excel",
    )
    return parser


def execute_once(input_path: Path, output_path: Path, collect: bool, limit: int) -> None:
    if collect:
        collected_count = collect_public_leads(input_path, limit=limit)
        print(f"Collected rows from public dataset: {collected_count}")

    summary = run_pipeline(input_path=input_path, output_path=output_path)
    print("Lead automation run summary")
    print(f"Input rows: {summary.input_rows}")
    print(f"Output rows: {summary.output_rows}")
    print(f"Duplicates removed: {summary.duplicates_removed}")
    print(f"Missing emails: {summary.missing_emails}")
    print(f"Saved file: {output_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.run_once and not args.schedule:
        parser.error("Choose one mode: --run-once or --schedule")

    if args.run_once and args.schedule:
        parser.error("Use only one mode at a time")

    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.run_once:
        execute_once(input_path, output_path, args.collect, args.limit)
        return

    schedule.every().day.at(args.time).do(
        execute_once, input_path, output_path, args.collect, args.limit
    )
    print(f"Scheduler active. Daily run time: {args.time}")
    print("Running one immediate execution for smoke validation...")
    execute_once(input_path, output_path, args.collect, args.limit)
    print("Waiting for scheduled runs. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
