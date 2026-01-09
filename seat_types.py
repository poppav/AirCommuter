from typing import List, Dict


def get_seat_types() -> List[Dict]:
	"""Returns available seat types with installation cost and comfort rating."""
	return [
		{"code": "SLIM", "name": "Slimline HD", "cost_per_seat": 500, "comfort": 1.0, "color": "#e0e0e0"},
		{"code": "RECL", "name": "Recliner Shorthaul", "cost_per_seat": 1500, "comfort": 1.5, "color": "#b3d9ff"},
		{"code": "LIE140", "name": "Lie Flat 140°", "cost_per_seat": 3500, "comfort": 2.5, "color": "#ffd9b3"},
		{"code": "LIE180", "name": "Full Lie Flat", "cost_per_seat": 6000, "comfort": 3.5, "color": "#ffb3d9"},
		{"code": "BUSINESS", "name": "Business Class", "cost_per_seat": 2500, "comfort": 2.0, "color": "#d9b3ff"},
		{"code": "PREMIUM", "name": "Premium Economy", "cost_per_seat": 1000, "comfort": 1.3, "color": "#b3ffd9"},
	]


def get_seat_type(code: str) -> Dict:
	"""Get a specific seat type by code."""
	for st in get_seat_types():
		if st["code"] == code:
			return st
	return get_seat_types()[0]  # Default to first


def calculate_cabin_cost(layout: List[Dict]) -> int:
	"""Calculate total installation cost for a cabin layout."""
	total = 0
	for row in layout:
		seat_type = get_seat_type(row.get("seat_type", "SLIM"))
		seats_per_row = int(row.get("seats", 6))
		total += seat_type["cost_per_seat"] * seats_per_row
	return total


def calculate_cabin_total_seats(layout: List[Dict]) -> int:
	"""Calculate total number of seats in the cabin layout."""
	if not layout:
		return 0
	return sum(int(row.get("seats", 0)) for row in layout)


def calculate_cabin_comfort(layout: List[Dict]) -> float:
	"""Calculate average comfort rating for the cabin."""
	if not layout:
		return 1.0
	total_comfort = 0
	total_seats = 0
	for row in layout:
		seat_type = get_seat_type(row.get("seat_type", "SLIM"))
		seats = int(row.get("seats", 6))
		total_comfort += seat_type["comfort"] * seats
		total_seats += seats
	return total_comfort / total_seats if total_seats > 0 else 1.0


def get_default_layout(capacity: int, max_seats_per_row: int = 6, max_rows: int = 40) -> List[Dict]:
	"""Generate a default economy layout for given capacity, respecting aircraft limits."""
	seats_per_row = min(max_seats_per_row, capacity)  # Use max seats per row, but don't exceed capacity in one row
	rows = max(1, min(max_rows, (capacity + seats_per_row - 1) // seats_per_row))  # Calculate rows needed, capped at max_rows
	layout = []
	total_seats = 0
	for i in range(rows):
		remaining = capacity - total_seats
		if remaining <= 0:
			break
		# Last row might have fewer seats if needed
		seats_in_row = min(seats_per_row, remaining)
		layout.append({"row": i + 1, "seat_type": "SLIM", "seats": seats_in_row})
		total_seats += seats_in_row
	return layout

