"""Competition leaderboard (public)."""

from __future__ import annotations

from typing import Any

from .base import Resource


class LeaderboardResource(Resource):
    def get(self) -> Any:
        """``GET /leaderboard`` — the current competition leaderboard. (public)

        Returns ``{roundNumber, roundName, roundStatus, volumeMultiplierTiers,
        updatedAt, nextUpdateAt, entries}`` where each entry has ``rank``,
        ``handle``, ``walletAddress``, ``points``, ``volume``, ``pnl`` (all in
        whole USDC, rounded to cents). Serves a live board while a round is
        ``ACTIVE`` or the last round's frozen snapshot between rounds. Cached —
        poll at ``nextUpdateAt``. Raises 404 when no round/snapshot exists.
        """
        return self._client.get("/leaderboard", auth=False)
