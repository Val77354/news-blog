"""Allowed values. Keep in sync with frontend/src/constants.js."""

from typing import Literal

Category = Literal["Technology", "Business", "World", "Science", "Sports"]

Country = Literal[
    "United Kingdom",
    "France",
    "Germany",
    "Italy",
    "Spain",
    "Netherlands",
    "Poland",
    "Sweden",
    "Ukraine",
    "Greece",
    "Portugal",
    "Switzerland",
]

PodcastSource = Literal["YouTube", "Spotify", "Apple Podcasts", "SoundCloud", "Other"]
