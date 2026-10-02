"""Top Quant usage example."""

from top_quant import TopQuantRunner
from top_quant.config import ScreeningConfig, DataSourceConfig

# Example 1: Run with defaults (mock data)
runner = TopQuantRunner()
report = runner.run()

# Print formatted report
print(runner.format_report(report))

# Example 2: Access candidates programmatically
print("\n--- Candidates by Rating ---")
for candidate in report.ranked_board():
    if candidate.rating.value != "❌ PASS":
        print(f"{candidate.symbol}: {candidate.rating.value} (Score: {candidate.raw_score:.1f})")

# Example 3: Custom configuration
config = ScreeningConfig(
    enforce_hard_filters=True,
    use_research_range=False
)
data_config = DataSourceConfig(
    quantwheel_api_key="YOUR_KEY_HERE",
    allow_mock_data=True  # Fall back to mock if API unavailable
)

runner_custom = TopQuantRunner(config, data_config)
report_custom = runner_custom.run()

# Example 4: Export specific section
a_plus_candidates = report.get_by_rating(__import__("top_quant.models", fromlist=["CandidateRating"]).CandidateRating.A_PLUS_PRIME)
print(f"\nA+ PRIME candidates: {len(a_plus_candidates)}")
for c in a_plus_candidates:
    print(f"  {c.symbol}: ${c.spot:.2f} | RR: {c.calcs.positioning_rr:.2f}x | Runway: {c.runway.value}")
