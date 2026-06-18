"""Typed descriptions of the documented response shapes.

These are :class:`typing.TypedDict` definitions used purely for editor
autocomplete, type-checking and documentation. At runtime the SDK returns
:class:`~loaf._object.LoafObject` instances (dicts), which also support
attribute access (``order.price``). New/extra fields the backend adds are
preserved at runtime even though they are not listed here.

Every monetary field is in plain dollars and every quantity in plain tokens
unless explicitly noted (see :mod:`loaf.money`). Timestamps are unix seconds.
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class PriceLevel(TypedDict):
    price: float  # dollars
    quantity: float  # tokens


class OrderBook(TypedDict, total=False):
    propertyId: int
    bids: list[PriceLevel]
    asks: list[PriceLevel]


class Candle(TypedDict):
    time: int  # unix seconds (bucket start)
    open: float
    high: float
    low: float
    close: float
    volume: float  # tokens


class TradeTick(TypedDict, total=False):
    """A public trade (from a property detail page or the ``trades`` WS channel)."""

    tradeId: int
    propertyId: int
    aggressorSide: str  # OrderSide of the taker
    price: float
    quantity: float
    timestamp: int


class OrderResult(TypedDict, total=False):
    """Response to ``POST /orders`` and the cancel endpoints (exchange acknowledgement)."""

    success: bool
    orderId: int
    errorMessage: str


class OrderNonce(TypedDict):
    nonce: str  # 32 hex chars
    deadline: int  # unix seconds (nonce expiry hint, NOT the order deadline)


class CancelAllResult(TypedDict, total=False):
    requestedCount: int
    cancelledOrderIds: list[int]
    failedOrders: list[dict[str, Any]]  # [{orderId, errorMessage}]


class OrderHistoryItem(TypedDict, total=False):
    id: int
    propertyId: int
    tokenName: str
    side: str  # OrderSide
    type: str  # OrderType
    timeInForce: str
    quantity: float
    price: Optional[float]  # None for market orders
    status: str  # OrderStatus
    filledQuantity: float
    rejectionReason: Optional[str]
    deadline: int
    filledAt: Optional[int]
    cancelledAt: Optional[int]
    createdAt: int


class TradeHistoryItem(TypedDict, total=False):
    tradeId: int
    propertyId: int
    tokenName: str
    txHash: str
    side: str  # OrderSide, relative to this user
    quantity: float
    price: float
    fee: float  # this user's fee, dollars
    executedAt: int
    status: str  # TradeStatus


class Position(TypedDict, total=False):
    propertyId: int
    tokenName: str
    quantity: float  # tradeable (total minus frozen)
    totalQuantity: float
    averageEntryPrice: float
    marketPrice: float
    percentChange: float  # plain percent
    percentOfPortfolio: float
    propertyPnl: float
    propertyPnlPercent: float
    isIpoAllocation: bool
    imageUrl: str


class PortfolioComponent(TypedDict, total=False):
    cash: float
    frozen: float
    portfolioValue: float
    portfolioPnl: float
    portfolioPnlPercent: float
    positions: list[Position]
    applicableFees: dict[str, int]  # {takerFeeBps, makerFeeBps}
    offeringOrders: list[dict[str, Any]]
    openOrders: list[OrderHistoryItem]
    tradeHistory: list[TradeHistoryItem]
    orderHistory: list[OrderHistoryItem]
    transfers: list[dict[str, Any]]


class IpoSubscribeResult(TypedDict, total=False):
    success: bool
    subscriptionId: int  # the IPO order id to track
    allocatedQuantity: float  # may be less than requested if partial
    errorMessage: str


class LeaderboardEntry(TypedDict, total=False):
    rank: int
    handle: Optional[str]
    walletAddress: str
    points: float
    volume: float  # whole USDC
    pnl: float  # whole USDC


__all__ = [
    "PriceLevel",
    "OrderBook",
    "Candle",
    "TradeTick",
    "OrderResult",
    "OrderNonce",
    "CancelAllResult",
    "OrderHistoryItem",
    "TradeHistoryItem",
    "Position",
    "PortfolioComponent",
    "IpoSubscribeResult",
    "LeaderboardEntry",
]
