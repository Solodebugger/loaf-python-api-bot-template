#!/usr/bin/env python3
"""Loaf trading bot — Volume farming on terafab every 2 seconds (95% of balance)."""

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

    print(f"  Cash: {comp.cash:,.2f} USDL  (frozen {comp.frozen:,.2f})")
    print(f"  Portfolio value: {comp.portfolioValue:,.2f}  PnL: {comp.portfolioPnl:,.2f}")


# --------------------------------------------------------------------------- #
# Strategy – Buy 95% → Sell immediately, every 2 seconds
# --------------------------------------------------------------------------- #

class Strategy:
    def __init__(self, client: LoafClient, token_name: str) -> None:
        self.client = client
        self.token_name = token_name
        self._lock = threading.Lock()
        self.best_bid = None
        self.best_ask = None
        self.mark_price = None

        self.last_action_time = 0
        self.interval = 2.0                 # every 2 seconds
        self.consecutive_fails = 0
        self.success_count = 0

    def on_orderbook(self, msg) -> None:
        with self._lock:
            self.best_bid = msg.bids[0].price if msg.get("bids") else None
            self.best_ask = msg.asks[0].price if msg.get("asks") else None

    def on_mark_price(self, msg) -> None:
        with self._lock:
            self.mark_price = msg.price

    def on_trade_tick(self, msg) -> None:
        pass

    def on_my_fill(self, msg) -> None:
        t = msg.trade
        print(f"  *** FILLED: {t.side} {t.quantity} {t.tokenName} @ {t.price}")

    def on_my_order(self, msg) -> None:
        print(f"  order #{msg.orderId} → {msg.status}")

    def on_balances(self, msg) -> None:
        print(f"  balance update: cash {msg.cash:,.2f}")

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

            # 2. Get price
            with self._lock:
                price = self.mark_price or self.best_ask or self.best_bid or 100.0

            buy_value = cash * 0.95          # ← 95% of balance
            quantity = round(buy_value / price, 1)

            if quantity < 0.1:
                print(f"[{self.token_name}] Quantity too small")
                self.consecutive_fails += 1
                return

            print(f"\n[{self.token_name}] BUY {quantity} (~${buy_value:.2f}) @ ~{price}")

            # 3. Market BUY
            self.client.orders.market_buy(self.token_name, quantity=quantity)
            time.sleep(0.6)

            # 4. Market SELL
            self.client.orders.market_sell(self.token_name, quantity=quantity)

            self.success_count += 1
            self.consecutive_fails = 0
            print(f"[{self.token_name}] SELL done | Successful cycles: {self.success_count}")

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

    print(f"\n=== Trading only: terafab every 2 seconds (95% balance) ===\n")

    strategy = Strategy(client, "terafab")

    # WebSocket
    ws = client.websocket()
    ws.on_orderbook(strategy.on_orderbook)
    ws.on_mark_price(strategy.on_mark_price)
    ws.on_trades(strategy.on_trade_tick)
    ws.on_trade(strategy.on_my_fill)
    ws.on_order_status(strategy.on_my_order)
    ws.on_balances(strategy.on_balances)
    ws.on_error(lambda m: print(f"  WS error: {m.get('message')}"))

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
        ws.stop()
        client.close()


if __name__ == "__main__":
    main()
