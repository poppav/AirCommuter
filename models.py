from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Aircraft:
	id: str
	type_code: str
	name: str
	purchase_price: int
	hours_since_maintenance: float = 0.0
	maintenance_due_hours: float = 300.0
	location: str = "HOME"


@dataclass
class Loan:
	loan_id: str
	principal: int
	interest_rate_apr: float
	remaining_balance: int
	monthly_payment: int


@dataclass
class Booking:
	booking_id: str
	route: str
	passengers: int
	ticket_price: int
	assigned_aircraft_id: Optional[str] = None
	is_completed: bool = False


@dataclass
class Company:
	name: str
	cash: int = 0
	fleet: List[Aircraft] = field(default_factory=list)
	loans: List[Loan] = field(default_factory=list)
	bookings: List[Booking] = field(default_factory=list)
	parking: Dict[str, Dict[str, int]] = field(default_factory=dict)  # airport -> {spots, hangars}


