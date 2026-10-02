"""Top Quant Framework — Bullish swing-trading setup analysis.

A dealer-positioning-centric system for identifying high-probability
bullish swing trades across SPX 500 + NDX 100 where gamma, vanna, IV,
and price structure align.
"""

__version__ = "0.1.0"
__author__ = "Top Quant"

from .runner import TopQuantRunner
from .models import Candidate, CandidateRating

__all__ = ["TopQuantRunner", "Candidate", "CandidateRating", "__version__"]
