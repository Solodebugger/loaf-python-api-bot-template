"""String enums for the Loaf API.

All values are exact, case-sensitive literals accepted/returned by the API.
Each enum subclasses ``str`` so a member is interchangeable with its string
value::

    >>> OrderSide.BUY == "BUY"
    True
    >>> json.dumps({"side": OrderSide.BUY})
    '{"side": "BUY"}'

You can always pass a plain string instead of an enum member.
"""

from __future__ import annotations

from enum import Enum


class _StrEnum(str, Enum):
    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.value


class OrderSide(_StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(_StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TimeInForce(_StrEnum):
    #: Good-til-cancelled. The default; recommended for bots.
    GTC = "GTC"
    #: Immediate-or-cancel.
    IOC = "IOC"
    #: Fill-or-kill.
    FOK = "FOK"
    #: Good-til-date. Requires a future unix-seconds ``deadline``.
    GTD = "GTD"


class OrderStatus(_StrEnum):
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class TradeStatus(_StrEnum):
    SETTLING = "SETTLING"
    SETTLED = "SETTLED"
    SETTLEMENT_FAILED = "SETTLEMENT_FAILED"


class OfferingOrderStatus(_StrEnum):
    """Status of an IPO/offering subscription order."""

    PENDING = "PENDING"
    ALLOCATED = "ALLOCATED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PropertyStatus(_StrEnum):
    PENDING = "PENDING"
    LIVE = "LIVE"
    DELISTED = "DELISTED"


class IpoStatus(_StrEnum):
    PENDING = "PENDING"
    LIVE = "LIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class TransferType(_StrEnum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class TransferStatus(_StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class PropertyType(_StrEnum):
    HOUSE = "HOUSE"
    APARTMENT = "APARTMENT"
    DUPLEX = "DUPLEX"
    TERRACE = "TERRACE"
    TOWNHOUSE = "TOWNHOUSE"
    VILLA = "VILLA"
    RETIRE = "RETIRE"
    LANDMARK = "LANDMARK"


class WSMessageType(_StrEnum):
    """`type` discriminator on every WebSocket frame."""

    # lifecycle
    CONNECTION = "connection"
    AUTH = "auth"
    AUTH_RESULT = "auth_result"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SUBSCRIPTION_CONFIRMED = "subscription_confirmed"
    ERROR = "error"
    ECHO = "echo"
    # public market data
    ORDERBOOK_UPDATE = "orderbook_update"
    TRADES_BATCH = "trades_batch"
    CANDLE_UPDATE = "candle_update"
    MARK_PRICE = "mark_price"
    IPO_ALLOCATION_UPDATE = "ipo_allocation_update"
    # private portfolio deltas
    BALANCES_UPDATE = "balances_update"
    POSITION_UPDATE = "position_update"
    ORDER_STATUS = "order_status"
    ORDER_UPDATE = "order_update"
    TRADE_NEW = "trade_new"
    TRANSFER_UPDATE = "transfer_update"
    OFFERING_ORDER_UPDATE = "offering_order_update"
