# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass

class Command:
    pass

@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: str
    eta: Optional[date] = None

@dataclass
class ChangeBatchQuantity(Command):
    ref: str
    qty: int

@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int
