"""Top Quant CLI — Command-line interface."""

import sys
import argparse
from datetime import datetime
from .runner import TopQuantRunner
from .config import ScreeningConfig, DataSourceConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Top Quant — Bullish swing-trading framework"
    )
    parser.add_argument(
        "--run", "-r",
        action="store_true",
        help="Run Top Quant daily analysis"
    )
    parser.add_argument(
        "--quantwheel-key",
        default=None,
        help="QuantWheel API key (or set QUANTWHEEL_API_KEY env var)"
    )
    parser.add_argument(
        "--flashalpha-key",
        default=None,
        help="FlashAlpha API key (or set FLASHALPHA_API_KEY env var)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use mock data (default: True)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Save report to file (default: print to stdout)"
    )
    parser.add_argument(
        "--hard-filters",
        action="store_true",
        default=True,
        help="Enforce hard filters (default: True)"
    )

    args = parser.parse_args()

    if not args.run:
        parser.print_help()
        return 0

    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                  TOP QUANT FRAMEWORK v0.1.0                        ║")
    print("║                  Starting daily analysis...                        ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    # Setup configs
    screening_config = ScreeningConfig(enforce_hard_filters=args.hard_filters)
    data_config = DataSourceConfig(
        quantwheel_api_key=args.quantwheel_key,
        flashalpha_api_key=args.flashalpha_key,
        allow_mock_data=args.mock
    )

    # Run analysis
    try:
        runner = TopQuantRunner(screening_config, data_config)
        report = runner.run()

        # Format and output
        formatted = runner.format_report(report)

        if args.output:
            with open(args.output, "w") as f:
                f.write(formatted)
            print(f"✓ Report saved to {args.output}\n")
        else:
            print(formatted)

        # Summary stats
        total = len(report.candidates)
        a_plus = len(report.get_by_rating(__import__("top_quant.models", fromlist=["CandidateRating"]).CandidateRating.A_PLUS_PRIME))
        a = len(report.get_by_rating(__import__("top_quant.models", fromlist=["CandidateRating"]).CandidateRating.A))
        watch = len(report.get_by_rating(__import__("top_quant.models", fromlist=["CandidateRating"]).CandidateRating.WATCH))

        print(f"\n{'='*70}")
        print(f"Summary: {total} total | 🔥 {a_plus} A+ | 🟢 {a} A | 🟡 {watch} WATCH")
        print(f"{'='*70}\n")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
