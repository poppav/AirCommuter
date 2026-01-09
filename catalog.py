from typing import List, Dict


def aircraft_catalog() -> List[Dict]:
	# Prices in USD; capacities, rough range (nm), and hourly cost are illustrative
	# max_seats_per_row and max_rows based on real-world aircraft configurations
	# For smaller planes only: oil_capacity (quarts) and oil_minimum (quarts)
	# Airliners don't require oil tracking - oil is managed automatically by maintenance
	return [
		{"type_code": "C337", "name": "Cessna 337 Skymaster", "price": 180000, "capacity": 5, "range_nm": 1308, "hourly_cost": 20, "max_duration_hours": 6, "max_seats_per_row": 2, "max_rows": 3, "oil_capacity": 24.0, "oil_minimum": 7.0},
		{"type_code": "BE58", "name": "Baron 58", "price": 250000, "capacity": 5, "range_nm": 860, "hourly_cost": 20, "max_duration_hours": 6, "max_seats_per_row": 2, "max_rows": 3, "oil_capacity": 24.0, "oil_minimum": 5.0},
		{"type_code": "C404", "name": "Cessna 404 Titan", "price": 400000, "capacity": 10, "range_nm": 1843, "hourly_cost": 40, "max_duration_hours": 9, "max_seats_per_row": 2, "max_rows": 5, "oil_capacity": 20.0, "oil_minimum": 6.0},
		{"type_code": "C90B", "name": "Beechcraft King Air 90", "price": 600000, "capacity": 6, "range_nm": 1039, "hourly_cost": 100, "max_duration_hours": 6, "max_seats_per_row": 2, "max_rows": 3, "oil_capacity": 18.0, "oil_minimum": 7.0},
		{"type_code": "DHC6", "name": "De Havilland Canada DHC-6 Twin Otter", "price": 1000000, "capacity": 19, "range_nm": 650, "hourly_cost": 200, "max_duration_hours": 9, "max_seats_per_row": 3, "max_rows": 7, "oil_capacity": 18.0, "oil_minimum": 6.0},
		{"type_code": "B190", "name": "Beechcraft 1900", "price": 1500000, "capacity": 19, "range_nm": 1476, "hourly_cost": 140, "max_duration_hours": 6, "max_seats_per_row": 3, "max_rows": 7},
		{"type_code": "L410", "name": "Turbolet L410", "price": 1000000, "capacity": 19, "range_nm": 294, "hourly_cost": 140, "max_duration_hours": 5.0, "max_seats_per_row": 3, "max_rows": 7, "oil_capacity": 16.0, "oil_minimum": 6.0},
		{"type_code": "B350", "name": "Beechcraft King Air 350", "price": 1850000, "capacity": 8, "range_nm": 2000, "hourly_cost": 155, "max_duration_hours": 4.5, "max_seats_per_row": 2, "max_rows": 4},
		{"type_code": "M700", "name": "Piper 700 Aerostar", "price": 300000, "capacity": 5, "range_nm": 644, "hourly_cost": 40, "max_duration_hours": 7.0, "max_seats_per_row": 2, "max_rows": 3},
		{"type_code": "C208", "name": "Cessna 208 Caravan", "price": 2500000, "capacity": 12, "range_nm": 1200, "hourly_cost": 30, "max_duration_hours": 5.5, "max_seats_per_row": 3, "max_rows": 4, "oil_capacity": 16.0, "oil_minimum": 6.0},
		{"type_code": "E55P", "name": "Embraer Phenom 300", "price": 5000000, "capacity": 8, "range_nm": 2010, "hourly_cost": 170, "max_duration_hours": 4.5, "max_seats_per_row": 2, "max_rows": 4},
		{"type_code": "AT72", "name": "ATR 72-600", "price": 14000000, "capacity": 70, "range_nm": 825, "hourly_cost": 360, "max_duration_hours": 3.5, "max_seats_per_row": 4, "max_rows": 20, "oil_capacity": 24.0, "oil_minimum": 10.0},
		{"type_code": "E190", "name": "Embraer E190", "price": 30000000, "capacity": 100, "range_nm": 1600, "hourly_cost": 360, "max_duration_hours": 4.5, "max_seats_per_row": 4, "max_rows": 28},
		{"type_code": "A320", "name": "Airbus A320-200", "price": 51000000, "capacity": 150, "range_nm": 3300, "hourly_cost": 560, "max_duration_hours": 6.5, "max_seats_per_row": 6, "max_rows": 40},
		{"type_code": "B738", "name": "Boeing 737-800", "price": 48000000, "capacity": 162, "range_nm": 2935, "hourly_cost": 520, "max_duration_hours": 6.5, "max_seats_per_row": 6, "max_rows": 40},
	]


