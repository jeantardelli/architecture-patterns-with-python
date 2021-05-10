from dataclasses import dataclass

class Event:
    pass

@dataclass
class OufOfStock(Event):
    sku: str
