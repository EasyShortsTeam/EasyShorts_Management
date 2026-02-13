"""In-memory mock store.

This is intentionally simple to let frontend integration proceed early.
Replace with real DB layer later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MockStore:
    series: list[dict]
    episodes: list[dict]
    shorts: list[dict]


store = MockStore(
    series=[
        {"id": "s_001", "title": "Demo Series", "description": "mock series"},
    ],
    episodes=[
        {"id": "e_001", "series_id": "s_001", "title": "Ep 1", "status": "ready"},
    ],
    shorts=[
        {"id": "sh_001", "title": "Demo Short", "status": "draft"},
    ],
)
