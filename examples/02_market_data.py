"""02 — Public market data (no API key needed).

    python examples/02_market_data.py
"""

from __future__ import annotations

from loaf import LoafClient

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def main() -> None:
    # Market data is public — anonymous client is fine.
    client = LoafClient()

    properties = client.market.properties().get("properties") or []
    print(f"{len(properties)} properties listed:\n")
    for prop in properties[:10]:
        print(f"  {prop.tokenName:<12} {prop.ticker:<8} "
              f"price={prop.marketPrice}  24h vol={prop.volume24h}  status={prop.status}")

    if not properties:
        return

    token = properties[0].tokenName
    print(f"\n--- detail for {token} ---")
    detail = client.market.property(token)
    book = detail.get("orderBook")
    if book:
        best_bid = book.bids[0] if book.get("bids") else None
        best_ask = book.asks[0] if book.get("asks") else None
        print(f"  best bid: {best_bid}")
        print(f"  best ask: {best_ask}")
    candles = detail.get("candlesticks") or []
    print(f"  {len(candles)} candles; latest: {candles[-1] if candles else 'n/a'}")

    print("\n--- latest news ---")
    for article in (client.market.news() or [])[:3]:
        print(f"  {article.title}")

    client.close()


if __name__ == "__main__":
    main()
