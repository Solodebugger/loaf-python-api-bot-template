"""Public market data: properties, info pages, news.

None of these require authentication — they work with an anonymous client.
All currency values are plain dollars and quantities plain tokens (see
:mod:`loaf.money`).
"""

from __future__ import annotations

from typing import Any

from .base import Resource


class MarketResource(Resource):
    # -- Properties / trade ------------------------------------------------ #

    def properties(self) -> Any:
        """``GET /trade`` — every property with market data + a 24h sparkline.

        Returns ``{"properties": [...]}``. Each item has ``propertyId``,
        ``tokenName``, ``ticker``, ``marketPrice``, ``dailyReferencePrice``,
        ``volume24h``, ``status``, ``candlesticks`` (hourly OHLCV), etc.
        """
        return self._client.get("/trade", auth=False)

    def property(self, token_name: str) -> Any:
        """``GET /trade/{token_name}`` — full detail for one property.

        Returns the property, full candlestick history, current ``orderBook``
        snapshot (``bids``/``asks`` price levels, may be ``null``),
        ``recentTrades``, ``volume24h``, ``dailyReferencePrice`` and market-hours
        metadata. ``token_name`` is lowercase letters only.
        """
        return self._client.get(f"/trade/{token_name}", auth=False)

    # -- Info pages -------------------------------------------------------- #

    def info_header(self, token_name: str) -> Any:
        """``GET /info/{token_name}/header`` — address, hero image, bed/bath/car, offering valuation."""
        return self._client.get(f"/info/{token_name}/header", auth=False)

    def info_overview(self, token_name: str) -> Any:
        """``GET /info/{token_name}/overview`` — description, media, metrics, amenities."""
        return self._client.get(f"/info/{token_name}/overview", auth=False)

    def info_documents(self, token_name: str) -> Any:
        """``GET /info/{token_name}/documents`` — public document list (title + URL)."""
        return self._client.get(f"/info/{token_name}/documents", auth=False)

    # -- News -------------------------------------------------------------- #

    def news(self) -> Any:
        """``GET /news`` — up to 10 latest positive-sentiment articles (a bare list)."""
        return self._client.get("/news", auth=False)
