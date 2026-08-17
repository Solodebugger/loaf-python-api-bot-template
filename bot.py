#!/usr/bin/env python3
"""Loaf trading bot — Volume farming on terafab every 2 seconds (5% of balance)."""
from __future__ import annotations

import os
import signal
import sys
import threading
import time
from typing import Any

import loaf
from loaf import LoafClient

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TARGET_TOKEN_NAME = "terafab"
USER_ID = os.environ.get("LOAF_USER_ID", "")


def build_client() -> LoafClient:
    api_key = os.environ.get("LOAF_API_KEY")
    if not api_key:
        sys.exit("No LOAF_API_KEY set.")
    return LoafClient(api_key=api_key)


# --------------------------------------------------------------------------- #
# Preflight
# --------------------------------------------------------------------------- #
def preflight(client: LoafClient) -> None:
    try:
        comp = client.portfolio.component()
    except loaf.LoafAuthError as exc:
        sys.exit(f"Authentication failed — check your API key. ({exc.message})")
    print(f" Cash: {comp.cash:,.2f} USDL (frozen {comp.frozen:,.2f})")
    print(f" Portfolio value: {comp.portfolioValue:,.2f} PnL: {comp.portfolioPnl:,.2f}")


# --------------------------------------------------------------------------- #
# Strategy – Buy 5% → Sell immediately, every 2 seconds
# --------------------------------------------------------------------------- #
class Strategy:
    def __init__(self, client: LoafClient, token_name: str) -> None:
        self.client = client
        self.token_name = token_name
        self._lock = threading.Lock()
        self.best_bid = None
        self.best_ask = None
        self.mark_price = None
        self.last_action_time = 0.0
        self.interval = 2.0          # every 2 seconds
        self.consecutive_fails = 0
        self.success_count = 0

    def on_orderbook(self, msg) -> None:
        with self._lock:
            bids = msg.get("bids") or []
            asks = msg.get("asks") or []
            self.best_bid = bids[0].price if bids else None
            self.best_ask = asks[0].price if asks else None

    def on_mark_price(self, msg) -> None:
        with self._lock:
            self.mark_price = msg.price

    def on_trade_tick(self, msg) -> None:
        pass

    def on_my_fill(self, msg) -> None:
        t = msg.trade
        print(f" *** FILLED: {t.side} {t.quantity} {t.tokenName} @ {t.price}")

    def on_my_order(self, msg) -> None:
        print(f" order #{msg.orderId} → {msg.status}")

    def on_balances(self, msg) -> None:
        print(f" balance update: cash {msg.cash:,.2f}")

    def _get_held_quantity(self) -> float:
        """Return current position size for this token (0 if none)."""
        try:
            portfolio = self.client.portfolio.component()
            positions = portfolio.get("positions") or []
            for p in positions:
                if getattr(p, "tokenName", None) == self.token_name:
                    return float(getattr(p, "quantity", 0) or 0)
        except Exception:
            pass
        return 0.0

    def on_tick(self) -> None:
        now = time.time()
        if now - self.last_action_time < self.interval:
            return
        self.last_action_time = now

        try:
            # 1. Get cash
            portfolio = self.client.portfolio.component()
            cash = float(getattr(portfolio, "cash", 0) or 0)
            if cash < 5:
                print(f"[{self.token_name}] Low cash: {cash:.2f}")
                self.consecutive_fails += 1
                return

            # 2. Get price – skip if we have none yet
            with self._lock:
                price = self.mark_price or self.best_ask or self.best_bid
            if price is None or price <= 0:
                print(f"[{self.token_name}] No price data yet – skipping")
                return

            buy_value = cash * 0.05          # ← 5% of balance
            quantity = round(buy_value / price, 1)
            if quantity < 0.1:
                print(f"[{self.token_name}] Quantity too small")
                self.consecutive_fails += 1
                return

            print(f"\n[{self.token_name}] BUY {quantity} (~${buy_value:.2f}) @ ~{price}")

            # 3. Market BUY
            self.client.orders.market_buy(self.token_name, quantity=quantity)

            # Wait a moment and then sell only what we actually hold
            # (fixes the main race condition)
            time.sleep(0.8)
            held = self._get_held_quantity()
            sell_qty = round(held, 1)

            if sell_qty >= 0.1:
                print(f"[{self.token_name}] SELL {sell_qty}")
                self.client.orders.market_sell(self.token_name, quantity=sell_qty)
                self.success_count += 1
                self.consecutive_fails = 0
                print(f"[{self.token_name}] SELL done | Successful cycles: {self.success_count}")
            else:
                print(f"[{self.token_name}] No position to sell after buy (held={held})")
                self.consecutive_fails += 1

        except Exception as e:
            print(f"[{self.token_name}] ERROR: {e}")
            self.consecutive_fails += 1


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    client = build_client()
    print(f"Connecting to {client.base_url} ...")
    preflight(client)

    print(f"\n=== Trading only: terafab every 2 seconds (5% balance) ===\n")
    strategy = Strategy(client, "terafab")

    # WebSocket
    ws = client.websocket()
    ws.on_orderbook(strategy.on_orderbook)
    ws.on_mark_price(strategy.on_mark_price)
    ws.on_trades(strategy.on_trade_tick)
    ws.on_trade(strategy.on_my_fill)
    ws.on_order_status(strategy.on_my_order)
    ws.on_balances(strategy.on_balances)
    ws.on_error(lambda m: print(f" WS error: {m.get('message')}"))

    ws.subscribe_orderbook("terafab")
    ws.subscribe_mark_price("terafab")
    ws.subscribe_trades("terafab")
    if USER_ID:
        ws.subscribe_portfolio(int(USER_ID))

    ws.start()
    ws.wait_until_connected(timeout=10)
    print("Live feed connected. Starting volume farming...\n")

    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())

    try:
        while not stop.is_set():
            strategy.on_tick()
            stop.wait(0.5)
    finally:
        print("\nShutting down ...")
        # Optional: flatten any leftover position
        try:
            held = strategy._get_held_quantity()
            if held >= 0.1:
                print(f"Flattening remaining {held} {TARGET_TOKEN_NAME}")
                client.orders.market_sell(TARGET_TOKEN_NAME, quantity=round(held, 1))
        except Exception as e:
            print(f"Cleanup sell failed: {e}")
        ws.stop()
        client.close()


if __name__ == "__main__":
    main()
