import uuid
import time
import hashlib
from typing import Dict, List, Any, Optional
from storage import load_state, save_state


def _now_ts() -> int:
	return int(time.time())


def _day_now() -> int:
	return int(time.time() // 86400)


def _new_id(prefix: str) -> str:
	return f"{prefix}_{uuid.uuid4().hex[:8]}"


def get_state() -> Dict[str, Any]:
	state = load_state()
	state.setdefault("company", {"name": ""})
	if "reputation" not in state.get("company", {}):
		state["company"]["reputation"] = 0.0  # Start at 0/100
	state.setdefault("cash", 0)
	state.setdefault("fleet", [])
	state.setdefault("loans", [])
	state.setdefault("bookings", [])
	state.setdefault("parking", {})
	state.setdefault("active_flights", [])
	state.setdefault("ledger", [])
	state.setdefault("aircraft_config", {})  # Overrides for max_duration_hours per type_code
	state.setdefault("pilots", [])  # List of pilot dicts
	state.setdefault("achievements", [])  # List of achievement IDs earned
	state.setdefault("fuel_price_multiplier", 1.0)  # Current fuel price multiplier
	state.setdefault("route_stats", {})  # Route profitability tracking
	state.setdefault("completed_flights", [])  # Historical flight records
	state.setdefault("last_daily_tick_day", _day_now())  # Last day daily tick was processed
	return state


def _add_ledger(state: Dict, category: str, amount: int, note: str) -> None:
	ledger = state.setdefault("ledger", [])
	entry = {
		"ts": _now_ts(),
		"category": category,
		"amount": amount,
		"note": note,
	}
	ledger.append(entry)
	# Keep last 1000 entries
	if len(ledger) > 1000:
		ledger[:] = ledger[-1000:]


def _has_owned_parking(state: Dict, airport: str) -> bool:
	parking = state.get("parking", {})
	info = parking.get(airport.upper(), {})
	# Support both old format (int) and new format (list)
	spots = info.get("spots", 0)
	if isinstance(spots, list):
		spot_count = len(spots)
	else:
		spot_count = int(spots)
	hangars = info.get("hangars", 0)
	if isinstance(hangars, list):
		hangar_count = len(hangars)
	else:
		hangar_count = int(hangars)
	return spot_count > 0 or hangar_count > 0


def has_owned_parking_at_airport(airport: str) -> bool:
	"""Check if the company owns parking or hangars at the given airport.
	
	Args:
		airport: Airport code (e.g., "HOME", "JFK")
	
	Returns:
		True if company owns at least one parking spot or hangar at the airport
	"""
	state = get_state()
	return _has_owned_parking(state, airport)


def has_hangar_at_airport(airport: str) -> bool:
	"""Check if the company owns at least one hangar at the given airport.
	
	Args:
		airport: Airport code (e.g., "HOME", "JFK")
	
	Returns:
		True if company owns at least one hangar at the airport
	"""
	state = get_state()
	parking = state.get("parking", {})
	info = parking.get(airport.upper(), {})
	hangars = info.get("hangars", 0)
	if isinstance(hangars, list):
		hangar_count = len(hangars)
	else:
		hangar_count = int(hangars)
	return hangar_count > 0


def _has_available_parking(state: Dict, airport: str) -> bool:
	# HOME airport has unlimited parking (home base)
	if airport.upper() == "HOME":
		return True
	
	parking = state.get("parking", {})
	info = parking.get(airport.upper(), {})
	# Support both old format (int) and new format (list)
	spots = info.get("spots", 0)
	if isinstance(spots, list):
		spot_count = len(spots)
	else:
		spot_count = int(spots)
	hangars = info.get("hangars", 0)
	if isinstance(hangars, list):
		hangar_count = len(hangars)
	else:
		hangar_count = int(hangars)
	fleet = state.get("fleet", [])
	# Count aircraft at this airport
	at_airport = sum(1 for ac in fleet if (ac.get("location") or "HOME").upper() == airport.upper())
	capacity = spot_count + (hangar_count * 10)  # Hangars hold 10 each
	return at_airport < capacity


MAINTENANCE_INTERVALS = {
	"A": 150.0,   # A Check every 150 flight hours
	"B": 750.0,   # B Check every 750 flight hours
	"C": 4000.0,  # C Check every 4000 flight hours
}


def _generate_marketplace_listings() -> List[Dict[str, Any]]:
	"""Generate aircraft marketplace listings with various conditions."""
	from catalog import aircraft_catalog
	import random
	
	# Seed random with current day for consistent listings per day
	day_seed = int(time.time() // 86400)  # Days since epoch
	random.seed(day_seed)
	
	listings = []
	catalog = aircraft_catalog()
	
	for aircraft in catalog:
		type_code = aircraft["type_code"]
		base_price = aircraft["price"]
		
		# Generate 1 new aircraft listing
		listings.append({
			"listing_id": f"new_{type_code}_{uuid.uuid4().hex[:8]}",
			"type_code": type_code,
			"name": aircraft["name"],
			"price": int(base_price),
			"condition": "new",
			"total_hours": 0.0,
			"reliability": 1.0,
			"hours_since_a_check": 0.0,
			"hours_since_b_check": 0.0,
			"hours_since_c_check": 0.0,
			"description": "Brand new aircraft, factory fresh",
		})
		
		# Generate 2-3 used aircraft listings
		for i in range(random.randint(2, 3)):
			# Random age and condition
			total_hours = random.uniform(500, 15000)
			age_factor = total_hours / 15000  # 0 to 1
			
			# Reliability based on hours and maintenance
			base_reliability = max(0.5, 1.0 - (age_factor * 0.3))
			
			# Maintenance hours - some might be overdue
			hours_since_a = random.uniform(0, 200)
			hours_since_b = random.uniform(0, 1000)
			hours_since_c = random.uniform(0, 5000)
			
			# Adjust reliability based on overdue maintenance
			if hours_since_a > 150:
				base_reliability -= 0.1
			if hours_since_b > 750:
				base_reliability -= 0.15
			if hours_since_c > 4000:
				base_reliability -= 0.2
			
			base_reliability = max(0.3, base_reliability)
			
			# Price based on condition
			price_multiplier = base_reliability * (1.0 - age_factor * 0.4)
			price = int(base_price * price_multiplier)
			
			# Condition category
			if total_hours < 3000:
				condition = "lightly_used"
				desc = f"Lightly used aircraft with {total_hours:.0f} flight hours"
			elif total_hours < 8000:
				condition = "used"
				desc = f"Used aircraft with {total_hours:.0f} flight hours"
			else:
				condition = "heavily_used"
				desc = f"Heavily used aircraft with {total_hours:.0f} flight hours"
			
			# Add warnings if maintenance is overdue
			warnings = []
			if hours_since_a > 150:
				warnings.append("A Check overdue")
			if hours_since_b > 750:
				warnings.append("B Check overdue")
			if hours_since_c > 4000:
				warnings.append("C Check overdue")
			
			if warnings:
				desc += f" - WARNING: {', '.join(warnings)}"
			
			listings.append({
				"listing_id": f"used_{type_code}_{uuid.uuid4().hex[:8]}",
				"type_code": type_code,
				"name": aircraft["name"],
				"price": price,
				"condition": condition,
				"total_hours": total_hours,
				"reliability": base_reliability,
				"hours_since_a_check": hours_since_a,
				"hours_since_b_check": hours_since_b,
				"hours_since_c_check": hours_since_c,
				"description": desc,
			})
		
		# Generate 1 vintage/classic aircraft listing (low chance)
		if random.random() < 0.3:  # 30% chance
			total_hours = random.uniform(15000, 30000)
			age_factor = min(1.0, total_hours / 20000)
			
			base_reliability = max(0.2, 1.0 - (age_factor * 0.5))
			
			# Vintage aircraft often have overdue maintenance
			hours_since_a = random.uniform(100, 300)
			hours_since_b = random.uniform(500, 1500)
			hours_since_c = random.uniform(3000, 6000)
			
			if hours_since_a > 150:
				base_reliability -= 0.15
			if hours_since_b > 750:
				base_reliability -= 0.2
			if hours_since_c > 4000:
				base_reliability -= 0.25
			
			base_reliability = max(0.2, base_reliability)
			
			price_multiplier = base_reliability * (1.0 - age_factor * 0.6)
			price = int(base_price * price_multiplier * 0.3)  # Very cheap but risky
			
			warnings = []
			if hours_since_a > 150:
				warnings.append("A Check overdue")
			if hours_since_b > 750:
				warnings.append("B Check overdue")
			if hours_since_c > 4000:
				warnings.append("C Check overdue")
			
			desc = f"Vintage aircraft with {total_hours:.0f} flight hours - HIGH RISK"
			if warnings:
				desc += f" - WARNING: {', '.join(warnings)}"
			
			listings.append({
				"listing_id": f"vintage_{type_code}_{uuid.uuid4().hex[:8]}",
				"type_code": type_code,
				"name": aircraft["name"],
				"price": price,
				"condition": "vintage",
				"total_hours": total_hours,
				"reliability": base_reliability,
				"hours_since_a_check": hours_since_a,
				"hours_since_b_check": hours_since_b,
				"hours_since_c_check": hours_since_c,
				"description": desc,
			})
	
	return listings


def get_marketplace_listings() -> List[Dict[str, Any]]:
	"""Get current marketplace aircraft listings."""
	state = get_state()
	marketplace = state.setdefault("marketplace", {})
	last_update_day = marketplace.get("last_update_day", 0)
	current_day = _day_now()
	
	# Regenerate listings daily
	if last_update_day != current_day:
		marketplace["aircraft_listings"] = _generate_marketplace_listings()
		marketplace["last_update_day"] = current_day
		save_state(state)
	
	return marketplace.get("aircraft_listings", [])


def lease_aircraft(type_code: str, name: str, monthly_payment: int, term_months: int, listing_id: str = None) -> None:
	"""Lease an aircraft with monthly payments.
	
	Args:
		type_code: Aircraft type code
		name: Aircraft name
		monthly_payment: Monthly lease payment
		term_months: Lease term in months
		listing_id: Optional marketplace listing ID
	"""
	state = get_state()
	cash = int(state.get("cash", 0))
	
	# First month payment due upfront
	if monthly_payment > cash:
		raise ValueError("Insufficient cash for first month payment")
	
	_home = "HOME"
	if not _has_available_parking(state, _home):
		raise ValueError("No available parking at HOME. Buy spots/hangars in Parking.")
	
	from catalog import aircraft_catalog
	from seat_types import get_default_layout
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(type_code)
	capacity = int(info.get("capacity", 150)) if info else 150
	max_seats_per_row = int(info.get("max_seats_per_row", 6)) if info else 6
	max_rows = int(info.get("max_rows", 40)) if info else 40
	
	aircraft_id = _new_id("ac")
	today = _day_now()
	
	# Get oil requirements from catalog (only for smaller planes)
	cat_oil = {c["type_code"]: c for c in aircraft_catalog()}
	info_oil = cat_oil.get(type_code)
	# Only track oil for smaller planes (if oil_capacity is specified)
	if info_oil and "oil_capacity" in info_oil:
		oil_capacity = float(info_oil.get("oil_capacity", 16.0))
		oil_minimum = float(info_oil.get("oil_minimum", 6.0))
		oil_level = oil_capacity  # Start at full
	else:
		# Airliners don't track oil
		oil_capacity = None
		oil_minimum = None
		oil_level = None
	
	aircraft = {
		"id": aircraft_id,
		"type_code": type_code,
		"name": name,
		"purchase_price": 0,  # Not purchased, leased
		"total_hours": 0.0,
		"hours_since_maintenance": 0.0,
		"maintenance_due_hours": 300.0,
		"hours_since_a_check": 0.0,
		"hours_since_b_check": 0.0,
		"hours_since_c_check": 0.0,
		"location": _home,
		"reliability": 1.0,
		"grounded": False,
		"cabin_layout": get_default_layout(capacity, max_seats_per_row, max_rows),
		"is_leased": True,
		"snags": [],
	}
	
	# Only add oil tracking for smaller planes
	if oil_capacity is not None:
		aircraft["oil_level"] = oil_level
		aircraft["oil_capacity"] = oil_capacity
		aircraft["oil_minimum"] = oil_minimum
		aircraft["hours_since_oil_refill"] = 0.0
		aircraft["hours_since_oil_change"] = 0.0  # Track full oil changes separately
	
	lease = {
		"lease_id": _new_id("lease"),
		"aircraft_id": aircraft_id,
		"type_code": type_code,
		"name": name,
		"monthly_payment": monthly_payment,
		"term_months": term_months,
		"start_date": today,
		"last_payment_month": -1,
	}
	
	# Remove from marketplace if applicable
	if listing_id:
		marketplace = state.setdefault("marketplace", {})
		listings = marketplace.setdefault("aircraft_listings", [])
		marketplace["aircraft_listings"] = [l for l in listings if l.get("listing_id") != listing_id]
	
	state["cash"] = cash - monthly_payment
	state["fleet"].append(aircraft)
	state.setdefault("leases", []).append(lease)
	_add_ledger(state, "lease", -monthly_payment, f"Lease {name} ({type_code}) - First month payment")
	save_state(state)


def get_lease_options() -> List[Dict[str, Any]]:
	"""Get available lease options for aircraft types."""
	from catalog import aircraft_catalog
	import random
	
	# Seed random with current day for consistent options per day
	day_seed = int(time.time() // 86400)
	random.seed(day_seed)
	
	lease_options = []
	catalog = aircraft_catalog()
	
	for aircraft in catalog:
		base_price = aircraft["price"]
		
		# Generate 2-3 lease options per aircraft type
		for i in range(random.randint(2, 3)):
			# Lease terms vary
			term_months = random.choice([12, 24, 36, 48])
			
			# Monthly payment is roughly (base_price * 0.02 to 0.04) / term_months
			# But also depends on lease type
			lease_type = random.choice(["short_term", "standard", "long_term"])
			
			if lease_type == "short_term":
				monthly_rate = random.uniform(0.025, 0.035)  # Higher rate
				term_months = random.choice([6, 12])
			elif lease_type == "standard":
				monthly_rate = random.uniform(0.020, 0.030)
				term_months = random.choice([24, 36])
			else:  # long_term
				monthly_rate = random.uniform(0.015, 0.025)  # Lower rate
				term_months = random.choice([36, 48, 60])
			
			monthly_payment = int((base_price * monthly_rate) / (term_months / 12))
			
			lease_options.append({
				"lease_option_id": f"lease_{aircraft['type_code']}_{uuid.uuid4().hex[:8]}",
				"type_code": aircraft["type_code"],
				"name": aircraft["name"],
				"monthly_payment": monthly_payment,
				"term_months": term_months,
				"lease_type": lease_type,
				"description": f"{lease_type.replace('_', ' ').title()} lease - ${monthly_payment:,}/month for {term_months} months",
			})
	
	return lease_options


def buy_aircraft(type_code: str, name: str, price: int, listing_id: str = None, total_hours: float = 0.0, initial_reliability: float = 1.0, initial_maintenance_hours: Dict[str, float] = None) -> None:
	"""Buy an aircraft. Can be new or used from marketplace.
	
	Args:
		type_code: Aircraft type code
		name: Aircraft name
		price: Purchase price
		listing_id: Optional marketplace listing ID (if buying from marketplace)
		total_hours: Total flight hours on aircraft (for used aircraft)
		initial_reliability: Initial reliability (0.0-1.0)
		initial_maintenance_hours: Dict with hours_since_a_check, hours_since_b_check, hours_since_c_check
	"""
	state = get_state()
	cash = int(state.get("cash", 0))
	if price > cash:
		raise ValueError("Insufficient cash")
	_home = "HOME"
	if not _has_available_parking(state, _home):
		raise ValueError("No available parking at HOME. Buy spots/hangars in Parking.")

	from catalog import aircraft_catalog
	from seat_types import get_default_layout
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(type_code)
	capacity = int(info.get("capacity", 150)) if info else 150
	max_seats_per_row = int(info.get("max_seats_per_row", 6)) if info else 6
	max_rows = int(info.get("max_rows", 40)) if info else 40
	
	# Initialize maintenance hours
	if initial_maintenance_hours:
		hours_since_a = initial_maintenance_hours.get("hours_since_a_check", 0.0)
		hours_since_b = initial_maintenance_hours.get("hours_since_b_check", 0.0)
		hours_since_c = initial_maintenance_hours.get("hours_since_c_check", 0.0)
	else:
		hours_since_a = 0.0
		hours_since_b = 0.0
		hours_since_c = 0.0
	
	# Get oil requirements from catalog (only for smaller planes)
	from catalog import aircraft_catalog
	cat_oil = {c["type_code"]: c for c in aircraft_catalog()}
	info_oil = cat_oil.get(type_code)
	# Only track oil for smaller planes (if oil_capacity is specified)
	if info_oil and "oil_capacity" in info_oil:
		oil_capacity = float(info_oil.get("oil_capacity", 16.0))
		oil_minimum = float(info_oil.get("oil_minimum", 6.0))
		oil_level = oil_capacity  # Start at full
	else:
		# Airliners don't track oil
		oil_capacity = None
		oil_minimum = None
		oil_level = None
	
	aircraft = {
		"id": _new_id("ac"),
		"type_code": type_code,
		"name": name,
		"purchase_price": int(price),
		"total_hours": float(total_hours),
		"hours_since_maintenance": float(max(hours_since_a, hours_since_b, hours_since_c)),
		"maintenance_due_hours": 300.0,
		"hours_since_a_check": hours_since_a,
		"hours_since_b_check": hours_since_b,
		"hours_since_c_check": hours_since_c,
		"location": _home,
		"reliability": max(0.0, min(1.0, float(initial_reliability))),
		"grounded": False,
		"cabin_layout": get_default_layout(capacity, max_seats_per_row, max_rows),
		"is_leased": False,
		"snags": [],  # List of active snags
	}
	
	# Only add oil tracking for smaller planes
	if oil_capacity is not None:
		aircraft["oil_level"] = oil_level
		aircraft["oil_capacity"] = oil_capacity
		aircraft["oil_minimum"] = oil_minimum
		aircraft["hours_since_oil_refill"] = 0.0
		aircraft["hours_since_oil_change"] = 0.0  # Track full oil changes separately
	
	# If buying from marketplace, remove listing
	if listing_id:
		marketplace = state.setdefault("marketplace", {})
		listings = marketplace.setdefault("aircraft_listings", [])
		marketplace["aircraft_listings"] = [l for l in listings if l.get("listing_id") != listing_id]
	
	state["cash"] = cash - int(price)
	state["fleet"].append(aircraft)
	_add_ledger(state, "purchase", -int(price), f"Buy {name} ({type_code})" + (f" - {total_hours:.0f}h total" if total_hours > 0 else ""))
	save_state(state)


def list_fleet() -> List[Dict[str, Any]]:
	return get_state().get("fleet", [])


def get_aircraft_max_duration(type_code: str) -> float:
	state = get_state()
	config = state.get("aircraft_config", {})
	type_config = config.get(type_code, {})
	if "max_duration_hours" in type_config:
		return float(type_config["max_duration_hours"])
	from catalog import aircraft_catalog
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(type_code)
	return float(info.get("max_duration_hours", 5.0)) if info else 5.0


def set_aircraft_max_duration(type_code: str, max_hours: float) -> None:
	state = get_state()
	config = state.setdefault("aircraft_config", {})
	type_config = config.setdefault(type_code, {})
	type_config["max_duration_hours"] = float(max_hours)
	save_state(state)


def get_maintenance_status(aircraft_id: str) -> Dict[str, Dict[str, Any]]:
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		return {}
	
	hours_a = float(aircraft.get("hours_since_a_check", 0.0))
	hours_b = float(aircraft.get("hours_since_b_check", 0.0))
	hours_c = float(aircraft.get("hours_since_c_check", 0.0))
	
	interval_a = MAINTENANCE_INTERVALS["A"]
	interval_b = MAINTENANCE_INTERVALS["B"]
	interval_c = MAINTENANCE_INTERVALS["C"]
	
	return {
		"a_check": {
			"hours": hours_a,
			"interval": interval_a,
			"due": hours_a >= interval_a * 0.9,
			"overdue": hours_a > interval_a,
		},
		"b_check": {
			"hours": hours_b,
			"interval": interval_b,
			"due": hours_b >= interval_b * 0.9,
			"overdue": hours_b > interval_b,
		},
		"c_check": {
			"hours": hours_c,
			"interval": interval_c,
			"due": hours_c >= interval_c * 0.9,
			"overdue": hours_c > interval_c,
		},
	}


def perform_maintenance_level(aircraft_id: str, level: str) -> None:
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	costs = {"A": 50000, "B": 200000, "C": 800000}
	cost = costs.get(level.upper())
	if cost is None:
		raise ValueError(f"Invalid maintenance level: {level}")
	
	cash = int(state.get("cash", 0))
	if cost > cash:
		raise ValueError(f"Insufficient cash. Need ${cost:,} for {level} check.")
	
	# Reset the specific check counter
	if level.upper() == "A":
		aircraft["hours_since_a_check"] = 0.0
		aircraft["reliability"] = min(1.0, float(aircraft.get("reliability", 1.0)) + 0.05)
		# Clear minor snags during A check
		snags = aircraft.get("snags", [])
		aircraft["snags"] = [s for s in snags if s.get("severity") != "Minor"]
	elif level.upper() == "B":
		aircraft["hours_since_b_check"] = 0.0
		aircraft["reliability"] = min(1.0, float(aircraft.get("reliability", 1.0)) + 0.10)
		# Clear minor and major snags during B check
		snags = aircraft.get("snags", [])
		aircraft["snags"] = [s for s in snags if s.get("severity") == "Critical"]
	elif level.upper() == "C":
		aircraft["hours_since_c_check"] = 0.0
		aircraft["reliability"] = min(1.0, float(aircraft.get("reliability", 1.0)) + 0.20)
		aircraft["grounded"] = False
		# C check clears all snags
		aircraft["snags"] = []
		# Also refill oil as part of C check (only for smaller planes)
		if "oil_level" in aircraft and "oil_capacity" in aircraft:
			oil_capacity = float(aircraft.get("oil_capacity", 32.0))
			aircraft["oil_level"] = oil_capacity
			aircraft["hours_since_oil_refill"] = 0.0
			aircraft["hours_since_oil_change"] = 0.0  # C check includes full oil change
			aircraft["hours_since_oil_change"] = 0.0  # C check includes full oil change
		# Airliners don't need oil refills (managed automatically)
	
	state["cash"] = cash - cost
	_add_ledger(state, "maintenance", -cost, f"{level} Check on {aircraft_id}")
	save_state(state)


def list_active_flights() -> List[Dict[str, Any]]:
	return get_state().get("active_flights", [])


def get_flight_weight_manifest(flight_id: str) -> Dict[str, Any]:
	"""Get weight and balance manifest for a specific flight.
	
	Args:
		flight_id: ID of the flight
		
	Returns:
		Dict containing weight manifest, or None if flight not found
	"""
	state = get_state()
	flights = state.get("active_flights", [])
	flight = next((f for f in flights if f.get("flight_id") == flight_id), None)
	
	if not flight:
		# Check completed flights
		completed = state.get("completed_flights", [])
		# Completed flights don't store full flight data, so we can't retrieve manifest
		return None
	
	return flight.get("weight_manifest")


def list_loans() -> List[Dict[str, Any]]:
	return get_state().get("loans", [])


def get_company_reputation() -> float:
	"""Get current company reputation. Returns 0.0 if not set."""
	state = get_state()
	company = state.get("company", {})
	reputation = company.get("reputation")
	if reputation is None:
		return 0.0
	return float(reputation)


def update_reputation(change: float, state: Dict[str, Any]) -> float:
	"""Update company reputation in the provided state object.
	
	Args:
		change: Amount to change reputation by (can be positive or negative)
		state: State dict to modify (must be passed, caller will save)
	
	Returns:
		New reputation value (clamped between 0 and 100)
	"""
	# Ensure company dict exists
	if "company" not in state:
		state["company"] = {}
	
	company = state["company"]
	
	# Get current reputation (default to 0.0)
	current_reputation = float(company.get("reputation", 0.0))
	
	# Calculate new reputation
	new_reputation = current_reputation + change
	
	# Clamp between 0 and 100
	new_reputation = max(0.0, min(100.0, new_reputation))
	
	# Update in state
	company["reputation"] = new_reputation
	
	return new_reputation


def calculate_reputation_bonus(reputation: float, base_revenue: int) -> int:
	"""Calculate bonus money based on reputation.
	
	Reputation scale: 0-100
	- 0-20: -10% to -5% (penalty)
	- 20-40: -5% to 0% (small penalty to neutral)
	- 40-60: 0% to 5% (neutral to small bonus)
	- 60-80: 5% to 15% (good bonus)
	- 80-100: 15% to 25% (excellent bonus)
	"""
	if reputation < 20:
		bonus_percent = -0.10 + (reputation / 20.0) * 0.05  # -10% to -5%
	elif reputation < 40:
		bonus_percent = -0.05 + ((reputation - 20) / 20.0) * 0.05  # -5% to 0%
	elif reputation < 60:
		bonus_percent = ((reputation - 40) / 20.0) * 0.05  # 0% to 5%
	elif reputation < 80:
		bonus_percent = 0.05 + ((reputation - 60) / 20.0) * 0.10  # 5% to 15%
	else:
		bonus_percent = 0.15 + ((reputation - 80) / 20.0) * 0.10  # 15% to 25%
	
	return int(base_revenue * bonus_percent)


def calculate_max_loan_amount() -> int:
	"""Calculate maximum loan amount based on company financials.
	
	Factors:
	- Cash on hand (can borrow up to 5x cash)
	- Fleet value (can borrow up to 0.5x fleet value)
	- Reputation (better reputation = higher multiplier)
	- Existing debt (reduces available credit)
	
	Returns:
		Maximum loan amount in dollars
	"""
	state = get_state()
	cash = int(state.get("cash", 0))
	fleet = state.get("fleet", [])
	reputation = float(state.get("company", {}).get("reputation", 0.0))
	existing_loans = state.get("loans", [])
	
	# Calculate fleet value
	from catalog import aircraft_catalog
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	fleet_value = 0
	for ac in fleet:
		type_code = ac.get("type_code")
		info = cat.get(type_code)
		if info:
			base_price = int(info.get("price", 0))
			# Depreciate based on hours (rough estimate)
			total_hours = float(ac.get("total_hours", 0.0))
			depreciation = min(0.5, total_hours / 10000.0)  # Max 50% depreciation
			aircraft_value = int(base_price * (1.0 - depreciation))
			fleet_value += aircraft_value
	
	# Calculate existing debt
	total_debt = sum(int(l.get("remaining_balance", 0)) for l in existing_loans)
	
	# Base credit limits
	cash_based_limit = cash * 5  # Can borrow 5x cash
	asset_based_limit = int(fleet_value * 0.5)  # Can borrow 50% of fleet value
	
	# Reputation multiplier (0.5x to 2.0x)
	rep_multiplier = 0.5 + (reputation / 100.0) * 1.5
	
	# Maximum loan amount
	max_loan = int((cash_based_limit + asset_based_limit) * rep_multiplier)
	
	# Subtract existing debt
	available_credit = max(0, max_loan - total_debt)
	
	# Minimum loan amount is $10,000, maximum is $50,000,000
	available_credit = max(10000, min(50000000, available_credit))
	
	return available_credit


def get_available_loan_offers() -> List[Dict[str, Any]]:
	"""Get available loan offers from different banks.
	
	Returns:
		List of loan offer dicts with bank_name, max_amount, interest_rate_apr, term_months, description
	"""
	import random
	state = get_state()
	max_loan = calculate_max_loan_amount()
	reputation = float(state.get("company", {}).get("reputation", 0.0))
	existing_loans = state.get("loans", [])
	total_debt = sum(int(l.get("remaining_balance", 0)) for l in existing_loans)
	
	# Banks with different profiles
	banks = [
		{
			"bank_name": "First National Bank",
			"base_rate": 0.055,
			"rate_range": (0.05, 0.07),
			"max_multiplier": 1.0,
			"terms": [12, 24, 36, 48, 60],
			"description": "Conservative bank, good rates for established companies",
		},
		{
			"bank_name": "Skyline Commercial Credit",
			"base_rate": 0.065,
			"rate_range": (0.06, 0.08),
			"max_multiplier": 1.2,
			"terms": [12, 24, 36, 48, 60, 72],
			"description": "Aviation-focused lender, higher limits",
		},
		{
			"bank_name": "Startup Capital Partners",
			"base_rate": 0.085,
			"rate_range": (0.08, 0.12),
			"max_multiplier": 1.5,
			"terms": [6, 12, 18, 24, 36],
			"description": "Higher rates but more flexible for new companies",
		},
		{
			"bank_name": "Elite Business Banking",
			"base_rate": 0.045,
			"rate_range": (0.04, 0.06),
			"max_multiplier": 0.8,
			"terms": [24, 36, 48, 60, 84],
			"description": "Premium rates for high-reputation companies (requires 60+ rep)",
		},
	]
	
	offers = []
	day_seed = int(time.time() // 86400)
	random.seed(day_seed)
	
	for bank in banks:
		# Check eligibility
		if bank["bank_name"] == "Elite Business Banking" and reputation < 60:
			continue  # Skip elite bank if reputation too low
		
		# Calculate rate based on reputation
		rate_range = bank["rate_range"]
		# Better reputation = lower rate (within range)
		rep_factor = 1.0 - (reputation / 100.0) * 0.3  # Up to 30% reduction
		rate = rate_range[0] + (rate_range[1] - rate_range[0]) * rep_factor * random.uniform(0.9, 1.1)
		rate = max(rate_range[0], min(rate_range[1], rate))
		
		# Calculate max amount for this bank
		bank_max = int(max_loan * bank["max_multiplier"])
		bank_max = max(10000, min(50000000, bank_max))
		
		# Generate offers for different terms
		for term in bank["terms"]:
			# Adjust rate slightly based on term (longer = slightly higher)
			term_rate = rate * (1.0 + (term / 60.0) * 0.05)  # Up to 5% increase for longer terms
			
			# Calculate monthly payment for preview
			monthly_rate = term_rate / 12.0
			if monthly_rate == 0:
				monthly_payment = bank_max // term
			else:
				monthly_payment = int(bank_max * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1))
			
			offers.append({
				"bank_name": bank["bank_name"],
				"max_amount": bank_max,
				"interest_rate_apr": term_rate,
				"term_months": term,
				"monthly_payment": monthly_payment,
				"description": bank["description"],
			})
	
	# Sort by interest rate (best rates first)
	offers.sort(key=lambda x: x["interest_rate_apr"])
	
	return offers


def take_loan(principal: int, interest_rate_apr: float, term_months: int, bank_name: str = "Unknown Bank") -> None:
	"""Take a loan from a bank.
	
	Args:
		principal: Loan amount
		interest_rate_apr: Annual interest rate (e.g., 0.06 for 6%)
		term_months: Loan term in months
		bank_name: Name of the bank
	"""
	if principal <= 0:
		raise ValueError("Principal must be positive")
	
	state = get_state()
	max_loan = calculate_max_loan_amount()
	existing_loans = state.get("loans", [])
	total_debt = sum(int(l.get("remaining_balance", 0)) for l in existing_loans)
	
	# Check if loan exceeds available credit
	if principal > (max_loan - total_debt):
		available = max_loan - total_debt
		raise ValueError(f"Loan amount exceeds available credit. Maximum available: ${available:,}")
	
	rate = interest_rate_apr / 12.0
	if rate == 0:
		payment = principal // term_months
	else:
		payment = int(principal * (rate * (1 + rate) ** term_months) / ((1 + rate) ** term_months - 1))
	
	loan = {
		"loan_id": _new_id("loan"),
		"principal": principal,
		"interest_rate_apr": interest_rate_apr,
		"term_months": term_months,
		"monthly_payment": payment,
		"remaining_balance": principal,
		"start_date": _day_now(),
		"bank_name": bank_name,
	}
	state["cash"] = int(state.get("cash", 0)) + principal
	state.setdefault("loans", []).append(loan)
	_add_ledger(state, "loan", principal, f"Loan ${principal:,} from {bank_name} at {interest_rate_apr:.1%} APR")
	save_state(state)


def buy_parking(airport: str, add_spots: int = 0, add_hangars: int = 0, spot_names: Optional[List[str]] = None, hangar_names: Optional[List[str]] = None) -> None:
	if not airport:
		raise ValueError("Airport code required")
	if add_spots < 0 or add_hangars < 0:
		raise ValueError("Cannot buy negative quantities")
	if spot_names is not None and len(spot_names) != add_spots:
		raise ValueError("Number of spot names must match number of spots")
	if hangar_names is not None and len(hangar_names) != add_hangars:
		raise ValueError("Number of hangar names must match number of hangars")
	state = get_state()
	spot_price = 100000
	hangar_price = 750000
	cost = add_spots * spot_price + add_hangars * hangar_price
	if cost > state.get("cash", 0):
		raise ValueError("Insufficient cash")
	parking = state.setdefault("parking", {})
	info = parking.setdefault(airport.upper(), {"spots": [], "hangars": []})
	
	# Migrate old format (int) to new format (list) if needed
	if not isinstance(info.get("spots"), list):
		old_count = int(info.get("spots", 0))
		info["spots"] = [{"name": f"Spot {i+1}"} for i in range(old_count)]
	if not isinstance(info.get("hangars"), list):
		old_count = int(info.get("hangars", 0))
		info["hangars"] = [{"name": f"Hangar {i+1}"} for i in range(old_count)]
	
	# Add new spots with names
	if add_spots > 0:
		if spot_names is None:
			# Default names if not provided
			existing_count = len(info["spots"])
			spot_names = [f"Spot {existing_count + i + 1}" for i in range(add_spots)]
		for name in spot_names:
			info["spots"].append({"name": name})
	
	# Add new hangars with names
	if add_hangars > 0:
		if hangar_names is None:
			# Default names if not provided
			existing_count = len(info["hangars"])
			hangar_names = [f"Hangar {existing_count + i + 1}" for i in range(add_hangars)]
		for name in hangar_names:
			info["hangars"].append({"name": name})
	
	state["cash"] = int(state.get("cash", 0)) - cost
	spot_names_str = ", ".join(spot_names) if spot_names else ""
	hangar_names_str = ", ".join(hangar_names) if hangar_names else ""
	ledger_note = f"Parking {airport} +{add_spots} spots +{add_hangars} hangars"
	if spot_names_str or hangar_names_str:
		parts = []
		if spot_names_str:
			parts.append(f"spots: {spot_names_str}")
		if hangar_names_str:
			parts.append(f"hangars: {hangar_names_str}")
		ledger_note += f" ({', '.join(parts)})"
	_add_ledger(state, "parking", -cost, ledger_note)
	save_state(state)


def list_parking():
	return get_state().get("parking", {})


def auto_complete_due_flights() -> int:
	state = get_state()
	flights = list(state.get("active_flights", []))
	done = 0
	for flt in list(flights):
		if int(flt.get("eta_ts", 0)) <= _now_ts():
			end_flight(flt["flight_id"])  # updates state and ledger
			done += 1
	return done


def run_daily_tick() -> int:
	"""Apply overnight parking fees once per day for aircraft at airports without owned capacity.
	Also process lease payments and update fuel prices.
	Returns number of penalties applied."""
	state = get_state()
	today = _day_now()
	penalties = 0
	
	# Update fuel prices daily
	update_fuel_prices()
	
	# Update last daily tick day
	state["last_daily_tick_day"] = today
	
	# Process parking fees
	import random
	from seat_types import calculate_cabin_total_seats
	
	for ac in state.get("fleet", []):
		loc = (ac.get("location") or "HOME").upper()
		last_day = int(ac.get("last_penalty_day", 0))
		if last_day == today:
			continue
		if not _has_owned_parking(state, loc):
			# Get aircraft capacity
			layout = ac.get("cabin_layout", [])
			capacity = calculate_cabin_total_seats(layout) if layout else 0
			if capacity == 0:
				# Fallback to catalog capacity if no layout
				from catalog import aircraft_catalog
				cat = {c["type_code"]: c for c in aircraft_catalog()}
				info = cat.get(ac.get("type_code"))
				capacity = int(info.get("capacity", 0)) if info else 0
			
			# Large aircraft (>19 seats) cannot park at airports without owned parking
			if capacity > 19:
				# Apply $5,000 fine for parking large aircraft without owned parking
				fine_amount = 5000
				state["cash"] = int(state.get("cash", 0)) - fine_amount
				ac["last_penalty_day"] = today
				_add_ledger(state, "parking_fine", -fine_amount, f"Parking violation: Aircraft with {capacity} seats parked at {loc} without owned parking/hangar")
				penalties += 1
			else:
				# Small aircraft (<=19 seats) pay realistic parking fees: $15-$30 per night
				amount = random.randint(15, 30)
				state["cash"] = int(state.get("cash", 0)) - amount
				ac["last_penalty_day"] = today
				_add_ledger(state, "parking_fee", -amount, f"Overnight parking fee at {loc}")
				penalties += 1
	
	# Process lease payments
	leases = state.get("leases", [])
	active_leases = []
	for lease in leases:
		lease_id = lease.get("lease_id")
		aircraft_id = lease.get("aircraft_id")
		monthly_payment = int(lease.get("monthly_payment", 0))
		start_date = int(lease.get("start_date", 0))
		term_months = int(lease.get("term_months", 12))
		
		# Calculate days since start
		days_since_start = today - start_date
		if days_since_start < 0:
			days_since_start = 0
		
		# Calculate months elapsed (approximately 30 days per month)
		months_elapsed = days_since_start // 30
		total_months = months_elapsed + 1
		
		# Check if lease has expired
		if total_months > term_months:
			# Lease expired - return aircraft or extend
			# For now, we'll just mark as expired
			continue
		
		# Check if payment is due (once per month)
		last_payment_month = int(lease.get("last_payment_month", -1))
		if last_payment_month < months_elapsed:
			# Payment due
			if state.get("cash", 0) >= monthly_payment:
				state["cash"] = int(state.get("cash", 0)) - monthly_payment
				lease["last_payment_month"] = months_elapsed
				_add_ledger(state, "lease_payment", -monthly_payment, f"Lease payment for {aircraft_id}")
			else:
				# Can't pay - lease might be terminated
				pass
		
		active_leases.append(lease)
	
	state["leases"] = active_leases
	
	# Process loan payments
	loans = state.get("loans", [])
	active_loans = []
	for loan in loans:
		loan_id = loan.get("loan_id")
		bank_name = loan.get("bank_name", "Unknown Bank")
		monthly_payment = int(loan.get("monthly_payment", 0))
		start_date = int(loan.get("start_date", 0))
		remaining_balance = int(loan.get("remaining_balance", 0))
		
		# Calculate days since start
		days_since_start = today - start_date
		if days_since_start < 0:
			days_since_start = 0
		
		# Calculate months elapsed (approximately 30 days per month)
		months_elapsed = days_since_start // 30
		
		# Check if payment is due (once per month, starting from month 1)
		last_payment_month = int(loan.get("last_payment_month", -1))
		if last_payment_month < months_elapsed and remaining_balance > 0:
			# Payment due
			payment_amount = min(monthly_payment, remaining_balance)
			cash = int(state.get("cash", 0))
			
			if cash >= payment_amount:
				# Can pay - automatic payment
				state["cash"] = cash - payment_amount
				loan["remaining_balance"] = remaining_balance - payment_amount
				loan["last_payment_month"] = months_elapsed
				_add_ledger(state, "loan_payment", -payment_amount, f"Automatic loan payment to {bank_name}")
			else:
				# Can't pay - add penalty interest (late fee)
				penalty = int(payment_amount * 0.05)  # 5% late fee
				state["cash"] = max(0, cash - penalty)  # Take penalty if possible
				loan["remaining_balance"] = remaining_balance + penalty  # Add penalty to balance
				_add_ledger(state, "loan_penalty", -penalty, f"Late payment penalty for {bank_name} loan")
		
		# Only keep active loans (with remaining balance)
		if loan["remaining_balance"] > 0:
			active_loans.append(loan)
		else:
			# Loan fully paid off
			_add_ledger(state, "loan", 0, f"Loan from {bank_name} fully paid off")
	
	state["loans"] = active_loans
	save_state(state)
	return penalties


def auto_process_daily_ticks() -> Dict[str, Any]:
	"""Automatically process any missed daily ticks since last run.
	This catches up on days when the game wasn't played.
	
	The existing run_daily_tick() logic already handles catching up on missed
	payments (loans, leases) and fees, so we just need to call it once.
	
	Returns:
		Dict with summary of what was processed: days_processed, total_penalties, etc.
	"""
	state = get_state()
	today = _day_now()
	last_tick_day = int(state.get("last_daily_tick_day", today))
	
	# Calculate days missed
	days_missed = today - last_tick_day
	
	if days_missed <= 0:
		# Already up to date
		return {
			"days_processed": 0,
			"total_penalties": 0,
			"up_to_date": True,
		}
	
	# Run daily tick once - it will catch up on all missed payments and fees
	# The existing logic in run_daily_tick() already handles multiple months of
	# loan/lease payments and will process everything that's due
	penalties = run_daily_tick()
	
	return {
		"days_processed": days_missed,
		"total_penalties": penalties,
		"up_to_date": True,
	}


def run_pilot_daily_tick() -> Dict[str, int]:
	"""Process pilot daily activities. Returns summary dict."""
	state = get_state()
	revenue = 0
	salary_costs = 0
	snags_found = 0
	damage_events = 0
	
	# This is a placeholder - implement pilot logic if needed
	# For now, just return empty summary
	
	return {
		"revenue": revenue,
		"salary_costs": salary_costs,
		"snags_found": snags_found,
		"damage_events": damage_events,
	}


def perform_maintenance(aircraft_id: str, level: str) -> None:
	"""Alias for perform_maintenance_level."""
	perform_maintenance_level(aircraft_id, level)


def change_aircraft_id(aircraft_id: str, new_id: str) -> None:
	"""Change an aircraft's ID. Charges administrative fee."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Check if new ID already exists
	if any(ac.get("id") == new_id for ac in state.get("fleet", [])):
		raise ValueError(f"Aircraft ID {new_id} already exists")
	
	admin_fee = 5000
	if state.get("cash", 0) < admin_fee:
		raise ValueError(f"Insufficient cash. Need ${admin_fee:,} for administrative fee.")
	
	aircraft["id"] = new_id
	state["cash"] = int(state.get("cash", 0)) - admin_fee
	_add_ledger(state, "admin", -admin_fee, f"Change aircraft ID from {aircraft_id} to {new_id}")
	save_state(state)


def get_aircraft_cabin_comfort(aircraft_id: str) -> float:
	"""Get cabin comfort rating for an aircraft."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		return 1.0
	from seat_types import calculate_cabin_comfort
	layout = aircraft.get("cabin_layout", [])
	return calculate_cabin_comfort(layout)


def get_aircraft_cabin_capacity(aircraft_id: str) -> int:
	"""Get total seat capacity for an aircraft."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		return 0
	from seat_types import calculate_cabin_total_seats
	layout = aircraft.get("cabin_layout", [])
	return calculate_cabin_total_seats(layout)


def get_aircraft_cabin_limits(aircraft_id: str) -> Dict[str, int]:
	"""Get cabin configuration limits for an aircraft."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	from catalog import aircraft_catalog
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(aircraft.get("type_code"))
	
	max_seats_per_row = int(info.get("max_seats_per_row", 6)) if info else 6
	max_rows = int(info.get("max_rows", 40)) if info else 40
	
	# Check for custom limits
	config = state.get("aircraft_config", {})
	type_config = config.get(aircraft.get("type_code"), {})
	if "max_seats_per_row" in type_config:
		max_seats_per_row = int(type_config["max_seats_per_row"])
	if "max_rows" in type_config:
		max_rows = int(type_config["max_rows"])
	
	return {
		"max_seats_per_row": max_seats_per_row,
		"max_rows": max_rows,
	}


def set_aircraft_cabin_limits(aircraft_id: str, max_seats_per_row: int = None, max_rows: int = None) -> None:
	"""Set custom cabin configuration limits for an aircraft type."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	type_code = aircraft.get("type_code")
	config = state.setdefault("aircraft_config", {})
	type_config = config.setdefault(type_code, {})
	
	if max_seats_per_row is not None:
		type_config["max_seats_per_row"] = int(max_seats_per_row)
	if max_rows is not None:
		type_config["max_rows"] = int(max_rows)
	
	save_state(state)


def configure_aircraft_cabin(aircraft_id: str, layout: List[Dict]) -> None:
	"""Configure the cabin layout for an aircraft. Charges installation cost."""
	state = get_state()
	ac = next((x for x in state.get("fleet", []) if x.get("id") == aircraft_id), None)
	if not ac:
		raise ValueError("Aircraft not found")
	# Validate against limits
	limits = get_aircraft_cabin_limits(aircraft_id)
	max_rows = limits["max_rows"]
	max_seats = limits["max_seats_per_row"]
	if len(layout) > max_rows:
		raise ValueError(f"Too many rows ({len(layout)}). Maximum is {max_rows} rows.")
	for row in layout:
		seats = int(row.get("seats", 0))
		if seats > max_seats:
			raise ValueError(f"Row {row.get('row')} has too many seats ({seats}). Maximum is {max_seats} seats per row.")
	from seat_types import calculate_cabin_cost
	cost = calculate_cabin_cost(layout)
	cash = int(state.get("cash", 0))
	if cost > cash:
		raise ValueError(f"Insufficient cash. Need ${cost:,} for cabin configuration.")
	ac["cabin_layout"] = layout
	state["cash"] = cash - cost
	_add_ledger(state, "cabin", -cost, f"Cabin configuration {aircraft_id}")
	save_state(state)


AIRPORT_SERVICES = {
	"refueling": {
		"name": "Refueling",
		"description": "Purchase fuel in litres or gallons. Prices vary by airport location.",
		"base_cost": 0,  # Cost calculated per unit
		"cost_per_hour": 0,
	},
	"deicing": {
		"name": "De-icing",
		"description": "De-ice aircraft to prevent delays and safety issues in winter conditions.",
		"base_cost": 500,
		"cost_per_hour": 50,
	},
	"catering": {
		"name": "Catering",
		"description": "Food and beverage service. Increases passenger satisfaction and demand.",
		"base_cost": 800,
		"cost_per_hour": 100,
	},
	"ground_power": {
		"name": "Ground Power Unit",
		"description": "External power supply. Reduces operating costs by saving APU fuel.",
		"base_cost": 300,
		"cost_per_hour": 30,
	},
	"lavatory": {
		"name": "Lavatory Service",
		"description": "Restroom servicing and maintenance for passenger comfort.",
		"base_cost": 200,
		"cost_per_hour": 20,
	},
	"water": {
		"name": "Water Service",
		"description": "Fresh water supply for aircraft systems and passenger use.",
		"base_cost": 150,
		"cost_per_hour": 15,
	},
	"cleaning": {
		"name": "Cleaning",
		"description": "Aircraft interior cleaning. Improves passenger satisfaction and demand.",
		"base_cost": 400,
		"cost_per_hour": 40,
	},
	"livery": {
		"name": "Livery Painting",
		"description": "Custom paint job and livery design. Improves brand recognition and passenger appeal.",
		"base_cost": 50000,
		"cost_per_hour": 0,  # One-time cost, not hourly
	},
}


def get_fuel_prices(airport_code: str) -> Dict[str, float]:
	"""Get fuel prices for a specific airport. Prices vary by airport."""
	# Use hash of airport code to generate deterministic but varying prices
	hash_val = int(hashlib.md5(airport_code.upper().encode()).hexdigest()[:8], 16)
	
	# Base prices in USD
	base_price_per_litre = 0.75
	base_price_per_gallon = 2.85
	
	# Variation: ±20% based on hash
	variation = (hash_val % 4000) / 10000.0 - 0.2  # -0.2 to +0.2
	
	price_per_litre = base_price_per_litre * (1.0 + variation)
	price_per_gallon = base_price_per_gallon * (1.0 + variation)
	
	return {
		"price_per_litre": round(price_per_litre, 2),
		"price_per_gallon": round(price_per_gallon, 2),
	}


def list_airport_services() -> List[Dict[str, Any]]:
	"""List all available airport services."""
	return [
		{"type": key, "name": value["name"], **value}
		for key, value in AIRPORT_SERVICES.items()
	]


def purchase_airport_service(aircraft_id: str, service_type: str, quantity: float = None, unit: str = "litres") -> None:
	"""Purchase an airport service for an aircraft at its current location.
	
	Args:
		aircraft_id: ID of the aircraft
		service_type: Type of service (e.g., "refueling", "livery", "cleaning")
		quantity: For refueling: fuel quantity. For others: ignored.
		unit: For refueling: "litres" or "gallons". For others: ignored.
	"""
	if service_type not in AIRPORT_SERVICES:
		raise ValueError(f"Unknown service type: {service_type}")
	
	state = get_state()
	aircraft = None
	for ac in state.get("fleet", []):
		if ac.get("id") == aircraft_id:
			aircraft = ac
			break
	
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	service = AIRPORT_SERVICES[service_type]
	location = aircraft.get("location", "HOME")
	
	# Calculate cost
	if service_type == "refueling":
		if quantity is None or quantity <= 0:
			raise ValueError("Quantity must be specified and greater than 0 for refueling")
		
		fuel_prices = get_fuel_prices(location)
		
		if unit.lower() == "gallons":
			quantity_litres = quantity * 3.78541
			price_per_unit = fuel_prices["price_per_gallon"]
			unit_display = "gallons"
		else:
			quantity_litres = quantity
			price_per_unit = fuel_prices["price_per_litre"]
			unit_display = "litres"
		
		cost = quantity * price_per_unit
		service_note = f"{service['name']} {quantity:,.0f} {unit_display} for {aircraft_id}"
	elif service_type == "livery":
		# Livery is a fixed cost service
		base_cost = service.get("base_cost", 0)
		cost = base_cost if base_cost > 0 else 50000
		service_note = f"{service['name']} for {aircraft_id}"
	else:
		from catalog import aircraft_catalog
		cat = {c["type_code"]: c for c in aircraft_catalog()}
		info = cat.get(aircraft.get("type_code"))
		hourly_cost = float(info.get("hourly_cost", 2000)) if info else 2000.0
		
		base_cost = service.get("base_cost", 0)
		cost_per_hour = service.get("cost_per_hour", 0)
		if base_cost > 0 and cost_per_hour > 0:
			cost = int(base_cost + (cost_per_hour * hourly_cost / 100))
		else:
			cost = base_cost if base_cost > 0 else 1000
		
		service_note = f"{service['name']} for {aircraft_id}"
	
	cost = int(cost)
	
	if cost > state.get("cash", 0):
		raise ValueError(f"Insufficient cash. Need ${cost:,} for {service['name']}.")
	
	state["cash"] = int(state.get("cash", 0)) - cost
	_add_ledger(state, "airport_service", -cost, f"{service_note} at {location}")
	
	# Track service benefits
	if service_type == "refueling":
		aircraft.setdefault("last_services", {})[service_type] = {
			"timestamp": _now_ts(),
			"quantity": quantity_litres,
			"unit": unit_display,
		}
	elif service_type == "livery":
		# Livery is a permanent service - store it on the aircraft
		# Generate default livery name
		company_name = state.get("company", {}).get("name", "Airline")
		livery_name = f"{company_name} Livery"
		
		aircraft["livery"] = {
			"name": livery_name,
			"painted_date": _day_now(),
			"painted_timestamp": _now_ts(),
		}
		aircraft.setdefault("last_services", {})[service_type] = _now_ts()
	else:
		aircraft.setdefault("last_services", {})[service_type] = _now_ts()
	
	save_state(state)


def get_aircraft_services(aircraft_id: str) -> Dict[str, Any]:
	"""Get recent services purchased for an aircraft."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		return {}
	return aircraft.get("last_services", {})


def purchase_custom_item(airport: str, item_name: str, cost: int) -> str:
	"""Purchase a custom item and store it at an airport.
	
	Args:
		airport: Airport code where the item will be stored
		item_name: Name of the custom item
		cost: Cost of the custom item
	
	Returns:
		The item ID of the purchased item
	"""
	if not airport or not airport.strip():
		raise ValueError("Airport code required")
	if not item_name or not item_name.strip():
		raise ValueError("Item name required")
	if cost <= 0:
		raise ValueError("Cost must be greater than 0")
	
	state = get_state()
	
	# Check if company has a hangar at the airport
	if not has_hangar_at_airport(airport.upper()):
		raise ValueError(f"No hangar owned at {airport}. You must own a hangar to store custom items.")
	
	# Check if player has enough cash
	if cost > state.get("cash", 0):
		raise ValueError(f"Insufficient cash. Need ${cost:,} for {item_name}.")
	
	# Create custom item
	item_id = _new_id("custom_item")
	custom_item = {
		"item_id": item_id,
		"name": item_name.strip(),
		"cost": int(cost),
		"airport": airport.upper(),
		"purchase_date": _day_now(),
		"purchase_timestamp": _now_ts(),
		"installed_on": None,  # Aircraft ID if installed, None if stored
	}
	
	# Store in state
	custom_items = state.setdefault("custom_items", [])
	custom_items.append(custom_item)
	
	# Deduct cost
	state["cash"] = int(state.get("cash", 0)) - cost
	_add_ledger(state, "custom_item", -cost, f"Custom item '{item_name}' purchased and stored at {airport.upper()}")
	
	save_state(state)
	return item_id


def list_stored_custom_items(airport: str = None) -> List[Dict[str, Any]]:
	"""List custom items stored at airports (not installed on aircraft).
	
	Args:
		airport: Optional airport code to filter by. If None, returns all stored items.
	
	Returns:
		List of custom item dictionaries
	"""
	state = get_state()
	custom_items = state.get("custom_items", [])
	
	# Filter to only stored items (not installed)
	stored_items = [item for item in custom_items if item.get("installed_on") is None]
	
	# Filter by airport if specified
	if airport:
		airport_upper = airport.upper()
		stored_items = [item for item in stored_items if item.get("airport") == airport_upper]
	
	return stored_items


def list_installed_custom_items(aircraft_id: str = None) -> List[Dict[str, Any]]:
	"""List custom items installed on aircraft.
	
	Args:
		aircraft_id: Optional aircraft ID to filter by. If None, returns all installed items.
	
	Returns:
		List of custom item dictionaries
	"""
	state = get_state()
	custom_items = state.get("custom_items", [])
	
	# Filter to only installed items
	installed_items = [item for item in custom_items if item.get("installed_on") is not None]
	
	# Filter by aircraft if specified
	if aircraft_id:
		installed_items = [item for item in installed_items if item.get("installed_on") == aircraft_id]
	
	return installed_items


def install_custom_item(item_id: str, aircraft_id: str) -> None:
	"""Install a custom item on an aircraft.
	
	Args:
		item_id: ID of the custom item to install
		aircraft_id: ID of the aircraft to install the item on
	
	Raises:
		ValueError: If item or aircraft not found, or if they're not at the same airport
	"""
	state = get_state()
	
	# Find the custom item
	custom_items = state.get("custom_items", [])
	item = next((i for i in custom_items if i.get("item_id") == item_id), None)
	if not item:
		raise ValueError("Custom item not found")
	
	# Check if item is already installed on another aircraft
	installed_on = item.get("installed_on")
	if installed_on:
		if installed_on == aircraft_id:
			raise ValueError(f"Item is already installed on this aircraft ({aircraft_id})")
		else:
			raise ValueError(f"Item is already installed on aircraft {installed_on}. Each custom item can only be installed on one aircraft at a time.")
	
	# Find the aircraft
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Check if item and aircraft are at the same airport
	item_airport = item.get("airport", "").upper()
	aircraft_location = (aircraft.get("location") or "HOME").upper()
	
	if item_airport != aircraft_location:
		raise ValueError(f"Item is stored at {item_airport} but aircraft is at {aircraft_location}. They must be at the same airport.")
	
	# Install the item
	item["installed_on"] = aircraft_id
	item["installed_date"] = _day_now()
	item["installed_timestamp"] = _now_ts()
	
	# Track on aircraft
	aircraft.setdefault("custom_items", []).append(item_id)
	
	save_state(state)


def uninstall_custom_item(item_id: str) -> None:
	"""Uninstall a custom item from an aircraft and return it to storage at the airport.
	
	Args:
		item_id: ID of the custom item to uninstall
	"""
	state = get_state()
	
	# Find the custom item
	custom_items = state.get("custom_items", [])
	item = next((i for i in custom_items if i.get("item_id") == item_id), None)
	if not item:
		raise ValueError("Custom item not found")
	
	# Check if item is installed
	aircraft_id = item.get("installed_on")
	if not aircraft_id:
		raise ValueError("Item is not installed on any aircraft")
	
	# Find the aircraft
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if aircraft:
		# Remove from aircraft's custom items list
		aircraft_custom_items = aircraft.get("custom_items", [])
		if item_id in aircraft_custom_items:
			aircraft_custom_items.remove(item_id)
	
	# Uninstall the item
	item["installed_on"] = None
	item.pop("installed_date", None)
	item.pop("installed_timestamp", None)
	
	save_state(state)


def list_pilots() -> List[Dict[str, Any]]:
	"""List all pilots."""
	return get_state().get("pilots", [])


def hire_pilot(name: str, skill_level: int = 1, salary: int = None) -> None:
	"""Hire a new pilot."""
	if not name or not name.strip():
		raise ValueError("Pilot name required")
	if skill_level < 1 or skill_level > 5:
		raise ValueError("Skill level must be between 1 and 5")
	
	state = get_state()
	if salary is None:
		salary = 5000 + (skill_level * 2000)  # Base salary based on skill
	
	pilot = {
		"pilot_id": _new_id("pilot"),
		"name": name.strip(),
		"skill_level": skill_level,
		"salary": salary,
		"assigned_aircraft_id": None,
		"total_revenue": 0,
		"total_flights": 0,
	}
	
	state.setdefault("pilots", []).append(pilot)
	save_state(state)


def assign_pilot_to_aircraft(pilot_id: str, aircraft_id: str = None) -> None:
	"""Assign a pilot to an aircraft, or unassign if aircraft_id is None."""
	state = get_state()
	pilot = next((p for p in state.get("pilots", []) if p.get("pilot_id") == pilot_id), None)
	if not pilot:
		raise ValueError("Pilot not found")
	
	if aircraft_id:
		# Verify aircraft exists
		aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
		if not aircraft:
			raise ValueError("Aircraft not found")
	
	pilot["assigned_aircraft_id"] = aircraft_id
	save_state(state)


def fire_pilot(pilot_id: str) -> None:
	"""Fire a pilot."""
	state = get_state()
	pilots = state.get("pilots", [])
	state["pilots"] = [p for p in pilots if p.get("pilot_id") != pilot_id]
	save_state(state)


def repay_loan(loan_id: str, amount: int = None) -> None:
	"""Repay a loan. If amount is None, pays minimum monthly payment."""
	state = get_state()
	loan = next((l for l in state.get("loans", []) if l.get("loan_id") == loan_id), None)
	if not loan:
		raise ValueError("Loan not found")
	
	if amount is None:
		amount = loan.get("monthly_payment", 0)
	
	if amount <= 0:
		raise ValueError("Payment amount must be positive")
	
	remaining = int(loan.get("remaining_balance", 0))
	if amount > remaining:
		amount = remaining
	
	cash = int(state.get("cash", 0))
	if amount > cash:
		raise ValueError(f"Insufficient cash. Need ${amount:,} for payment.")
	
	loan["remaining_balance"] = remaining - amount
	state["cash"] = cash - amount
	_add_ledger(state, "loan_payment", -amount, f"Loan payment {loan_id}")
	
	# Remove loan if fully paid
	if loan["remaining_balance"] <= 0:
		loans = state.get("loans", [])
		state["loans"] = [l for l in loans if l.get("loan_id") != loan_id]
	
	save_state(state)


def get_aircraft_weight_limits(aircraft_id: str) -> Dict[str, float]:
	"""Get weight limits for an aircraft.
	
	Args:
		aircraft_id: ID of the aircraft
		
	Returns:
		Dict with empty_weight, max_zero_fuel_weight, max_takeoff_weight (or None if not set)
	"""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		return {}
	
	return {
		"empty_weight": aircraft.get("empty_weight"),
		"max_zero_fuel_weight": aircraft.get("max_zero_fuel_weight"),
		"max_takeoff_weight": aircraft.get("max_takeoff_weight"),
	}


def set_aircraft_weight_limits(aircraft_id: str, empty_weight: float = None, max_zero_fuel_weight: float = None, max_takeoff_weight: float = None) -> None:
	"""Set weight limits for an aircraft.
	
	Args:
		aircraft_id: ID of the aircraft
		empty_weight: Empty weight of aircraft in lbs
		max_zero_fuel_weight: Maximum zero fuel weight in lbs
		max_takeoff_weight: Maximum takeoff weight in lbs
	"""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	if empty_weight is not None:
		aircraft["empty_weight"] = float(empty_weight)
	if max_zero_fuel_weight is not None:
		aircraft["max_zero_fuel_weight"] = float(max_zero_fuel_weight)
	if max_takeoff_weight is not None:
		aircraft["max_takeoff_weight"] = float(max_takeoff_weight)
	
	save_state(state)


def generate_weight_manifest(passengers: int, aircraft_id: str = None) -> Dict[str, Any]:
	"""Generate a weight and balance manifest for a flight.
	
	Args:
		passengers: Number of passengers booked for the flight
		aircraft_id: Optional aircraft ID to check weight limits
		
	Returns:
		Dict containing weight manifest with passenger weights, cargo weight, and totals
	"""
	import random
	
	# Get aircraft weight limits if aircraft_id provided
	weight_limits = None
	empty_weight = None
	max_zero_fuel_weight = None
	if aircraft_id:
		weight_limits = get_aircraft_weight_limits(aircraft_id)
		empty_weight = weight_limits.get("empty_weight")
		max_zero_fuel_weight = weight_limits.get("max_zero_fuel_weight")
	
	# Average passenger weight (including carry-on): 190 lbs (86 kg)
	# Individual passenger weights vary: 150-250 lbs
	passenger_weights = []
	total_passenger_weight = 0.0
	
	for i in range(passengers):
		# Random weight per passenger: 150-250 lbs
		weight = random.uniform(150.0, 250.0)
		passenger_weights.append({
			"passenger_num": i + 1,
			"weight_lbs": round(weight, 1),
		})
		total_passenger_weight += weight
	
	total_passenger_weight = round(total_passenger_weight, 1)
	
	# Calculate available weight for cargo
	# Formula: Empty Weight + Passenger Weight + Cargo Weight = Zero Fuel Weight
	# Zero Fuel Weight must not exceed Max Zero Fuel Weight
	if empty_weight is not None and max_zero_fuel_weight is not None:
		# Calculate maximum cargo weight based on zero fuel weight limit
		available_for_cargo = max_zero_fuel_weight - empty_weight - total_passenger_weight
		available_for_cargo = max(0.0, available_for_cargo)  # Can't be negative
		
		# Generate cargo weight (random, but within available limit)
		# Use 70-100% of available cargo capacity for randomness
		if available_for_cargo > 0:
			cargo_weight = random.uniform(available_for_cargo * 0.7, available_for_cargo)
		else:
			cargo_weight = 0.0
	else:
		# Fallback to old method if weight limits not set
		# Cargo weight: random but limited by number of passengers
		base_cargo_min = 500.0
		base_cargo_max = 2000.0
		cargo_reduction_per_pax = 15.0
		
		max_cargo = max(0.0, base_cargo_max - (passengers * cargo_reduction_per_pax))
		min_cargo = max(0.0, base_cargo_min - (passengers * cargo_reduction_per_pax * 0.5))
		
		if max_cargo > min_cargo:
			cargo_weight = random.uniform(min_cargo, max_cargo)
		else:
			cargo_weight = 0.0
	
	cargo_weight = round(cargo_weight, 1)
	
	# Calculate zero fuel weight
	zero_fuel_weight = (empty_weight or 0.0) + total_passenger_weight + cargo_weight
	zero_fuel_weight = round(zero_fuel_weight, 1)
	
	# Check if within limits
	within_limits = True
	if max_zero_fuel_weight is not None:
		within_limits = zero_fuel_weight <= max_zero_fuel_weight
	
	return {
		"passenger_weights": passenger_weights,
		"passenger_count": passengers,
		"total_passenger_weight": total_passenger_weight,
		"cargo_weight": cargo_weight,
		"empty_weight": empty_weight,
		"zero_fuel_weight": zero_fuel_weight,
		"max_zero_fuel_weight": max_zero_fuel_weight,
		"max_takeoff_weight": weight_limits.get("max_takeoff_weight") if weight_limits else None,
		"within_limits": within_limits,
	}


def start_flight(aircraft_id: str, route: str, ticket_price: int, duration_hours: float) -> None:
	"""Start a flight.
	
	Args:
		aircraft_id: ID of aircraft
		route: Route string (e.g., "HOME-DEST")
		ticket_price: Ticket price per passenger
		duration_hours: Flight duration in hours
	"""
	import random
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Parse route to get destination
	parts = route.split("-")
	if len(parts) >= 2:
		dest = parts[-1].strip().upper()
		origin = parts[0].strip().upper()
	else:
		dest = "HOME"
		origin = "HOME"
	
	# Check for pilot assignment and skill impact
	pilot_skill_bonus = 0.0
	pilot_assigned = None
	pilots = state.get("pilots", [])
	for pilot in pilots:
		if pilot.get("assigned_aircraft_id") == aircraft_id:
			pilot_assigned = pilot.get("name")
			skill_level = pilot.get("skill_level", 1)
			# Higher skill = better flight quality (affects reputation)
			pilot_skill_bonus = (skill_level - 1) * 0.5  # +0.5 rep per skill level above 1
			break
	
	# Calculate passengers based on demand
	from catalog import aircraft_catalog
	from seat_types import calculate_cabin_total_seats, calculate_cabin_comfort
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(aircraft.get("type_code"))
	hourly_cost = float(info.get("hourly_cost", 2000)) if info else 2000.0
	
	# Get actual cabin capacity
	layout = aircraft.get("cabin_layout", [])
	actual_capacity = calculate_cabin_total_seats(layout) if layout else 0
	cap = actual_capacity if actual_capacity > 0 else int(info.get("capacity", 150)) if info else 150
	
	# Calculate demand based on price and comfort
	# Baseline price accounts for operating costs + fuel/maintenance overhead + profit margin
	# Since hourly_cost is now just unspecified costs, we need a higher multiplier
	# and a base minimum to ensure profitable ticket prices
	comfort = calculate_cabin_comfort(layout) if layout else 1.0
	
	# Base minimum price per seat per hour (accounts for fuel, maintenance, etc. not in hourly_cost)
	base_min_per_seat_per_hour = 15.0  # Minimum $15/seat/hour regardless of aircraft
	
	# Operating cost component (from hourly_cost, now lower)
	operating_cost_per_seat_per_hour = (hourly_cost / cap) if cap > 0 else 0
	
	# Total baseline: base minimum + operating cost, with profit margin
	baseline_per_hour_per_seat = max(base_min_per_seat_per_hour, operating_cost_per_seat_per_hour * 2.0) * 3.5
	comfort_mult = 1.0 + (comfort - 1.0) * 0.5
	baseline = baseline_per_hour_per_seat * duration_hours * comfort_mult
	comfort_boost = 1.0 + (comfort - 1.0) * 0.15
	price_ratio = baseline / ticket_price if ticket_price > 0 else 0.1
	demand_ratio = min(1.0, max(0.1, price_ratio * comfort_boost))
	
	# Apply seasonal demand multiplier
	seasonal_mult = get_seasonal_demand_multiplier()
	demand_ratio *= seasonal_mult
	
	# Calculate passengers based on demand
	pax_requested = cap
	passengers = max(0, min(int(round(pax_requested * demand_ratio)), cap))
	
	# Check for service-based demand boosts
	aircraft_services = get_aircraft_services(aircraft_id)
	now = _now_ts()
	service_window = 24 * 3600  # 24 hours
	
	# Catering and cleaning boost demand
	if aircraft_services.get("catering", 0) > (now - service_window):
		passengers = min(cap, int(passengers * 1.1))  # 10% boost
	if aircraft_services.get("cleaning", 0) > (now - service_window):
		passengers = min(cap, int(passengers * 1.05))  # 5% boost
	
	# Generate weight and balance manifest
	weight_manifest = generate_weight_manifest(passengers, aircraft_id)
	
	flight = {
		"flight_id": _new_id("flight"),
		"aircraft_id": aircraft_id,
		"route": route,
		"dest": dest,
		"origin": origin,
		"duration_hours": duration_hours,
		"passengers": passengers,
		"ticket_price": ticket_price,
		"eta_ts": _now_ts() + int(duration_hours * 3600),
		"booking_id": None,
		"pax_requested": pax_requested,
		"baseline_price": int(round(baseline)),
		"demand_note": None,
		"preflight_issue": None,
		"cabin_comfort": float(comfort),
		"pilot_assigned": pilot_assigned,
		"pilot_skill_bonus": pilot_skill_bonus,
		"seasonal_multiplier": seasonal_mult,
		"weight_manifest": weight_manifest,
	}
	
	state.setdefault("active_flights", []).append(flight)
	save_state(state)


def get_aircraft_oil_info(type_code: str) -> Dict[str, Any]:
	"""Get oil information for an aircraft type (capacity, minimum).
	Returns None for airliners that don't track oil."""
	from catalog import aircraft_catalog
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(type_code)
	if info and "oil_capacity" in info:
		return {
			"capacity": float(info.get("oil_capacity", 16.0)),
			"minimum": float(info.get("oil_minimum", 6.0)),
		}
	return None  # Airliners don't track oil


def walkaround_check(aircraft_id: str) -> Dict[str, Any]:
	"""Perform walkaround inspection. Returns findings including snags and oil level.
	
	Args:
		aircraft_id: ID of aircraft to check
	
	Returns:
		Dict with:
		- 'snags': List of snag dicts with 'component', 'severity', 'description', 'mel' (bool)
		- 'oil_level': Current oil level (None for airliners)
		- 'oil_capacity': Oil capacity (None for airliners)
		- 'oil_minimum': Minimum oil level (None for airliners)
		- 'oil_low': bool indicating if oil is below required (False for airliners)
		- 'oil_critical': bool indicating if oil is critically low (False for airliners)
	"""
	import random
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Check if this aircraft tracks oil (smaller planes only)
	oil_info = get_aircraft_oil_info(aircraft.get("type_code"))
	
	if oil_info is None:
		# Airliner - no oil tracking needed
		# Still check for snags
		snags = list(aircraft.get("snags", []))
		reliability = float(aircraft.get("reliability", 1.0))
		
		# Check maintenance status for snag probability
		a_hours = float(aircraft.get("hours_since_a_check", 0.0))
		b_hours = float(aircraft.get("hours_since_b_check", 0.0))
		c_hours = float(aircraft.get("hours_since_c_check", 0.0))
		
		# Base snag probability increases with low reliability and overdue maintenance
		base_probability = (1.0 - reliability) * 0.3
		if a_hours > MAINTENANCE_INTERVALS["A"]:
			base_probability += 0.15
		if b_hours > MAINTENANCE_INTERVALS["B"]:
			base_probability += 0.20
		if c_hours > MAINTENANCE_INTERVALS["C"]:
			base_probability += 0.30
		
		# Random chance to discover new snag during walkaround
		random.seed(int(time.time()) + hash(aircraft_id))
		if random.random() < base_probability:
			# Generate a new snag with detailed descriptions (same as smaller planes)
			components = [
				"Landing Gear", "Navigation Lights", "Tire Pressure", "Engine Cowling",
				"Control Surfaces", "Antenna", "Pitot Tube", "Static Port", "Fuel Cap",
				"Oil Cap", "Hydraulic System", "Brake System", "Communication System",
				"Transponder", "Weather Radar", "Cabin Door Seal", "Emergency Exit"
			]
			
			# Use simplified but realistic descriptions for airliners
			component_issues_simple = {
				"Landing Gear": {"Minor": "Small crack in nose gear strut", "Major": "Hydraulic leak in landing gear actuator", "Critical": "Structural crack in main landing gear"},
				"Navigation Lights": {"Minor": "Dim navigation light on left wingtip", "Major": "Inoperative anti-collision beacon", "Critical": "Complete failure of navigation lights"},
				"Tire Pressure": {"Minor": "Slightly low pressure in nose tire", "Major": "Significantly low tire pressure", "Critical": "Flat tire - immediate replacement required"},
				"Engine Cowling": {"Minor": "Loose fastener on engine cowling", "Major": "Cracked engine cowling panel", "Critical": "Structural failure of engine cowling"},
				"Control Surfaces": {"Minor": "Slight play in aileron control", "Major": "Excessive play in control surface", "Critical": "Control surface failure - flight prohibited"},
				"Antenna": {"Minor": "Loose antenna mounting", "Major": "Damaged antenna requiring replacement", "Critical": "Antenna failure - communication loss"},
				"Pitot Tube": {"Minor": "Minor blockage in pitot tube", "Major": "Significant blockage affecting airspeed", "Critical": "Complete pitot tube blockage"},
				"Static Port": {"Minor": "Minor blockage in static port", "Major": "Significant static port blockage", "Critical": "Complete static port failure"},
				"Fuel Cap": {"Minor": "Loose fuel cap", "Major": "Damaged fuel cap seal", "Critical": "Fuel cap failure - fuel leak risk"},
				"Oil Cap": {"Minor": "Loose oil filler cap", "Major": "Damaged oil cap seal", "Critical": "Oil cap failure - oil leak"},
				"Hydraulic System": {"Minor": "Minor hydraulic fluid leak", "Major": "Significant hydraulic leak", "Critical": "Critical hydraulic system failure"},
				"Brake System": {"Minor": "Minor brake pad wear", "Major": "Significant brake pad wear", "Critical": "Critical brake system failure"},
				"Communication System": {"Minor": "Radio static on one frequency", "Major": "Significant radio communication issues", "Critical": "Complete communication system failure"},
				"Transponder": {"Minor": "Transponder intermittent operation", "Major": "Transponder system degradation", "Critical": "Transponder failure - no ATC identification"},
				"Weather Radar": {"Minor": "Minor weather radar display issue", "Major": "Significant weather radar degradation", "Critical": "Weather radar complete failure"},
				"Cabin Door Seal": {"Minor": "Minor door seal wear", "Major": "Significant door seal damage", "Critical": "Critical door seal failure"},
				"Emergency Exit": {"Minor": "Minor emergency exit handle wear", "Major": "Emergency exit mechanism issues", "Critical": "Emergency exit failure - safety violation"}
			}
			
			severities = ["Minor", "Major", "Critical"]
			severity_weights = [0.5, 0.3, 0.2]
			
			component = random.choice(components)
			severity = random.choices(severities, weights=severity_weights)[0]
			
			mel_allowed = False
			if severity != "Critical":
				mel_allowed = random.random() < 0.4
			elif component == "Weather Radar":
				mel_allowed = True
			
			description = component_issues_simple.get(component, {}).get(severity, f"{severity} issue with {component}")
			
			new_snag = {
				"snag_id": _new_id("snag"),
				"component": component,
				"severity": severity,
				"description": description,
				"mel": mel_allowed,
				"discovered_at": _now_ts(),
			}
			
			snags.append(new_snag)
			aircraft["snags"] = snags
			save_state(state)
		
		return {
			"snags": snags,
			"oil_level": None,
			"oil_capacity": None,
			"oil_minimum": None,
			"oil_unit": None,
			"oil_low": False,
			"oil_critical": False,
		}
	
	# Smaller plane - track oil
	# Initialize oil tracking if not present (for older aircraft)
	if "oil_level" not in aircraft:
		aircraft["oil_level"] = oil_info["capacity"]
		aircraft["oil_capacity"] = oil_info["capacity"]
		aircraft["oil_minimum"] = oil_info["minimum"]
		aircraft["hours_since_oil_refill"] = 0.0
		aircraft["hours_since_oil_change"] = 0.0  # Track full oil changes separately
	
	# Get oil levels
	oil_level = float(aircraft.get("oil_level", oil_info["capacity"]))
	oil_capacity = float(aircraft.get("oil_capacity", oil_info["capacity"]))
	oil_minimum = float(aircraft.get("oil_minimum", oil_info["minimum"]))
	hours_since_oil = float(aircraft.get("hours_since_oil_refill", 0.0))
	hours_since_oil_change = float(aircraft.get("hours_since_oil_change", 0.0))
	
	# Oil consumption: approximately 0.11 quarts per flight hour
	# Planes typically need top-ups monthly (about 30 days = ~720 hours of operation)
	# Calculate monthly consumption: capacity - minimum should last about a month
	# For example, if capacity is 32 and minimum is 6, that's 26 quarts for ~720 hours
	# So consumption rate is approximately 0.11 quarts per hour
	oil_consumed = hours_since_oil * 0.11  # ~0.11 quarts per hour
	current_oil = max(0.0, oil_capacity - oil_consumed)
	aircraft["oil_level"] = current_oil
	
	# Check against minimum level and capacity
	# Oil is low if below 50% of capacity, or if approaching minimum
	oil_low = current_oil < (oil_capacity * 0.5)  # Below 50% of capacity is low
	oil_critical = current_oil < oil_minimum  # Below minimum is critical
	
	# Check oil change status (should be done every 50 hours)
	oil_change_interval = 50.0
	oil_change_due = hours_since_oil_change >= oil_change_interval
	oil_change_overdue = hours_since_oil_change > (oil_change_interval * 1.2)  # 20% over is overdue
	
	# Check for snags
	# Snags can be discovered during walkaround
	# Probability increases with:
	# - Low reliability
	# - Overdue maintenance
	# - Existing snags (maintenance issues compound)
	
	snags = list(aircraft.get("snags", []))
	reliability = float(aircraft.get("reliability", 1.0))
	
	# Check maintenance status for snag probability
	a_hours = float(aircraft.get("hours_since_a_check", 0.0))
	b_hours = float(aircraft.get("hours_since_b_check", 0.0))
	c_hours = float(aircraft.get("hours_since_c_check", 0.0))
	
	# Base snag probability increases with low reliability and overdue maintenance
	base_probability = (1.0 - reliability) * 0.3
	if a_hours > MAINTENANCE_INTERVALS["A"]:
		base_probability += 0.15
	if b_hours > MAINTENANCE_INTERVALS["B"]:
		base_probability += 0.20
	if c_hours > MAINTENANCE_INTERVALS["C"]:
		base_probability += 0.30
	
	# Random chance to discover new snag during walkaround
	random.seed(int(time.time()) + hash(aircraft_id))
	if random.random() < base_probability:
		# Generate a new snag with detailed, realistic descriptions
		components = [
			"Landing Gear", "Navigation Lights", "Tire Pressure", "Engine Cowling",
			"Control Surfaces", "Antenna", "Pitot Tube", "Static Port", "Fuel Cap",
			"Oil Cap", "Hydraulic System", "Brake System", "Communication System",
			"Transponder", "Weather Radar", "Cabin Door Seal", "Emergency Exit"
		]
		
		# Detailed component-specific issues
		component_issues = {
			"Landing Gear": {
				"Minor": ["Small crack in nose gear strut", "Loose rivet on right main gear door", "Minor corrosion on landing gear leg"],
				"Major": ["Significant wear on main landing gear tires", "Hydraulic leak in landing gear actuator", "Damaged gear door mechanism"],
				"Critical": ["Structural crack in main landing gear", "Landing gear fails to retract", "Critical hydraulic failure in gear system"]
			},
			"Navigation Lights": {
				"Minor": ["Dim navigation light on left wingtip", "Flickering strobe light", "Loose connection on position light"],
				"Major": ["Navigation light assembly cracked", "Inoperative anti-collision beacon", "Wiring issue in lighting system"],
				"Critical": ["Complete failure of navigation lights", "Electrical short in lighting circuit", "Critical visibility issue - lights non-functional"]
			},
			"Tire Pressure": {
				"Minor": ["Slightly low pressure in nose tire (5 PSI)", "Uneven wear pattern on main tires", "Minor sidewall scuffing"],
				"Major": ["Significantly low tire pressure (15+ PSI)", "Excessive wear requiring replacement", "Tire damage from FOD"],
				"Critical": ["Flat tire - immediate replacement required", "Tire blowout risk", "Critical tire failure - flight prohibited"]
			},
			"Engine Cowling": {
				"Minor": ["Loose fastener on engine cowling", "Minor scratch on cowling surface", "Small dent in cowling"],
				"Major": ["Cracked engine cowling panel", "Missing cowling fasteners", "Significant damage to cowling"],
				"Critical": ["Structural failure of engine cowling", "Cowling separation risk", "Critical engine exposure - flight prohibited"]
			},
			"Control Surfaces": {
				"Minor": ["Slight play in aileron control", "Minor binding in elevator trim", "Small dent in rudder"],
				"Major": ["Excessive play in control surface", "Damaged control surface hinge", "Significant control surface damage"],
				"Critical": ["Control surface failure - flight prohibited", "Loss of control authority", "Critical flight control malfunction"]
			},
			"Antenna": {
				"Minor": ["Loose antenna mounting", "Minor corrosion on antenna base", "Slight damage to antenna housing"],
				"Major": ["Damaged antenna requiring replacement", "Antenna base structural issue", "Signal degradation from damage"],
				"Critical": ["Antenna failure - communication loss", "Structural failure of antenna mount", "Critical communication failure"]
			},
			"Pitot Tube": {
				"Minor": ["Minor blockage in pitot tube", "Small dent on pitot tube", "Slight corrosion on tube"],
				"Major": ["Significant blockage affecting airspeed", "Damaged pitot tube housing", "Pitot tube heating system failure"],
				"Critical": ["Complete pitot tube blockage", "Critical airspeed indication failure", "Flight prohibited - no airspeed data"]
			},
			"Static Port": {
				"Minor": ["Minor blockage in static port", "Slight damage to static port", "Minor corrosion"],
				"Major": ["Significant static port blockage", "Damaged static port housing", "Altitude indication issues"],
				"Critical": ["Complete static port failure", "Critical altitude indication loss", "Flight prohibited - no altitude data"]
			},
			"Fuel Cap": {
				"Minor": ["Loose fuel cap", "Minor seal damage on fuel cap", "Slight fuel cap wear"],
				"Major": ["Damaged fuel cap seal", "Fuel cap not securing properly", "Significant fuel cap damage"],
				"Critical": ["Fuel cap failure - fuel leak risk", "Critical fuel system integrity issue", "Flight prohibited - fuel leak"]
			},
			"Oil Cap": {
				"Minor": ["Loose oil filler cap", "Minor seal wear on oil cap", "Slight oil cap damage"],
				"Major": ["Damaged oil cap seal", "Oil cap not securing", "Significant oil cap issue"],
				"Critical": ["Oil cap failure - oil leak", "Critical engine oil system issue", "Flight prohibited - oil leak"]
			},
			"Hydraulic System": {
				"Minor": ["Minor hydraulic fluid leak", "Slight pressure drop", "Small hydraulic line abrasion"],
				"Major": ["Significant hydraulic leak", "Hydraulic system pressure issues", "Damaged hydraulic line"],
				"Critical": ["Critical hydraulic system failure", "Loss of hydraulic pressure", "Flight prohibited - hydraulic failure"]
			},
			"Brake System": {
				"Minor": ["Minor brake pad wear", "Slight brake fluid level low", "Minor brake line wear"],
				"Major": ["Significant brake pad wear", "Brake fluid leak", "Damaged brake components"],
				"Critical": ["Critical brake system failure", "Loss of braking capability", "Flight prohibited - brake failure"]
			},
			"Communication System": {
				"Minor": ["Radio static on one frequency", "Minor antenna connection issue", "Slight radio interference"],
				"Major": ["Significant radio communication issues", "Antenna connection failure", "Radio system degradation"],
				"Critical": ["Complete communication system failure", "Loss of radio communication", "Flight prohibited - no comms"]
			},
			"Transponder": {
				"Minor": ["Transponder intermittent operation", "Minor transponder antenna issue", "Slight transponder glitch"],
				"Major": ["Transponder system degradation", "Significant transponder issues", "Antenna connection problems"],
				"Critical": ["Transponder failure - no ATC identification", "Complete transponder malfunction", "Flight prohibited - no transponder"]
			},
			"Weather Radar": {
				"Minor": ["Minor weather radar display issue", "Slight radar antenna misalignment", "Minor radar interference"],
				"Major": ["Significant weather radar degradation", "Radar antenna damage", "Weather radar system issues"],
				"Critical": ["Weather radar complete failure", "Critical weather detection loss", "MEL eligible - weather radar inoperative"]
			},
			"Cabin Door Seal": {
				"Minor": ["Minor door seal wear", "Slight door seal compression", "Minor door seal gap"],
				"Major": ["Significant door seal damage", "Door seal not sealing properly", "Door seal replacement needed"],
				"Critical": ["Critical door seal failure", "Cabin pressure integrity compromised", "Flight prohibited - pressurization issue"]
			},
			"Emergency Exit": {
				"Minor": ["Minor emergency exit handle wear", "Slight emergency exit marking fade", "Minor emergency exit mechanism play"],
				"Major": ["Emergency exit mechanism issues", "Damaged emergency exit handle", "Emergency exit not functioning properly"],
				"Critical": ["Emergency exit failure - safety violation", "Critical emergency exit malfunction", "Flight prohibited - safety issue"]
			}
		}
		
		severities = ["Minor", "Major", "Critical"]
		severity_weights = [0.5, 0.3, 0.2]  # 50% minor, 30% major, 20% critical
		
		component = random.choice(components)
		severity = random.choices(severities, weights=severity_weights)[0]
		
		# MEL (Minimum Equipment List) - some items can be deferred
		# Critical items cannot be deferred (except weather radar which can be MEL)
		mel_allowed = False
		if severity != "Critical":
			mel_allowed = random.random() < 0.4  # 40% of non-critical can be MEL
		elif component == "Weather Radar":
			mel_allowed = True  # Weather radar can be MEL even if critical
		
		# Get detailed description based on component and severity
		if component in component_issues and severity in component_issues[component]:
			description = random.choice(component_issues[component][severity])
		else:
			# Fallback to generic descriptions
			descriptions = {
				"Minor": f"Minor issue with {component}",
				"Major": f"Significant issue with {component} requiring attention",
				"Critical": f"CRITICAL: {component} failure - flight prohibited"
			}
			description = descriptions[severity]
		
		new_snag = {
			"snag_id": _new_id("snag"),
			"component": component,
			"severity": severity,
			"description": description,
			"mel": mel_allowed,
			"discovered_at": _now_ts(),
		}
		
		snags.append(new_snag)
		aircraft["snags"] = snags
		save_state(state)
	
	# Check tire condition for smaller planes
	tire_condition = None
	tire_wear = None
	if oil_info is not None:  # Only for smaller planes
		# Tire wear increases with flight hours and reliability
		# Initialize tire condition if not present
		if "tire_wear_percent" not in aircraft:
			aircraft["tire_wear_percent"] = 5.0  # Start with 5% wear
		
		# Tire wear increases with flight hours and decreases with reliability
		wear_rate = 0.5  # 0.5% wear per flight hour
		current_wear = float(aircraft.get("tire_wear_percent", 5.0))
		# Add some wear based on hours since last maintenance
		hours_since_maint = float(aircraft.get("hours_since_maintenance", 0.0))
		additional_wear = hours_since_maint * (wear_rate / 100.0)
		tire_wear = min(100.0, current_wear + additional_wear)
		aircraft["tire_wear_percent"] = tire_wear
		
		# Determine tire condition
		if tire_wear < 30:
			tire_condition = "Good"
		elif tire_wear < 60:
			tire_condition = "Fair"
		elif tire_wear < 85:
			tire_condition = "Poor"
		else:
			tire_condition = "Critical"
	
	return {
		"snags": snags,
		"oil_level": current_oil,
		"oil_capacity": oil_capacity,
		"oil_minimum": oil_minimum,
		"oil_unit": "quarts",  # Always quarts for smaller planes
		"oil_low": oil_low,
		"oil_critical": oil_critical,
		"hours_since_oil_change": hours_since_oil_change,
		"oil_change_interval": oil_change_interval,
		"oil_change_due": oil_change_due,
		"oil_change_overdue": oil_change_overdue,
		"tire_condition": tire_condition,
		"tire_wear": tire_wear,
	}


def preflight_check(aircraft_id: str, flight_hours: float = 0.0) -> Dict[str, Any]:
	"""Perform preflight check. Returns any issues found.
	
	Args:
		aircraft_id: ID of aircraft to check
		flight_hours: Optional flight hours for this flight (for validation)
	
	Returns:
		Dict with 'failed', 'component', 'mel', 'severity' keys if issue found,
		or empty dict if no issues
	"""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Check if aircraft is grounded
	if aircraft.get("grounded", False):
		return {
			"failed": True,
			"component": "Aircraft Status",
			"severity": "Critical",
			"mel": False,
		}
	
	# Check C check - critical
	c_hours = float(aircraft.get("hours_since_c_check", 0.0))
	if c_hours > MAINTENANCE_INTERVALS["C"] * 1.2:
		aircraft["grounded"] = True
		return {
			"failed": True,
			"component": "C Check",
			"severity": "Critical",
			"mel": False,
		}
	
	# Check if adding flight hours would exceed C check limit
	if flight_hours > 0:
		projected_c_hours = c_hours + flight_hours
		if projected_c_hours > MAINTENANCE_INTERVALS["C"] * 1.2:
			return {
				"failed": True,
				"component": "C Check Projection",
				"severity": "Critical",
				"mel": False,
			}
	
	# No issues found
	return {
		"failed": False,
	}


def refill_aircraft_oil(aircraft_id: str) -> None:
	"""Top up aircraft oil to full capacity. This is a regular top-up, not a full oil change.
	Does NOT reset the oil change timer. Only works for smaller planes."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Check if this aircraft tracks oil
	if "oil_level" not in aircraft or "oil_capacity" not in aircraft:
		raise ValueError("This aircraft type does not require manual oil refills (airliners manage oil automatically).")
	
	oil_capacity = float(aircraft.get("oil_capacity", 32.0))
	current_oil = float(aircraft.get("oil_level", 0.0))
	oil_needed = oil_capacity - current_oil
	
	if oil_needed <= 0:
		return  # Already full
	
	# Cost: $50 per quart
	cost = int(oil_needed * 50)
	if cost > state.get("cash", 0):
		raise ValueError(f"Insufficient cash. Need ${cost:,} for oil refill.")
	
	aircraft["oil_level"] = oil_capacity
	aircraft["hours_since_oil_refill"] = 0.0
	# Note: hours_since_oil_change is NOT reset - this is just a top-up
	state["cash"] = int(state.get("cash", 0)) - cost
	_add_ledger(state, "oil", -cost, f"Oil top-up {aircraft_id} ({oil_needed:.1f} quarts)")
	save_state(state)


def change_aircraft_oil(aircraft_id: str) -> None:
	"""Perform a full oil change. This resets the oil change timer and should be done every 50 hours.
	More expensive than a regular top-up. Only works for smaller planes."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	# Check if this aircraft tracks oil
	if "oil_level" not in aircraft or "oil_capacity" not in aircraft:
		raise ValueError("This aircraft type does not require manual oil changes (airliners manage oil automatically).")
	
	oil_capacity = float(aircraft.get("oil_capacity", 32.0))
	
	# Full oil change cost: $100 per quart (more expensive than top-up)
	# Includes cost of new oil and labor
	cost = int(oil_capacity * 100)
	if cost > state.get("cash", 0):
		raise ValueError(f"Insufficient cash. Need ${cost:,} for full oil change.")
	
	aircraft["oil_level"] = oil_capacity
	aircraft["hours_since_oil_refill"] = 0.0
	aircraft["hours_since_oil_change"] = 0.0  # Reset oil change timer
	state["cash"] = int(state.get("cash", 0)) - cost
	_add_ledger(state, "oil", -cost, f"Full oil change {aircraft_id} ({oil_capacity:.1f} quarts)")
	save_state(state)


def calculate_snag_penalties(snags: List[Dict], oil_low: bool, oil_critical: bool) -> Dict[str, Any]:
	"""Calculate penalties for flying with snags or low oil.
	
	Returns:
		Dict with 'total_penalty', 'reputation_penalty', 'reasons' list
	"""
	penalty = 0
	reputation_penalty = 0.0
	reasons = []
	
	# Penalties for snags
	for snag in snags:
		severity = snag.get("severity", "Minor")
		if severity == "Minor":
			penalty += 5000
			reputation_penalty -= 0.5
			reasons.append(f"Minor snag: {snag.get('component')} - $5,000 fine")
		elif severity == "Major":
			penalty += 25000
			reputation_penalty -= 1.5
			reasons.append(f"Major snag: {snag.get('component')} - $25,000 fine")
		elif severity == "Critical":
			penalty += 100000
			reputation_penalty -= 5.0
			reasons.append(f"CRITICAL snag: {snag.get('component')} - $100,000 fine")
	
	# Penalties for low oil
	if oil_critical:
		penalty += 50000
		reputation_penalty -= 3.0
		reasons.append("CRITICAL: Oil level critically low - $50,000 fine")
	elif oil_low:
		penalty += 15000
		reputation_penalty -= 1.0
		reasons.append("Warning: Oil level low - $15,000 fine")
	
	return {
		"total_penalty": penalty,
		"reputation_penalty": reputation_penalty,
		"reasons": reasons,
	}


def clear_snag(aircraft_id: str, snag_id: str) -> None:
	"""Clear a snag from an aircraft (typically after maintenance)."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	snags = aircraft.get("snags", [])
	aircraft["snags"] = [s for s in snags if s.get("snag_id") != snag_id]
	save_state(state)


def ground_aircraft(aircraft_id: str, reason: str = None) -> None:
	"""Ground an aircraft."""
	state = get_state()
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	if not aircraft:
		raise ValueError("Aircraft not found")
	
	aircraft["grounded"] = True
	save_state(state)


def cancel_flight(flight_id: str) -> Dict[str, Any]:
	"""Cancel an active flight.
	
	Args:
		flight_id: ID of the flight to cancel
		
	Returns:
		Dict with cancellation details including penalties
	"""
	state = get_state()
	flights = state.get("active_flights", [])
	idx = next((i for i, f in enumerate(flights) if f.get("flight_id") == flight_id), None)
	if idx is None:
		raise ValueError("Flight not found")
	
	flight = flights.pop(idx)
	aircraft_id = flight.get("aircraft_id")
	passengers = int(flight.get("passengers", 0))
	ticket_price = int(flight.get("ticket_price", 0))
	
	# Calculate penalties
	# Refund cost: 10% of ticket revenue (processing fees)
	refund_cost = int((passengers * ticket_price) * 0.10)
	
	# Reputation penalty: -0.5 per passenger (disappointed customers)
	reputation_penalty = -0.5 * passengers
	
	# Apply reputation change
	old_reputation = float(state.get("company", {}).get("reputation", 0.0))
	new_reputation = update_reputation(reputation_penalty, state)
	
	# Deduct refund cost
	state["cash"] = int(state.get("cash", 0)) - refund_cost
	_add_ledger(state, "flight_cancellation", -refund_cost, f"Flight {flight_id} cancellation refunds")
	
	# Save state
	save_state(state)
	
	return {
		"flight_id": flight_id,
		"aircraft_id": aircraft_id,
		"route": flight.get("route"),
		"passengers": passengers,
		"refund_cost": refund_cost,
		"reputation_penalty": reputation_penalty,
		"old_reputation": old_reputation,
		"new_reputation": new_reputation,
	}


def end_flight(flight_id: str, flight_quality_answers: Dict[str, Any] = None) -> Dict[str, Any]:
	"""End a flight and calculate revenue, costs, and reputation effects.
	
	Args:
		flight_id: ID of the flight to end
		flight_quality_answers: Optional dict of flight quality questionnaire answers.
			Keys: "touchdown_fpm", "departure_timing", "custom_rep_change" (optional)
			If provided, reputation will be calculated based on these values
	"""
	state = get_state()
	flights = state.get("active_flights", [])
	idx = next((i for i, f in enumerate(flights) if f.get("flight_id") == flight_id), None)
	if idx is None:
		raise ValueError("Flight not found")
	
	flight = flights.pop(idx)
	aircraft_id = flight.get("aircraft_id")
	aircraft = next((ac for ac in state.get("fleet", []) if ac.get("id") == aircraft_id), None)
	
	# Calculate revenue
	revenue = int(flight.get("passengers", 0)) * int(flight.get("ticket_price", 0))
	
	# Calculate costs
	from catalog import aircraft_catalog
	cat = {c["type_code"]: c for c in aircraft_catalog()}
	info = cat.get(aircraft.get("type_code")) if aircraft else None
	hourly_cost = float(info.get("hourly_cost", 2000)) if info else 2000.0
	flight_hours = float(flight.get("duration_hours", 0))
	
	# Apply service effects
	aircraft_services = get_aircraft_services(aircraft_id) if aircraft_id else {}
	now = _now_ts()
	service_window = 24 * 3600
	
	cost_multiplier = 1.0
	refueling_service = aircraft_services.get("refueling")
	if refueling_service:
		refuel_timestamp = refueling_service.get("timestamp") if isinstance(refueling_service, dict) else refueling_service
		if refuel_timestamp > (now - service_window):
			cost_multiplier -= 0.05
	if aircraft_services.get("ground_power", 0) > (now - service_window):
		cost_multiplier -= 0.02
	
	# Apply fuel price multiplier
	fuel_mult = get_fuel_price_multiplier()
	cost_multiplier *= fuel_mult
	
	cost = int(hourly_cost * flight_hours * cost_multiplier)
	
	# Calculate penalties
	penalty = 0
	penalty_reasons = []
	
	# Apply hours and check maintenance repercussions
	if aircraft is None:
		# If aircraft missing, just take the cost and revenue into cash
		# Get current reputation from state
		old_reputation = float(state.get("company", {}).get("reputation", 0.0))
		new_reputation = old_reputation
		reputation_change = 0.0
		reputation_bonus = 0
		
		# Only calculate reputation if we have valid answers with at least touchdown or departure timing
		if flight_quality_answers and (flight_quality_answers.get("touchdown_fpm") or flight_quality_answers.get("departure_timing")):
			# Calculate reputation from answers
			reputation_change = _calculate_reputation_from_answers(flight_quality_answers)
			
			# Add pilot skill bonus
			pilot_skill_bonus = float(flight.get("pilot_skill_bonus", 0.0))
			reputation_change += pilot_skill_bonus
			
			new_reputation = update_reputation(reputation_change, state)
			reputation_bonus = calculate_reputation_bonus(new_reputation, revenue)
		
		net = revenue - cost + reputation_bonus
		net = net * 3  # Triple earnings
		state["cash"] = int(state.get("cash", 0)) + net
		save_state(state)
		return {
			"revenue": revenue,
			"cost": cost,
			"penalty": penalty,
			"reputation_bonus": reputation_bonus,
			"net": net,
			"reasons": [],
			"location": "UNKNOWN",
			"reliability": None,
			"grounded": False,
			"hourly_cost": hourly_cost,
			"duration_hours": flight_hours,
			"reputation_change": reputation_change,
			"old_reputation": old_reputation,
			"new_reputation": new_reputation,
		}
	
	# Update aircraft hours
	aircraft["hours_since_maintenance"] = float(aircraft.get("hours_since_maintenance", 0.0)) + flight_hours
	if "hours_since_a_check" not in aircraft:
		aircraft["hours_since_a_check"] = float(aircraft.get("hours_since_a_check", 0.0))
	if "hours_since_b_check" not in aircraft:
		aircraft["hours_since_b_check"] = float(aircraft.get("hours_since_b_check", 0.0))
	if "hours_since_c_check" not in aircraft:
		aircraft["hours_since_c_check"] = float(aircraft.get("hours_since_c_check", 0.0))
	
	aircraft["hours_since_a_check"] = float(aircraft.get("hours_since_a_check", 0.0)) + flight_hours
	aircraft["hours_since_b_check"] = float(aircraft.get("hours_since_b_check", 0.0)) + flight_hours
	aircraft["hours_since_c_check"] = float(aircraft.get("hours_since_c_check", 0.0)) + flight_hours
	
	# Update oil consumption (only for smaller planes that track oil)
	if "oil_level" in aircraft:
		# Smaller plane - track oil consumption
		aircraft["hours_since_oil_refill"] = float(aircraft.get("hours_since_oil_refill", 0.0)) + flight_hours
		aircraft["hours_since_oil_change"] = float(aircraft.get("hours_since_oil_change", 0.0)) + flight_hours
		oil_consumed = flight_hours * 0.11  # ~0.11 quarts per hour
		current_oil = float(aircraft.get("oil_level", aircraft.get("oil_capacity", 32.0)))
		aircraft["oil_level"] = max(0.0, current_oil - oil_consumed)
	# Airliners don't consume oil (managed automatically by maintenance)
	
	# Check for due/overdue maintenance
	maintenance_warnings = []
	
	# Check oil change interval (50 hours for smaller planes)
	if "oil_level" in aircraft:
		hours_since_oil_change = float(aircraft.get("hours_since_oil_change", 0.0))
		oil_change_interval = 50.0
		if hours_since_oil_change > oil_change_interval:
			overdue_factor = hours_since_oil_change / oil_change_interval
			# If overdue and something goes wrong (snags, reliability issues), apply fine
			has_snags = len(aircraft.get("snags", [])) > 0
			reliability = float(aircraft.get("reliability", 1.0))
			if has_snags or reliability < 0.9:
				# Fine for overdue oil change when problems occur
				fine = int(5000 * (overdue_factor - 1.0))
				penalty += fine
				penalty_reasons.append(f"Overdue oil change ({hours_since_oil_change:.0f}h / {oil_change_interval:.0f}h) - Fine: ${fine:,}")
				aircraft["reliability"] = max(0.0, reliability - 0.01 * (overdue_factor - 1.0))
	
	# Check A Check
	a_hours = aircraft["hours_since_a_check"]
	a_interval = MAINTENANCE_INTERVALS["A"]
	if a_hours >= a_interval:
		overdue_factor = a_hours / a_interval
		if overdue_factor > 1.2:
			p = int(5000 * (overdue_factor - 1.0))
			penalty += p
			maintenance_warnings.append(f"A Check overdue ({a_hours:.0f}h / {a_interval:.0f}h)")
			aircraft["reliability"] = max(0.0, float(aircraft.get("reliability", 1.0)) - 0.02 * (overdue_factor - 1.0))
	
	# Check B Check
	b_hours = aircraft["hours_since_b_check"]
	b_interval = MAINTENANCE_INTERVALS["B"]
	if b_hours >= b_interval:
		overdue_factor = b_hours / b_interval
		if overdue_factor > 1.1:
			p = int(15000 * (overdue_factor - 1.0))
			penalty += p
			maintenance_warnings.append(f"B Check overdue ({b_hours:.0f}h / {b_interval:.0f}h)")
			aircraft["reliability"] = max(0.0, float(aircraft.get("reliability", 1.0)) - 0.05 * (overdue_factor - 1.0))
	
	# Check C Check
	c_hours = aircraft["hours_since_c_check"]
	c_interval = MAINTENANCE_INTERVALS["C"]
	if c_hours >= c_interval:
		overdue_factor = c_hours / c_interval
		if overdue_factor > 1.05:
			p = int(50000 * (overdue_factor - 1.0))
			penalty += p
			maintenance_warnings.append(f"C Check overdue ({c_hours:.0f}h / {c_interval:.0f}h) - CRITICAL")
			aircraft["reliability"] = max(0.0, float(aircraft.get("reliability", 1.0)) - 0.15 * (overdue_factor - 1.0))
			if overdue_factor > 1.2:
				aircraft["grounded"] = True
				penalty_reasons.append("Aircraft grounded: C Check critically overdue")
	
	if maintenance_warnings:
		penalty_reasons.extend(maintenance_warnings)
	
	# Legacy maintenance check
	if aircraft["hours_since_maintenance"] > float(aircraft.get("maintenance_due_hours", 300.0)):
		overdue_factor = aircraft["hours_since_maintenance"] / float(aircraft.get("maintenance_due_hours", 300.0))
		if overdue_factor > 1.5:
			aircraft["reliability"] = max(0.0, float(aircraft.get("reliability", 1.0)) - 0.1 * (overdue_factor - 1.5))
			if aircraft["reliability"] < 0.5:
				aircraft["grounded"] = True
	
	# Move to destination
	dest = flight.get("dest") or aircraft.get("location", "HOME")
	aircraft["location"] = dest
	final_location = dest
	if not _has_owned_parking(state, dest):
		penalty_reasons.append(f"No owned parking at {dest}; overnight fee may apply")
	
	# Calculate reputation change and bonus
	old_reputation = float(state.get("company", {}).get("reputation", 0.0))
	reputation_change = 0.0
	reputation_bonus = 0
	new_reputation = old_reputation
	
	# Only calculate reputation if we have valid answers with at least touchdown or departure timing
	if flight_quality_answers and (flight_quality_answers.get("touchdown_fpm") or flight_quality_answers.get("departure_timing")):
		reputation_change = _calculate_reputation_from_answers(flight_quality_answers)
		new_reputation = update_reputation(reputation_change, state)
	
	# Generate passenger feedback (before calculating bonus so feedback affects bonus)
	feedback = generate_passenger_feedback({
		"new_reputation": new_reputation,
		"pax_boarded": flight.get("passengers", 0),
		"pax_requested": flight.get("pax_requested", 0),
		"cabin_comfort": flight.get("cabin_comfort", 1.0),
		"reputation_change": reputation_change,
	})
	
	# Apply feedback reputation impact
	if feedback.get("reputation_impact", 0) != 0:
		feedback_rep_change = feedback["reputation_impact"]
		new_reputation = update_reputation(feedback_rep_change, state)
		reputation_change += feedback_rep_change
	
	# Calculate reputation bonus after all reputation changes
	reputation_bonus = calculate_reputation_bonus(new_reputation, revenue)
	
	net = revenue - cost - penalty + reputation_bonus
	net = net * 3  # Triple earnings
	state["cash"] = int(state.get("cash", 0)) + net
	state["active_flights"] = flights
	
	# Record completed flight for statistics
	completed_flight = {
		"timestamp": _now_ts(),
		"route": flight.get("route", "UNKNOWN"),
		"revenue": revenue,
		"cost": cost,
		"passengers": flight.get("passengers", 0),
		"capacity": flight.get("pax_requested", 0),
	}
	state.setdefault("completed_flights", []).append(completed_flight)
	# Keep last 1000 completed flights
	if len(state["completed_flights"]) > 1000:
		state["completed_flights"] = state["completed_flights"][-1000:]
	
	# Check for achievements
	new_achievements = check_and_award_achievements()
	
	# Add to ledger
	ledger_note = f"{flight.get('route')} net; penalties: {', '.join(penalty_reasons) if penalty_reasons else 'none'}"
	if reputation_bonus != 0:
		ledger_note += f"; rep bonus: ${reputation_bonus:,}"
	_add_ledger(state, "flight", net, ledger_note)
	save_state(state)
	
	return {
		"revenue": revenue,
		"cost": cost,
		"penalty": penalty,
		"reputation_bonus": reputation_bonus,
		"net": net,
		"reasons": penalty_reasons,
		"location": final_location,
		"reliability": float(aircraft.get("reliability", 1.0)) if aircraft else None,
		"grounded": aircraft.get("grounded", False) if aircraft else False,
		"hourly_cost": hourly_cost,
		"duration_hours": flight_hours,
		"pax_boarded": flight.get("passengers", 0),
		"pax_requested": flight.get("pax_requested", 0),
		"baseline_price": flight.get("baseline_price", 0),
		"cabin_comfort": flight.get("cabin_comfort", 1.0),
		"reputation_change": reputation_change,
		"old_reputation": old_reputation,
		"new_reputation": new_reputation,
		"pilot_assigned": flight.get("pilot_assigned"),
		"passenger_feedback": feedback,
		"new_achievements": new_achievements,
	}


def _calculate_reputation_from_answers(answers: Dict[str, Any]) -> float:
	"""Calculate reputation change from flight quality answers.
	
	Args:
		answers: Dict with optional keys: touchdown_fpm, departure_timing, custom_rep_change
	
	Returns:
		Total reputation change
	"""
	reputation_change = 0.0
	
	# Feet per minute on touchdown (lower is better)
	touchdown_fpm = answers.get("touchdown_fpm")
	if touchdown_fpm is not None:
		try:
			fpm = float(touchdown_fpm)
			if fpm <= 200:
				reputation_change += 2.0
			elif fpm <= 400:
				reputation_change += 1.0
			elif fpm <= 600:
				reputation_change += 0.0
			elif fpm <= 800:
				reputation_change -= 1.0
			else:
				reputation_change -= 2.0
		except (ValueError, TypeError):
			pass
	
	# Departure timing (on-time is best)
	departure_timing = answers.get("departure_timing")
	if departure_timing is not None:
		try:
			minutes = float(departure_timing)
			abs_minutes = abs(minutes)
			if abs_minutes == 0:
				reputation_change += 1.0
			elif abs_minutes <= 5:
				reputation_change += 0.5
			elif abs_minutes <= 15:
				reputation_change += 0.0
			elif abs_minutes <= 30:
				reputation_change -= 0.5
			elif abs_minutes <= 60:
				reputation_change -= 1.0
			else:
				reputation_change -= 2.0
		except (ValueError, TypeError):
			pass
	
	# Custom observation (optional - only apply if provided)
	custom_rep_change = answers.get("custom_rep_change")
	if custom_rep_change is not None:
		try:
			custom_change = float(custom_rep_change)
			custom_change = max(-5.0, min(5.0, custom_change))
			reputation_change += custom_change
		except (ValueError, TypeError):
			pass
	
	return reputation_change


def get_seasonal_demand_multiplier() -> float:
	"""Get seasonal demand multiplier based on current date.
	Returns multiplier (0.7 to 1.3) affecting passenger demand."""
	import datetime
	now = datetime.datetime.now()
	month = now.month
	
	# Seasonal multipliers:
	# Dec-Jan: 1.3 (holiday season)
	# Jun-Aug: 1.2 (summer vacation)
	# Mar-May, Sep-Nov: 1.0 (normal)
	# Feb: 0.9 (post-holiday slump)
	
	if month in [12, 1]:
		return 1.3  # Holiday season
	elif month in [6, 7, 8]:
		return 1.2  # Summer vacation
	elif month == 2:
		return 0.9  # Post-holiday slump
	else:
		return 1.0  # Normal season


def update_fuel_prices() -> float:
	"""Update fuel prices with random fluctuations. Returns new multiplier."""
	import random
	state = get_state()
	current_mult = float(state.get("fuel_price_multiplier", 1.0))
	
	# Random walk: fuel prices can change by -5% to +5% per day
	change = random.uniform(-0.05, 0.05)
	new_mult = max(0.7, min(1.5, current_mult + change))  # Clamp between 0.7x and 1.5x
	
	state["fuel_price_multiplier"] = new_mult
	save_state(state)
	return new_mult


def get_fuel_price_multiplier() -> float:
	"""Get current fuel price multiplier."""
	state = get_state()
	return float(state.get("fuel_price_multiplier", 1.0))


def get_achievement_definitions() -> List[Dict[str, Any]]:
	"""Get all achievement definitions. Returns list of achievement dicts with id, name, desc, and check function."""
	return [
		{"id": "first_flight", "name": "First Flight", "desc": "Complete your first flight", "check": lambda s: len(s.get("completed_flights", [])) >= 1},
		{"id": "ten_flights", "name": "10 Flights", "desc": "Complete 10 flights", "check": lambda s: len(s.get("completed_flights", [])) >= 10},
		{"id": "hundred_flights", "name": "100 Flights", "desc": "Complete 100 flights", "check": lambda s: len(s.get("completed_flights", [])) >= 100},
		{"id": "first_aircraft", "name": "First Aircraft", "desc": "Purchase your first aircraft", "check": lambda s: len(s.get("fleet", [])) >= 1},
		{"id": "fleet_of_five", "name": "Fleet of Five", "desc": "Own 5 aircraft", "check": lambda s: len(s.get("fleet", [])) >= 5},
		{"id": "millionaire", "name": "Millionaire", "desc": "Reach $1,000,000 in cash", "check": lambda s: s.get("cash", 0) >= 1000000},
		{"id": "five_million", "name": "Five Million", "desc": "Reach $5,000,000 in cash", "check": lambda s: s.get("cash", 0) >= 5000000},
		{"id": "reputation_50", "name": "Good Reputation", "desc": "Reach 50 reputation", "check": lambda s: s.get("company", {}).get("reputation", 0) >= 50},
		{"id": "reputation_80", "name": "Excellent Reputation", "desc": "Reach 80 reputation", "check": lambda s: s.get("company", {}).get("reputation", 0) >= 80},
		{"id": "first_pilot", "name": "First Pilot", "desc": "Hire your first pilot", "check": lambda s: len(s.get("pilots", [])) >= 1},
		{"id": "pilot_team", "name": "Pilot Team", "desc": "Hire 5 pilots", "check": lambda s: len(s.get("pilots", [])) >= 5},
	]


def check_and_award_achievements() -> List[Dict[str, Any]]:
	"""Check for new achievements and award them. Returns list of newly earned achievements."""
	state = get_state()
	earned = state.get("achievements", [])
	new_achievements = []
	
	# Get achievement definitions
	achievements = get_achievement_definitions()
	
	for ach in achievements:
		if ach["id"] not in earned and ach["check"](state):
			earned.append(ach["id"])
			new_achievements.append({"id": ach["id"], "name": ach["name"], "desc": ach["desc"]})
	
	if new_achievements:
		state["achievements"] = earned
		save_state(state)
	
	return new_achievements


def get_route_profitability_stats(period_days: int = 30) -> List[Dict[str, Any]]:
	"""Get profitability statistics for each route.
	
	Args:
		period_days: Number of days to look back
	
	Returns:
		List of route stats dicts with route, flights, revenue, cost, net, avg_load_factor
	"""
	state = get_state()
	completed = state.get("completed_flights", [])
	now = _now_ts()
	cutoff = now - (period_days * 86400)
	
	recent_flights = [f for f in completed if int(f.get("timestamp", 0)) >= cutoff]
	
	# Group by route
	route_stats = {}
	for flight in recent_flights:
		route = flight.get("route", "UNKNOWN")
		if route not in route_stats:
			route_stats[route] = {
				"route": route,
				"flights": 0,
				"revenue": 0,
				"cost": 0,
				"passengers": 0,
				"capacity": 0,
			}
		
		stats = route_stats[route]
		stats["flights"] += 1
		stats["revenue"] += int(flight.get("revenue", 0))
		stats["cost"] += int(flight.get("cost", 0))
		stats["passengers"] += int(flight.get("passengers", 0))
		stats["capacity"] += int(flight.get("capacity", 0))
	
	# Calculate net and load factor
	result = []
	for route, stats in route_stats.items():
		net = stats["revenue"] - stats["cost"]
		load_factor = (stats["passengers"] / stats["capacity"] * 100) if stats["capacity"] > 0 else 0
		result.append({
			"route": route,
			"flights": stats["flights"],
			"revenue": stats["revenue"],
			"cost": stats["cost"],
			"net": net,
			"avg_load_factor": load_factor,
		})
	
	# Sort by net profit (descending)
	result.sort(key=lambda x: x["net"], reverse=True)
	return result


def generate_passenger_feedback(flight_result: Dict[str, Any]) -> Dict[str, Any]:
	"""Generate passenger feedback based on flight quality.
	
	Args:
		flight_result: Result dict from end_flight
	
	Returns:
		Dict with feedback_type, message, reputation_impact
	"""
	import random
	
	reputation = flight_result.get("new_reputation", 50.0)
	load_factor = 0.0
	pax = flight_result.get("pax_boarded", 0)
	capacity = flight_result.get("pax_requested", 1)
	if capacity > 0:
		load_factor = (pax / capacity) * 100
	
	comfort = flight_result.get("cabin_comfort", 1.0)
	reputation_change = flight_result.get("reputation_change", 0.0)
	
	# Determine feedback type
	if reputation >= 80 and load_factor >= 80 and comfort >= 1.2:
		feedback_type = "excellent"
		messages = [
			"Outstanding service! Will definitely fly again.",
			"Best flight experience ever! Highly recommend.",
			"Exceptional comfort and service. Five stars!",
		]
		rep_impact = random.uniform(0.1, 0.3)
	elif reputation >= 60 and load_factor >= 60:
		feedback_type = "good"
		messages = [
			"Pleasant flight, comfortable seats.",
			"Good service, on-time departure.",
			"Enjoyable experience, will fly again.",
		]
		rep_impact = random.uniform(0.0, 0.1)
	elif reputation < 40 or load_factor < 40:
		feedback_type = "poor"
		messages = [
			"Uncomfortable seats, poor service.",
			"Delayed departure, cramped cabin.",
			"Disappointing experience, won't recommend.",
		]
		rep_impact = random.uniform(-0.5, -0.1)
	else:
		feedback_type = "neutral"
		messages = [
			"Average flight, nothing special.",
			"Met expectations, nothing more.",
		]
		rep_impact = 0.0
	
	return {
		"feedback_type": feedback_type,
		"message": random.choice(messages),
		"reputation_impact": rep_impact,
	}
