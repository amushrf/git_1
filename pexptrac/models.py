from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class Expense:
    id: int
    amount: Decimal
    category: str
    date: date
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["amount"] = str(self.amount)
        data["date"] = self.date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Expense":
        return cls(
            id=int(data["id"]),
            amount=Decimal(str(data["amount"])),
            category=str(data["category"]),
            date=date.fromisoformat(str(data["date"])),
            note=str(data.get("note", "")),
        )
