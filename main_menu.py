import tkinter as tk
import time
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from typing import Dict, Any
import os
import sys

# Sound system
SOUND_ENABLED = True
SOUNDS_DIR = "sounds"  # Directory for custom sound files
SOUND_AVAILABLE = False
USE_PYGAME = False
USE_PLAYSOUND = False

# Try to initialize sound libraries
try:
	import winsound
	SOUND_AVAILABLE = True
except ImportError:
	pass

# Try pygame for MP3 support
try:
	import pygame
	pygame.mixer.init()
	SOUND_AVAILABLE = True
	USE_PYGAME = True
except ImportError:
	pass

# Try playsound as fallback (simpler, supports MP3)
if not USE_PYGAME:
	try:
		from playsound import playsound
		SOUND_AVAILABLE = True
		USE_PLAYSOUND = True
	except ImportError:
		pass

def play_sound(sound_type: str = "click", use_custom: bool = True):
	"""Play a sound effect. 
	
	Args:
		sound_type: Type of sound ('click', 'success', 'error', 'achievement', 'notification')
		use_custom: If True, tries to play custom sound file first, then falls back to system sounds
	
	Sound files should be placed in the 'sounds/' directory with names like:
	- click.mp3 or click.wav
	- success.mp3 or success.wav
	- error.mp3 or error.wav
	- achievement.mp3 or achievement.wav
	- notification.mp3 or notification.wav
	"""
	if not SOUND_ENABLED or not SOUND_AVAILABLE:
		return
	
	# Try custom sound file first if enabled
	if use_custom and os.path.exists(SOUNDS_DIR):
		sound_file = None
		for ext in [".mp3", ".wav", ".ogg"]:
			path = os.path.join(SOUNDS_DIR, f"{sound_type}{ext}")
			if os.path.exists(path):
				sound_file = path
				break
		
		if sound_file:
			try:
				if USE_PYGAME:
					sound = pygame.mixer.Sound(sound_file)
					sound.play()
				elif USE_PLAYSOUND:
					playsound(sound_file, block=False)
				else:
					# Try winsound for WAV files
					if sound_file.endswith('.wav'):
						winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
					else:
						# Can't play MP3 with winsound, fall through to system sounds
						raise Exception("MP3 not supported with winsound")
				return  # Successfully played custom sound
			except Exception:
				pass  # Fall through to system sounds
	
	# Fall back to Windows system sounds
	try:
		if sound_type == "click":
			winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
		elif sound_type == "success":
			winsound.PlaySound("SystemDefault", winsound.SND_ALIAS | winsound.SND_ASYNC)
		elif sound_type == "error":
			winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
		elif sound_type == "achievement":
			winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
		elif sound_type == "notification":
			winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS | winsound.SND_ASYNC)
	except Exception:
		pass  # Silently fail if sound can't play

def wrap_command_with_sound(command, sound_type="click"):
	"""Wrap a command function to play a sound before executing."""
	def wrapped():
		play_sound(sound_type)
		command()
	return wrapped

# Game Theme Colors
GAME_COLORS = {
	"bg_primary": "#1a1a2e",      # Dark blue-black
	"bg_secondary": "#16213e",    # Darker blue
	"bg_panel": "#0f3460",         # Dark blue panel
	"accent_blue": "#00d4ff",      # Bright cyan
	"accent_green": "#00ff88",     # Bright green
	"accent_orange": "#ff6b35",    # Orange
	"accent_gold": "#ffd700",      # Gold
	"text_primary": "#ffffff",     # White
	"text_secondary": "#b0b0b0",  # Light gray
	"text_muted": "#808080",       # Gray
	"success": "#00ff88",          # Green
	"warning": "#ffaa00",          # Orange
	"error": "#ff4444",            # Red
	"button_bg": "#0f3460",        # Button background
	"button_hover": "#1a4d7a",     # Button hover
	"border": "#00d4ff",            # Border color
}

def configure_game_style():
	"""Configure ttk styles for game-like appearance."""
	style = ttk.Style()
	
	# Configure main theme
	style.theme_use('clam')
	
	# Frame styles
	style.configure('Game.TFrame', background=GAME_COLORS["bg_primary"])
	style.configure('Panel.TFrame', background=GAME_COLORS["bg_panel"], relief='flat')
	
	# LabelFrame styles
	style.configure('Game.TLabelframe', 
		background=GAME_COLORS["bg_primary"],
		foreground=GAME_COLORS["text_primary"],
		borderwidth=2,
		relief='solid')
	style.configure('Game.TLabelframe.Label',
		background=GAME_COLORS["bg_primary"],
		foreground=GAME_COLORS["accent_blue"],
		font=("Segoe UI", 10, "bold"))
	
	# Button styles
	style.configure('Game.TButton',
		background=GAME_COLORS["button_bg"],
		foreground=GAME_COLORS["text_primary"],
		borderwidth=2,
		relief='raised',
		font=("Segoe UI", 9, "bold"),
		padding=8)
	style.map('Game.TButton',
		background=[('active', GAME_COLORS["button_hover"]),
					('pressed', GAME_COLORS["bg_secondary"])],
		borderwidth=[('active', 2), ('pressed', 1)])
	
	# Label styles
	style.configure('Game.TLabel',
		background=GAME_COLORS["bg_primary"],
		foreground=GAME_COLORS["text_primary"],
		font=("Segoe UI", 9))
	style.configure('Game.Title.TLabel',
		background=GAME_COLORS["bg_primary"],
		foreground=GAME_COLORS["accent_blue"],
		font=("Segoe UI", 14, "bold"))
	style.configure('Game.Header.TLabel',
		background=GAME_COLORS["bg_primary"],
		foreground=GAME_COLORS["accent_green"],
		font=("Segoe UI", 11, "bold"))
	
	# Entry styles
	style.configure('Game.TEntry',
		fieldbackground=GAME_COLORS["bg_secondary"],
		foreground=GAME_COLORS["text_primary"],
		borderwidth=2,
		relief='solid')
	
	# Combobox styles
	style.configure('Game.TCombobox',
		fieldbackground=GAME_COLORS["bg_secondary"],
		foreground=GAME_COLORS["text_primary"],
		borderwidth=2,
		relief='solid')
	
	# Treeview styles
	style.configure('Game.Treeview',
		background=GAME_COLORS["bg_secondary"],
		foreground=GAME_COLORS["text_primary"],
		fieldbackground=GAME_COLORS["bg_secondary"],
		borderwidth=1,
		relief='solid')
	style.configure('Game.Treeview.Heading',
		background=GAME_COLORS["bg_panel"],
		foreground=GAME_COLORS["accent_blue"],
		font=("Segoe UI", 9, "bold"),
		relief='raised')
	style.map('Game.Treeview',
		background=[('selected', GAME_COLORS["accent_blue"])],
		foreground=[('selected', GAME_COLORS["bg_primary"])])


class App(tk.Tk):

	def __init__(self):
		super().__init__()
		self.title("AirCommuter - Airline Manager")
		self.geometry("1400x900")
		self.resizable(True, True)

		# Configure game theme
		configure_game_style()
		
		# Set window background
		self.configure(bg=GAME_COLORS["bg_primary"])

		container = ttk.Frame(self, style='Game.TFrame')
		container.pack(fill=tk.BOTH, expand=True)

		self.frames = {}
		for FrameClass in (
			MainMenuFrame,
			CompanySetupFrame,
			FleetManagerFrame,
			StoreFrame,
			ParkingFrame,
			FlightsFrame,
			LoansFrame,
			ReportsFrame,
			CabinConfigFrame,
			PilotsFrame,
			AirportServicesFrame,
		):
			frame = FrameClass(parent=container, controller=self)
			self.frames[FrameClass.__name__] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		container.rowconfigure(0, weight=1)
		container.columnconfigure(0, weight=1)

		self.show_frame("MainMenuFrame")

	def show_frame(self, name: str):
		frame = self.frames.get(name)
		if frame is None:
			messagebox.showerror("Navigation Error", f"Frame '{name}' not found")
			return
		
		# Auto-process daily ticks when showing main menu
		if name == "MainMenuFrame":
			try:
				from services import auto_process_daily_ticks
				auto_process_daily_ticks()
			except Exception:
				pass  # Silently fail if auto-processing has issues
		
		frame.tkraise()
		# Generate event and also explicitly call on_shown for MainMenuFrame to ensure data loads
		frame.event_generate("<<FrameShown>>", when="tail")
		# Explicitly call on_shown for MainMenuFrame to ensure data loads on initial display
		if name == "MainMenuFrame" and hasattr(frame, 'on_shown'):
			frame.on_shown()


class BaseFrame(tk.Frame):

	def __init__(self, parent, controller):
		super().__init__(parent, bg=GAME_COLORS["bg_primary"])
		self.controller = controller
		self._build_header()
		self.bind("<<FrameShown>>", self.on_shown)

	def _build_header(self):
		toolbar = tk.Frame(self, bg=GAME_COLORS["bg_panel"], height=50)
		toolbar.pack(side=tk.TOP, fill=tk.X)
		toolbar.pack_propagate(False)
		
		# Home button with game styling
		btn_home = tk.Button(toolbar, 
			text="🏠 Main Menu", 
			command=wrap_command_with_sound(lambda: self.controller.show_frame("MainMenuFrame")),
			bg=GAME_COLORS["button_bg"],
			fg=GAME_COLORS["text_primary"],
			font=("Segoe UI", 10, "bold"),
			relief='raised',
			borderwidth=2,
			padx=12,
			pady=6,
			cursor='hand2',
			activebackground=GAME_COLORS["button_hover"],
			activeforeground=GAME_COLORS["accent_blue"])
		btn_home.pack(side=tk.LEFT, padx=8, pady=8)

		self.title_var = tk.StringVar(value=self.__class__.__name__)
		lbl = tk.Label(toolbar, 
			textvariable=self.title_var, 
			font=("Segoe UI", 14, "bold"),
			bg=GAME_COLORS["bg_panel"],
			fg=GAME_COLORS["accent_blue"])
		lbl.pack(side=tk.LEFT, padx=12)

		# Decorative separator with color
		sep = tk.Frame(self, height=3, bg=GAME_COLORS["accent_blue"])
		sep.pack(fill=tk.X)

	def on_shown(self, _event=None):
		"""Called when frame is shown."""
		pass


class MainMenuFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("AirCommuter - Main Menu")

		content = tk.Frame(self, bg=GAME_COLORS["bg_primary"])
		content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

		# Top: Company name and quick status
		top_bar = tk.Frame(content, bg=GAME_COLORS["bg_panel"], relief='raised', borderwidth=2)
		top_bar.pack(fill=tk.X, pady=(0, 12))
		self.company_name_var = tk.StringVar(value="No company setup")
		tk.Label(top_bar, text="Company:", font=("Segoe UI", 10, "bold"), 
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(side=tk.LEFT, padx=12, pady=8)
		tk.Label(top_bar, textvariable=self.company_name_var, font=("Segoe UI", 12, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_green"]).pack(side=tk.LEFT, padx=8, pady=8)
		
		# Reputation display
		self.reputation_var = tk.StringVar(value="Reputation: -")
		self.reputation_label = tk.Label(top_bar, textvariable=self.reputation_var, 
			font=("Segoe UI", 10, "bold"), bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_gold"])
		self.reputation_label.pack(side=tk.RIGHT, padx=12, pady=8)

		# Main content: split into navigation (left) and financial dashboard (right)
		main_content = tk.Frame(content, bg=GAME_COLORS["bg_primary"])
		main_content.pack(fill=tk.BOTH, expand=True)

		# Left side: Navigation buttons in 3-column grid
		nav_frame = tk.LabelFrame(main_content, text="Navigation", 
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_blue"],
			font=("Segoe UI", 11, "bold"), relief='raised', borderwidth=2)
		nav_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

		buttons = [
			("✈️ Setup Company", "CompanySetupFrame"),
			("🛩️ Manage Fleet", "FleetManagerFrame"),
			("🛒 Buy Aircraft", "StoreFrame"),
			("🪑 Cabin Configuration", "CabinConfigFrame"),
			("🅿️ Parking Manager", "ParkingFrame"),
			("🛫 Airport Services", "AirportServicesFrame"),
			("✈️ Flights", "FlightsFrame"),
			("👨‍✈️ Pilots", "PilotsFrame"),
			("💰 Loans", "LoansFrame"),
			("📊 Reports", "ReportsFrame"),
		]

		grid = tk.Frame(nav_frame, bg=GAME_COLORS["bg_panel"])
		grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

		# Use 3 columns for better space usage
		cols = 3
		for idx, (label, frame_name) in enumerate(buttons):
			btn = tk.Button(grid, text=label, 
				command=wrap_command_with_sound(lambda n=frame_name: controller.show_frame(n)),
				bg=GAME_COLORS["button_bg"],
				fg=GAME_COLORS["text_primary"],
				font=("Segoe UI", 9, "bold"),
				relief='raised',
				borderwidth=2,
				padx=8,
				pady=8,
				cursor='hand2',
				activebackground=GAME_COLORS["button_hover"],
				activeforeground=GAME_COLORS["accent_blue"])
			btn.grid(row=idx // cols, column=idx % cols, padx=6, pady=6, sticky="ew")
			grid.columnconfigure(idx % cols, weight=1)

		# Right side: Financial Dashboard
		finance_frame = tk.LabelFrame(main_content, text="Financial Dashboard",
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_blue"],
			font=("Segoe UI", 11, "bold"), relief='raised', borderwidth=2)
		finance_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
		finance_frame.config(width=320)

		self._build_financial_dashboard(finance_frame)

		# Bottom: Quick actions
		actions = tk.Frame(content, bg=GAME_COLORS["bg_primary"])
		actions.pack(fill=tk.X, pady=(12, 0))
		btn_autocomplete = tk.Button(actions, text="⚡ Auto-complete due flights", 
			command=wrap_command_with_sound(self._on_autocomplete),
			bg=GAME_COLORS["button_bg"],
			fg=GAME_COLORS["text_primary"],
			font=("Segoe UI", 9, "bold"),
			relief='raised',
			borderwidth=2,
			padx=12,
			pady=8,
			cursor='hand2',
			activebackground=GAME_COLORS["button_hover"],
			activeforeground=GAME_COLORS["accent_blue"])
		btn_autocomplete.pack(side=tk.LEFT)
		btn_daily = tk.Button(actions, text="📅 Run daily tick", 
			command=wrap_command_with_sound(self._on_daily_tick),
			bg=GAME_COLORS["button_bg"],
			fg=GAME_COLORS["text_primary"],
			font=("Segoe UI", 9, "bold"),
			relief='raised',
			borderwidth=2,
			padx=12,
			pady=8,
			cursor='hand2',
			activebackground=GAME_COLORS["button_hover"],
			activeforeground=GAME_COLORS["accent_blue"])
		btn_daily.pack(side=tk.LEFT, padx=8)
		
		# Load initial data after all UI elements are created
		self.on_shown()

	def _build_financial_dashboard(self, parent):
		# Cash
		cash_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		cash_frame.pack(fill=tk.X, padx=12, pady=(12, 8))
		tk.Label(cash_frame, text="Cash Balance", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(anchor=tk.W)
		self.cash_var = tk.StringVar(value="$ 0")
		tk.Label(cash_frame, textvariable=self.cash_var, font=("Segoe UI", 16, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_green"]).pack(anchor=tk.W, pady=(2, 0))

		# Fleet stats
		fleet_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		fleet_frame.pack(fill=tk.X, padx=12, pady=8)
		tk.Label(fleet_frame, text="Fleet", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(anchor=tk.W)
		stats_row1 = tk.Frame(fleet_frame, bg=GAME_COLORS["bg_panel"])
		stats_row1.pack(fill=tk.X, pady=(2, 0))
		self.fleet_count_var = tk.StringVar(value="0 aircraft")
		tk.Label(stats_row1, textvariable=self.fleet_count_var, font=("Segoe UI", 10),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_primary"]).pack(side=tk.LEFT)
		self.active_flights_var = tk.StringVar(value="0 active")
		tk.Label(stats_row1, textvariable=self.active_flights_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_muted"]).pack(side=tk.RIGHT)

		# Loans
		loans_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		loans_frame.pack(fill=tk.X, padx=12, pady=8)
		tk.Label(loans_frame, text="Loans", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(anchor=tk.W)
		self.loans_count_var = tk.StringVar(value="0 loans")
		tk.Label(loans_frame, textvariable=self.loans_count_var, font=("Segoe UI", 10),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_primary"]).pack(anchor=tk.W, pady=(2, 0))
		self.loans_total_var = tk.StringVar(value="$0 total")
		tk.Label(loans_frame, textvariable=self.loans_total_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_muted"]).pack(anchor=tk.W)

		# Pilots
		pilots_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		pilots_frame.pack(fill=tk.X, padx=12, pady=8)
		tk.Label(pilots_frame, text="Pilots", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(anchor=tk.W)
		stats_row2 = tk.Frame(pilots_frame, bg=GAME_COLORS["bg_panel"])
		stats_row2.pack(fill=tk.X, pady=(2, 0))
		self.pilots_count_var = tk.StringVar(value="0 pilots")
		tk.Label(stats_row2, textvariable=self.pilots_count_var, font=("Segoe UI", 10),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_primary"]).pack(side=tk.LEFT)
		self.pilots_assigned_var = tk.StringVar(value="0 assigned")
		tk.Label(stats_row2, textvariable=self.pilots_assigned_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_muted"]).pack(side=tk.RIGHT)

		# Recent activity (last 30 days income/expense)
		activity_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		activity_frame.pack(fill=tk.X, padx=12, pady=8)
		tk.Label(activity_frame, text="Recent Activity (30d)", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(anchor=tk.W)
		stats_row3 = tk.Frame(activity_frame, bg=GAME_COLORS["bg_panel"])
		stats_row3.pack(fill=tk.X, pady=(2, 0))
		self.income_30d_var = tk.StringVar(value="Income: $0")
		tk.Label(stats_row3, textvariable=self.income_30d_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["success"]).pack(side=tk.LEFT)
		self.expense_30d_var = tk.StringVar(value="Expense: $0")
		tk.Label(stats_row3, textvariable=self.expense_30d_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["error"]).pack(side=tk.RIGHT)
		net_row = tk.Frame(activity_frame, bg=GAME_COLORS["bg_panel"])
		net_row.pack(fill=tk.X, pady=(2, 0))
		self.net_30d_var = tk.StringVar(value="Net: $0")
		self.net_label = tk.Label(net_row, textvariable=self.net_30d_var, font=("Segoe UI", 11, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_gold"])
		self.net_label.pack(anchor=tk.W)

		# Market conditions
		market_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		market_frame.pack(fill=tk.X, padx=12, pady=8)
		tk.Label(market_frame, text="Market Conditions", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_secondary"]).pack(anchor=tk.W)
		self.seasonal_var = tk.StringVar(value="Season: -")
		tk.Label(market_frame, textvariable=self.seasonal_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_primary"]).pack(anchor=tk.W, pady=(2, 0))
		self.fuel_price_var = tk.StringVar(value="Fuel: -")
		tk.Label(market_frame, textvariable=self.fuel_price_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_primary"]).pack(anchor=tk.W)

		# Achievements
		achievements_frame = tk.Frame(parent, bg=GAME_COLORS["bg_panel"])
		achievements_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		tk.Label(achievements_frame, text="🏆 Achievements", font=("Segoe UI", 10, "bold"),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["accent_gold"]).pack(anchor=tk.W)
		self.achievements_var = tk.StringVar(value="0 earned")
		tk.Label(achievements_frame, textvariable=self.achievements_var, font=("Segoe UI", 9),
			bg=GAME_COLORS["bg_panel"], fg=GAME_COLORS["text_primary"]).pack(anchor=tk.W, pady=(2, 0))
		
		# Scrollable list for achievements
		achievements_list_frame = tk.Frame(achievements_frame, bg=GAME_COLORS["bg_panel"])
		achievements_list_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
		
		# Create scrollable text widget
		self.achievements_text = scrolledtext.ScrolledText(achievements_list_frame, 
			height=6, width=30, wrap=tk.WORD, bg=GAME_COLORS["bg_secondary"],
			fg=GAME_COLORS["text_primary"], font=("Segoe UI", 8),
			relief=tk.FLAT, borderwidth=1, state=tk.DISABLED)
		self.achievements_text.pack(fill=tk.BOTH, expand=True)

	def on_shown(self, _event=None):
		# Lazy import to avoid circular imports once we add storage
		try:
			import time
			from storage import load_state
			from services import list_loans, list_active_flights, get_company_reputation
			state = load_state()
			company = state.get("company") or {}
			name = company.get("name") or "No company setup"
			cash = state.get("cash", 0)
			fleet = state.get("fleet", [])
			
			# Company name and cash
			self.company_name_var.set(name)
			self.cash_var.set(f"$ {cash:,.0f}")
			
			# Reputation
			reputation = get_company_reputation()
			rep_color = "#0a7f2e" if reputation >= 60 else "#ff9800" if reputation >= 40 else "#b00020"
			self.reputation_var.set(f"Reputation: {reputation:.1f}/100")
			self.reputation_label.config(foreground=rep_color)
			
			# Fleet stats
			self.fleet_count_var.set(f"{len(fleet)} aircraft")
			active_flights = list_active_flights()
			self.active_flights_var.set(f"{len(active_flights)} active flights")
			
			# Loans
			loans = list_loans()
			self.loans_count_var.set(f"{len(loans)} loans")
			loans_total = sum(int(l.get("remaining_balance", 0)) for l in loans)
			self.loans_total_var.set(f"${loans_total:,} total balance")
			
			# Pilots
			pilots = state.get("pilots", [])
			self.pilots_count_var.set(f"{len(pilots)} pilots")
			assigned = sum(1 for p in pilots if p.get("assigned_aircraft_id"))
			self.pilots_assigned_var.set(f"{assigned} assigned")
			
			# Recent activity (30 days)
			ledger = state.get("ledger", [])
			now = int(time.time())
			thirty_days_ago = now - (30 * 86400)
			recent = [e for e in ledger if int(e.get("ts", 0)) >= thirty_days_ago]
			income = sum(int(e.get("amount", 0)) for e in recent if int(e.get("amount", 0)) > 0)
			expense = sum(abs(int(e.get("amount", 0))) for e in recent if int(e.get("amount", 0)) < 0)
			net = income - expense
			self.income_30d_var.set(f"Income: ${income:,}")
			self.expense_30d_var.set(f"Expense: ${expense:,}")
			
			# Market conditions
			from services import get_seasonal_demand_multiplier, get_fuel_price_multiplier
			seasonal_mult = get_seasonal_demand_multiplier()
			import datetime
			month = datetime.datetime.now().month
			season_names = {12: "Holiday", 1: "Holiday", 6: "Summer", 7: "Summer", 8: "Summer", 2: "Low", 3: "Normal", 4: "Normal", 5: "Normal", 9: "Normal", 10: "Normal", 11: "Normal"}
			season_name = season_names.get(month, "Normal")
			season_icon = "📈" if seasonal_mult > 1.0 else "📉" if seasonal_mult < 1.0 else "➡"
			self.seasonal_var.set(f"{season_icon} Season: {season_name} ({seasonal_mult:.1f}x demand)")
			
			fuel_mult = get_fuel_price_multiplier()
			fuel_icon = "⬆" if fuel_mult > 1.0 else "⬇" if fuel_mult < 1.0 else "➡"
			self.fuel_price_var.set(f"{fuel_icon} Fuel: {fuel_mult:.2f}x")
			
			# Achievements
			achievements = state.get("achievements", [])
			self.achievements_var.set(f"🏆 {len(achievements)} earned")
			
			# Get achievement definitions from services (ensures they match what's awarded)
			from services import get_achievement_definitions
			all_achievements = get_achievement_definitions()
			achievement_definitions = {ach["id"]: {"name": ach["name"], "desc": ach["desc"]} for ach in all_achievements}
			
			# Update achievements display
			self.achievements_text.config(state=tk.NORMAL)
			self.achievements_text.delete(1.0, tk.END)
			
			if achievements:
				for ach_id in achievements:
					ach_info = achievement_definitions.get(ach_id, {"name": ach_id, "desc": ""})
					ach_name = ach_info.get("name", ach_id)
					ach_desc = ach_info.get("desc", "")
					self.achievements_text.insert(tk.END, f"🏆 {ach_name}\n", "achievement_name")
					if ach_desc:
						self.achievements_text.insert(tk.END, f"   {ach_desc}\n\n", "achievement_desc")
			else:
				self.achievements_text.insert(tk.END, "No achievements earned yet.\n", "no_achievements")
			
			# Configure text tags for styling
			self.achievements_text.tag_config("achievement_name", 
				foreground=GAME_COLORS["accent_gold"], font=("Segoe UI", 9, "bold"))
			self.achievements_text.tag_config("achievement_desc", 
				foreground=GAME_COLORS["text_muted"], font=("Segoe UI", 8))
			self.achievements_text.tag_config("no_achievements", 
				foreground=GAME_COLORS["text_muted"], font=("Segoe UI", 8, "italic"))
			
			self.achievements_text.config(state=tk.DISABLED)
			net_color = "#0a7f2e" if net >= 0 else "#b00020"
			self.net_30d_var.set(f"Net: ${net:,}")
			self.net_label.config(foreground=net_color)
		except Exception:
			pass

	def _on_autocomplete(self):
		try:
			from services import auto_complete_due_flights
			count = auto_complete_due_flights()
			messagebox.showinfo("Flights", f"Auto-completed {count} flights.")
		except Exception as exc:
			messagebox.showerror("Flights", str(exc))

	def _on_daily_tick(self):
		try:
			from services import run_daily_tick, run_pilot_daily_tick
			parking_count = run_daily_tick()
			pilot_summary = run_pilot_daily_tick()
			
			msg = f"Parking fees: {parking_count} applied\n"
			msg += f"Pilot revenue: ${pilot_summary.get('revenue', 0):,}\n"
			msg += f"Pilot salaries: ${pilot_summary.get('salary_costs', 0):,}\n"
			msg += f"Net pilot income: ${pilot_summary.get('revenue', 0) - pilot_summary.get('salary_costs', 0):,}\n"
			if pilot_summary.get('snags_found', 0) > 0:
				msg += f"Snags found: {pilot_summary.get('snags_found', 0)}\n"
			if pilot_summary.get('damage_events', 0) > 0:
				msg += f"Aircraft grounded: {pilot_summary.get('damage_events', 0)}"
			messagebox.showinfo("Daily Tick", msg)
		except Exception as exc:
			messagebox.showerror("Daily Tick", str(exc))


class CompanySetupFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Setup Company")

		form = ttk.Frame(self)
		form.pack(padx=16, pady=16)

		self.name_var = tk.StringVar()
		self.cash_var = tk.StringVar(value="5000000")

		self._add_row(form, "Company Name", self.name_var)
		self._add_row(form, "Starting Cash", self.cash_var)

		btns = ttk.Frame(form)
		btns.pack(pady=12, fill=tk.X)
		btn_save = ttk.Button(btns, text="Save", command=wrap_command_with_sound(self.save_company))
		btn_save.pack(side=tk.LEFT)

	def _add_row(self, parent, label, var):
		row = ttk.Frame(parent)
		row.pack(fill=tk.X, pady=6)
		ttk.Label(row, text=label, width=18).pack(side=tk.LEFT)
		entry = ttk.Entry(row, textvariable=var, width=40)
		entry.pack(side=tk.LEFT)

	def save_company(self):
		name = self.name_var.get().strip()
		if not name:
			messagebox.showwarning("Validation", "Please enter a company name.")
			return
		try:
			start_cash = float(self.cash_var.get().replace(",", "").strip())
		except ValueError:
			messagebox.showerror("Validation", "Starting Cash must be a number.")
			return
		try:
			from storage import load_state, save_state
			state = load_state()
			state["company"] = {"name": name}
			state["cash"] = max(0, round(start_cash))
			state["ledger"] = []
			state["fleet"] = []
			state["loans"] = []
			state["bookings"] = []
			state["parking"] = {}
			state["active_flights"] = []
			state["aircraft_config"] = {}
			state["pilots"] = []
			save_state(state)
			messagebox.showinfo("Saved", "Company saved.")
			self.controller.show_frame("MainMenuFrame")
		except Exception as exc:
			messagebox.showerror("Error", f"Failed to save company: {exc}")


class FleetManagerFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Fleet Manager")

		toolbar = tk.Frame(self, bg=GAME_COLORS["bg_primary"])
		toolbar.pack(fill=tk.X, padx=12, pady=8)
		
		def create_game_button(parent, text, command):
			return tk.Button(parent, text=text, command=wrap_command_with_sound(command),
				bg=GAME_COLORS["button_bg"],
				fg=GAME_COLORS["text_primary"],
				font=("Segoe UI", 9, "bold"),
				relief='raised',
				borderwidth=2,
				padx=12,
				pady=6,
				cursor='hand2',
				activebackground=GAME_COLORS["button_hover"],
				activeforeground=GAME_COLORS["accent_blue"])
		
		btn_refresh = create_game_button(toolbar, "🔄 Refresh", self.refresh)
		btn_refresh.pack(side=tk.LEFT)
		btn_maint = create_game_button(toolbar, "🔧 Perform Maintenance", self._on_maint)
		btn_maint.pack(side=tk.LEFT, padx=8)
		btn_oil = create_game_button(toolbar, "🛢️ Check Oil", self._on_refill_oil)
		btn_oil.pack(side=tk.LEFT, padx=8)
		btn_oil_change = create_game_button(toolbar, "🔄 Full Oil Change", self._on_change_oil)
		btn_oil_change.pack(side=tk.LEFT, padx=8)
		btn_change = create_game_button(toolbar, "✏️ Change ID", self._on_change_id)
		btn_change.pack(side=tk.LEFT, padx=8)
		btn_weight = create_game_button(toolbar, "⚖️ Configure Weight Limits", self._on_configure_weight)
		btn_weight.pack(side=tk.LEFT, padx=8)

		cols = ("id", "type", "name", "hrs", "a_check", "b_check", "c_check", "loc", "price")
		self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20, style='Game.Treeview')
		for c, h in zip(cols, ["ID", "Type", "Name", "Hours", "A Check", "B Check", "C Check", "Location", "Price"]):
			self.tree.heading(c, text=h)
			self.tree.column(c, width=100 if c in ("a_check", "b_check", "c_check") else 120, anchor=tk.W)
		# Configure tags for color coding
		self.tree.tag_configure("overdue", foreground=GAME_COLORS["error"])
		self.tree.tag_configure("due", foreground=GAME_COLORS["warning"])
		self.tree.tag_configure("ok", foreground=GAME_COLORS["success"])
		self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		self.tree.delete(*self.tree.get_children())
		try:
			from services import list_fleet, get_maintenance_status, MAINTENANCE_INTERVALS
			for ac in list_fleet():
				ac_id = ac.get("id")
				maint_status = get_maintenance_status(ac_id)
				
				# Format maintenance status for each check
				def format_check_status(check_type):
					if check_type not in maint_status:
						return "N/A"
					check = maint_status[check_type]
					hours = check["hours"]
					interval = check["interval"]
					if check["overdue"]:
						return f"{hours:.0f}/{interval:.0f} ⚠"
					elif check["due"]:
						return f"{hours:.0f}/{interval:.0f} !"
					else:
						return f"{hours:.0f}/{interval:.0f}"
				
				# Determine tag color based on worst status
				tag = "ok"
				if any(maint_status.get(k, {}).get("overdue", False) for k in ["a_check", "b_check", "c_check"]):
					tag = "overdue"
				elif any(maint_status.get(k, {}).get("due", False) for k in ["a_check", "b_check", "c_check"]):
					tag = "due"
				
				vals = (
					ac.get("id"), ac.get("type_code"), ac.get("name"),
					f"{ac.get('hours_since_maintenance', 0):.1f}",
					format_check_status("a_check"),
					format_check_status("b_check"),
					format_check_status("c_check"),
					ac.get("location", ""),
					f"$ {ac.get('purchase_price', 0):,}",
				)
				self.tree.insert("", tk.END, values=vals, tags=(tag,))
		except Exception:
			pass

	def _get_selected_aircraft_id(self):
		item = self.tree.focus()
		if not item:
			return None
		vals = self.tree.item(item, "values")
		return vals[0] if vals else None

	def _on_maint(self):
		ac_id = self._get_selected_aircraft_id()
		if not ac_id:
			messagebox.showinfo("Maintenance", "Select an aircraft first.")
			return
		try:
			from services import perform_maintenance
			perform_maintenance(ac_id)
			messagebox.showinfo("Maintenance", "Maintenance completed.")
			self.refresh()
		except Exception as exc:
			messagebox.showerror("Maintenance", str(exc))
	
	def _on_refill_oil(self):
		ac_id = self._get_selected_aircraft_id()
		if not ac_id:
			messagebox.showinfo("Check Oil", "Select an aircraft first.")
			return
		try:
			from services import list_fleet, refill_aircraft_oil, walkaround_check
			fleet = list_fleet()
			aircraft = next((ac for ac in fleet if ac.get("id") == ac_id), None)
			if not aircraft:
				messagebox.showerror("Check Oil", "Aircraft not found.")
				return
			
			# Check if aircraft tracks oil
			if "oil_level" not in aircraft or "oil_capacity" not in aircraft:
				messagebox.showinfo("Check Oil", "This aircraft type does not require manual oil checks (airliners manage oil automatically).")
				return
			
			# Get current oil status
			walkaround = walkaround_check(ac_id)
			oil_level = walkaround.get("oil_level", 0.0)
			oil_capacity = walkaround.get("oil_capacity", 32.0)
			oil_minimum = walkaround.get("oil_minimum", 12.0)
			oil_percent = (oil_level / oil_capacity * 100) if oil_capacity > 0 else 0
			
			# Show oil level in popup
			status_msg = f"Oil Level: {oil_level:.1f} / {oil_capacity:.1f} quarts ({oil_percent:.0f}%)\n"
			status_msg += f"Minimum: {oil_minimum:.1f} quarts\n\n"
			
			if oil_level < oil_minimum:
				status_msg += "⚠️ CRITICAL: Oil below minimum!"
			elif oil_percent < 50:
				status_msg += "⚠️ Oil level is low"
			else:
				status_msg += "✓ Oil level is good"
			
			# Ask if they want to add oil
			if oil_level < oil_capacity:
				if messagebox.askyesno("Check Oil", status_msg + "\n\nWould you like to add oil?"):
					try:
						refill_aircraft_oil(ac_id)
						messagebox.showinfo("Oil Top-Up", "Oil topped up successfully!")
						self.refresh()
					except Exception as exc:
						messagebox.showerror("Oil Top-Up", str(exc))
			else:
				messagebox.showinfo("Check Oil", status_msg)
		except Exception as exc:
			messagebox.showerror("Check Oil", str(exc))
	
	def _on_change_oil(self):
		ac_id = self._get_selected_aircraft_id()
		if not ac_id:
			messagebox.showinfo("Oil Change", "Select an aircraft first.")
			return
		try:
			# Check if aircraft needs oil (smaller planes only)
			from services import list_fleet, change_aircraft_oil
			fleet = list_fleet()
			aircraft = next((ac for ac in fleet if ac.get("id") == ac_id), None)
			if not aircraft:
				messagebox.showerror("Oil Change", "Aircraft not found.")
				return
			
			# Check if aircraft tracks oil
			if "oil_level" not in aircraft or "oil_capacity" not in aircraft:
				messagebox.showinfo("Oil Change", "This aircraft type does not require manual oil changes (airliners manage oil automatically).")
				return
			
			# Confirm oil change
			hours_since = aircraft.get("hours_since_oil_change", 0.0)
			confirm = messagebox.askyesno("Full Oil Change", 
				f"Perform full oil change on {ac_id}?\n\n"
				f"Hours since last change: {hours_since:.1f}h\n"
				f"Recommended interval: 50 hours\n\n"
				f"This will cost ${aircraft.get('oil_capacity', 32.0) * 100:.0f} (more expensive than top-up).")
			if confirm:
				change_aircraft_oil(ac_id)
				messagebox.showinfo("Oil Change", "Full oil change completed successfully!")
				self.refresh()
		except Exception as exc:
			messagebox.showerror("Oil Change", str(exc))
	
	def _on_change_id(self):
		ac_id = self._get_selected_aircraft_id()
		if not ac_id:
			messagebox.showinfo("Fleet", "Select an aircraft first.")
			return
		new_id = simpledialog.askstring("Change Aircraft ID", f"Enter new ID for {ac_id}:\n\nNote: Administrative fee of $5,000 will be charged.")
		if new_id is None:
			return
		new_id = new_id.strip()
		if not new_id:
			messagebox.showwarning("Fleet", "ID cannot be empty.")
			return
		try:
			from services import change_aircraft_id
			change_aircraft_id(ac_id, new_id)
			self.refresh()
			messagebox.showinfo("Fleet", f"Aircraft ID updated. $5,000 administrative fee charged.")
		except Exception as exc:
			messagebox.showerror("Fleet", str(exc))
	
	def _on_configure_weight(self):
		"""Configure weight limits for selected aircraft."""
		ac_id = self._get_selected_aircraft_id()
		if not ac_id:
			messagebox.showinfo("Fleet", "Select an aircraft first.")
			return
		
		try:
			from services import get_aircraft_weight_limits, set_aircraft_weight_limits, list_fleet
			
			# Get current values
			limits = get_aircraft_weight_limits(ac_id)
			fleet = list_fleet()
			aircraft = next((ac for ac in fleet if ac.get("id") == ac_id), None)
			if not aircraft:
				messagebox.showerror("Fleet", "Aircraft not found.")
				return
			
			# Create dialog
			dialog = tk.Toplevel(self)
			dialog.title(f"Configure Weight Limits - {ac_id}")
			dialog.geometry("600x500")
			dialog.transient(self)
			dialog.grab_set()
			
			# Center the dialog
			dialog.update_idletasks()
			x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
			y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
			dialog.geometry(f"+{x}+{y}")
			
			# Title
			title_frame = ttk.Frame(dialog)
			title_frame.pack(padx=20, pady=(20, 10))
			ttk.Label(title_frame, text="Aircraft Weight Limits Configuration", font=("Segoe UI", 12, "bold")).pack()
			ttk.Label(title_frame, text=f"Aircraft: {ac_id} ({aircraft.get('name', 'N/A')})", 
				font=("Segoe UI", 9), foreground="#666").pack(pady=(4, 0))
			
			# Info text
			info_frame = ttk.Frame(dialog)
			info_frame.pack(fill=tk.X, padx=20, pady=10)
			info_text = "Enter weight limits in pounds (lbs).\n" \
				"Zero Fuel Weight = Empty Weight + Passenger Weight + Cargo Weight\n" \
				"Zero Fuel Weight must not exceed Max Zero Fuel Weight."
			ttk.Label(info_frame, text=info_text, font=("Segoe UI", 8), 
				foreground="#666", justify=tk.LEFT, wraplength=450).pack()
			
			main_frame = ttk.Frame(dialog)
			main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
			
			# Empty Weight
			empty_frame = ttk.Frame(main_frame)
			empty_frame.pack(fill=tk.X, pady=8)
			ttk.Label(empty_frame, text="Empty Weight (lbs):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
			empty_var = tk.StringVar(value=str(limits.get("empty_weight", "") or ""))
			empty_entry = ttk.Entry(empty_frame, textvariable=empty_var, width=20)
			empty_entry.pack(side=tk.LEFT)
			ttk.Label(empty_frame, text="(Aircraft weight without fuel, passengers, or cargo)", 
				font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=(8, 0))
			
			# Max Zero Fuel Weight
			zfw_frame = ttk.Frame(main_frame)
			zfw_frame.pack(fill=tk.X, pady=8)
			ttk.Label(zfw_frame, text="Max Zero Fuel Weight (lbs):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
			zfw_var = tk.StringVar(value=str(limits.get("max_zero_fuel_weight", "") or ""))
			zfw_entry = ttk.Entry(zfw_frame, textvariable=zfw_var, width=20)
			zfw_entry.pack(side=tk.LEFT)
			ttk.Label(zfw_frame, text="(Maximum weight without fuel)", 
				font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=(8, 0))
			
			# Max Takeoff Weight
			mtow_frame = ttk.Frame(main_frame)
			mtow_frame.pack(fill=tk.X, pady=8)
			ttk.Label(mtow_frame, text="Max Takeoff Weight (lbs):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
			mtow_var = tk.StringVar(value=str(limits.get("max_takeoff_weight", "") or ""))
			mtow_entry = ttk.Entry(mtow_frame, textvariable=mtow_var, width=20)
			mtow_entry.pack(side=tk.LEFT)
			ttk.Label(mtow_frame, text="(Maximum weight at takeoff)", 
				font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=(8, 0))
			
			# Buttons
			btn_frame = ttk.Frame(dialog)
			btn_frame.pack(padx=20, pady=(10, 20))
			
			def save():
				try:
					empty_val = empty_var.get().strip()
					zfw_val = zfw_var.get().strip()
					mtow_val = mtow_var.get().strip()
					
					empty_weight = float(empty_val) if empty_val else None
					max_zfw = float(zfw_val) if zfw_val else None
					max_mtow = float(mtow_val) if mtow_val else None
					
					# Validate
					if empty_weight is not None and empty_weight <= 0:
						messagebox.showerror("Error", "Empty weight must be greater than 0.")
						return
					if max_zfw is not None and max_zfw <= 0:
						messagebox.showerror("Error", "Max Zero Fuel Weight must be greater than 0.")
						return
					if max_mtow is not None and max_mtow <= 0:
						messagebox.showerror("Error", "Max Takeoff Weight must be greater than 0.")
						return
					if empty_weight is not None and max_zfw is not None and empty_weight >= max_zfw:
						messagebox.showerror("Error", "Empty Weight must be less than Max Zero Fuel Weight.")
						return
					if max_zfw is not None and max_mtow is not None and max_zfw > max_mtow:
						messagebox.showerror("Error", "Max Zero Fuel Weight must not exceed Max Takeoff Weight.")
						return
					
					set_aircraft_weight_limits(ac_id, empty_weight, max_zfw, max_mtow)
					messagebox.showinfo("Success", "Weight limits configured successfully.")
					dialog.destroy()
				except ValueError:
					messagebox.showerror("Error", "Please enter valid numbers for all fields.")
				except Exception as exc:
					messagebox.showerror("Error", str(exc))
			
			ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
			ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
			
			dialog.wait_window()
			
		except Exception as exc:
			messagebox.showerror("Fleet", str(exc))


class StoreFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Aircraft Store")
		
		# Create notebook for tabs
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		
		# Tab 1: New Aircraft (from catalog)
		self.new_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.new_frame, text="New Aircraft")
		self._build_new_aircraft_tab()
		
		# Tab 2: Marketplace (used aircraft)
		self.marketplace_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.marketplace_frame, text="Marketplace")
		self._build_marketplace_tab()
		
		# Tab 3: Leasing
		self.lease_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.lease_frame, text="Leasing")
		self._build_leasing_tab()
		
		self.bind("<<FrameShown>>", lambda e: self.refresh())
	
	def _build_new_aircraft_tab(self):
		toolbar = ttk.Frame(self.new_frame)
		toolbar.pack(fill=tk.X, padx=12, pady=8)
		btn_buy = ttk.Button(toolbar, text="Buy Selected", command=wrap_command_with_sound(self._on_buy_new))
		btn_buy.pack(side=tk.LEFT)
		btn_edit_duration = ttk.Button(toolbar, text="Edit Max Duration", command=wrap_command_with_sound(self._on_edit_duration))
		btn_edit_duration.pack(side=tk.LEFT, padx=8)
		btn_refresh = ttk.Button(toolbar, text="Refresh", command=wrap_command_with_sound(self.refresh))
		btn_refresh.pack(side=tk.LEFT, padx=8)
		
		cols = ("type", "name", "price", "max_duration")
		self.new_tree = ttk.Treeview(self.new_frame, columns=cols, show="headings", height=20)
		for c, h in zip(cols, ["Type", "Name", "Price", "Max Duration"]):
			self.new_tree.heading(c, text=h)
			self.new_tree.column(c, width=160 if c != "name" else 200, anchor=tk.W)
		self.new_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
		self.new_tree.bind("<Double-1>", lambda e: self._on_aircraft_double_click("new"))
	
	def _build_marketplace_tab(self):
		toolbar = ttk.Frame(self.marketplace_frame)
		toolbar.pack(fill=tk.X, padx=12, pady=8)
		btn_buy = ttk.Button(toolbar, text="Buy Selected", command=wrap_command_with_sound(self._on_buy_marketplace))
		btn_buy.pack(side=tk.LEFT)
		btn_refresh = ttk.Button(toolbar, text="Refresh", command=wrap_command_with_sound(self.refresh))
		btn_refresh.pack(side=tk.LEFT, padx=8)
		ttk.Label(toolbar, text="Marketplace listings refresh daily", font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=12)
		
		cols = ("type", "name", "condition", "hours", "reliability", "price", "description")
		self.marketplace_tree = ttk.Treeview(self.marketplace_frame, columns=cols, show="headings", height=20)
		for c, h in zip(cols, ["Type", "Name", "Condition", "Hours", "Reliability", "Price", "Description"]):
			self.marketplace_tree.heading(c, text=h)
			if c == "description":
				self.marketplace_tree.column(c, width=300, anchor=tk.W)
			else:
				self.marketplace_tree.column(c, width=100, anchor=tk.W)
		self.marketplace_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
		self.marketplace_tree.bind("<Double-1>", lambda e: self._on_aircraft_double_click("marketplace"))
	
	def _build_leasing_tab(self):
		toolbar = ttk.Frame(self.lease_frame)
		toolbar.pack(fill=tk.X, padx=12, pady=8)
		btn_lease = ttk.Button(toolbar, text="Lease Selected", command=wrap_command_with_sound(self._on_lease))
		btn_lease.pack(side=tk.LEFT)
		btn_refresh = ttk.Button(toolbar, text="Refresh", command=wrap_command_with_sound(self.refresh))
		btn_refresh.pack(side=tk.LEFT, padx=8)
		
		cols = ("type", "name", "monthly_payment", "term_months", "description")
		self.lease_tree = ttk.Treeview(self.lease_frame, columns=cols, show="headings", height=20)
		for c, h in zip(cols, ["Type", "Name", "Monthly Payment", "Term (months)", "Description"]):
			self.lease_tree.heading(c, text=h)
			if c == "description":
				self.lease_tree.column(c, width=250, anchor=tk.W)
			else:
				self.lease_tree.column(c, width=120, anchor=tk.W)
		self.lease_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
		self.lease_tree.bind("<Double-1>", lambda e: self._on_aircraft_double_click("lease"))

	def refresh(self):
		# Refresh new aircraft tab
		self.new_tree.delete(*self.new_tree.get_children())
		try:
			from catalog import aircraft_catalog
			from services import get_aircraft_max_duration
			for item in aircraft_catalog():
				max_dur = get_aircraft_max_duration(item["type_code"])
				vals = (item["type_code"], item["name"], f"$ {item['price']:,}", f"{max_dur:.1f}h")
				self.new_tree.insert("", tk.END, values=vals)
		except Exception:
			pass
		
		# Refresh marketplace tab
		self.marketplace_tree.delete(*self.marketplace_tree.get_children())
		try:
			from services import get_marketplace_listings
			listings = get_marketplace_listings()
			for listing in listings:
				condition = listing.get("condition", "unknown").replace("_", " ").title()
				hours = listing.get("total_hours", 0.0)
				reliability = listing.get("reliability", 1.0)
				price = listing.get("price", 0)
				desc = listing.get("description", "")
				
				vals = (
					listing.get("type_code", ""),
					listing.get("name", ""),
					condition,
					f"{hours:.0f}h",
					f"{reliability:.2f}",
					f"$ {price:,}",
					desc[:80] + "..." if len(desc) > 80 else desc
				)
				# Color code based on condition
				tag = "new" if condition == "New" else "vintage" if condition == "Vintage" else "used"
				self.marketplace_tree.insert("", tk.END, values=vals, tags=(tag,))
			
			# Configure tags
			self.marketplace_tree.tag_configure("new", foreground="#0a7f2e")
			self.marketplace_tree.tag_configure("vintage", foreground="#b00020")
			self.marketplace_tree.tag_configure("used", foreground="#666")
		except Exception as exc:
			import traceback
			traceback.print_exc()
		
		# Refresh leasing tab
		self.lease_tree.delete(*self.lease_tree.get_children())
		try:
			from services import get_lease_options
			options = get_lease_options()
			for option in options:
				vals = (
					option.get("type_code", ""),
					option.get("name", ""),
					f"$ {option.get('monthly_payment', 0):,}",
					str(option.get("term_months", 0)),
					option.get("description", "")
				)
				self.lease_tree.insert("", tk.END, values=vals)
		except Exception as exc:
			import traceback
			traceback.print_exc()

	def _on_buy_new(self):
		item = self.new_tree.focus()
		if not item:
			messagebox.showinfo("Store", "Select an aircraft to buy.")
			return
		vals = self.new_tree.item(item, "values")
		try:
			from catalog import aircraft_catalog
			from services import buy_aircraft
			catalog_map = {c["type_code"]: c for c in aircraft_catalog()}
			code = vals[0]
			entry = catalog_map.get(code)
			if not entry:
				messagebox.showerror("Store", "Catalog entry not found.")
				return
			buy_aircraft(entry["type_code"], entry["name"], entry["price"])
			messagebox.showinfo("Store", f"Purchased {entry['name']}.")
			self.refresh()
		except Exception as exc:
			messagebox.showerror("Store", str(exc))
	
	def _on_buy_marketplace(self):
		item = self.marketplace_tree.focus()
		if not item:
			messagebox.showinfo("Store", "Select an aircraft from marketplace to buy.")
			return
		
		# Get the listing data
		vals = self.marketplace_tree.item(item, "values")
		try:
			from services import get_marketplace_listings, buy_aircraft
			listings = get_marketplace_listings()
			
			# Find matching listing
			type_code = vals[0]
			name = vals[1]
			price_str = vals[5].replace("$", "").replace(",", "").strip()
			
			listing = None
			for l in listings:
				if l.get("type_code") == type_code and l.get("name") == name and str(l.get("price")) == price_str:
					listing = l
					break
			
			if not listing:
				messagebox.showerror("Store", "Listing not found.")
				return
			
			# Confirm purchase
			condition = listing.get("condition", "unknown")
			hours = listing.get("total_hours", 0.0)
			reliability = listing.get("reliability", 1.0)
			price = listing.get("price", 0)
			desc = listing.get("description", "")
			
			confirm_msg = f"Buy {name} ({type_code})?\n\n"
			confirm_msg += f"Condition: {condition.replace('_', ' ').title()}\n"
			confirm_msg += f"Total Hours: {hours:.0f}\n"
			confirm_msg += f"Reliability: {reliability:.2f}\n"
			confirm_msg += f"Price: ${price:,}\n\n"
			confirm_msg += f"{desc}\n\n"
			confirm_msg += "Proceed with purchase?"
			
			if not messagebox.askyesno("Confirm Purchase", confirm_msg):
				return
			
			# Buy with marketplace data
			buy_aircraft(
				listing["type_code"],
				listing["name"],
				listing["price"],
				listing_id=listing.get("listing_id"),
				total_hours=listing.get("total_hours", 0.0),
				initial_reliability=listing.get("reliability", 1.0),
				initial_maintenance_hours={
					"hours_since_a_check": listing.get("hours_since_a_check", 0.0),
					"hours_since_b_check": listing.get("hours_since_b_check", 0.0),
					"hours_since_c_check": listing.get("hours_since_c_check", 0.0),
				}
			)
			messagebox.showinfo("Store", f"Purchased {name} from marketplace.")
			self.refresh()
		except Exception as exc:
			import traceback
			traceback.print_exc()
			messagebox.showerror("Store", str(exc))
	
	def _on_lease(self):
		item = self.lease_tree.focus()
		if not item:
			messagebox.showinfo("Store", "Select a lease option.")
			return
		
		vals = self.lease_tree.item(item, "values")
		try:
			from services import get_lease_options, lease_aircraft
			options = get_lease_options()
			
			# Find matching option
			type_code = vals[0]
			name = vals[1]
			monthly_payment_str = vals[2].replace("$", "").replace(",", "").strip()
			
			option = None
			for o in options:
				if o.get("type_code") == type_code and o.get("name") == name and str(o.get("monthly_payment")) == monthly_payment_str:
					option = o
					break
			
			if not option:
				messagebox.showerror("Store", "Lease option not found.")
				return
			
			# Confirm lease
			monthly_payment = option.get("monthly_payment", 0)
			term_months = option.get("term_months", 0)
			total_cost = monthly_payment * term_months
			
			confirm_msg = f"Lease {name} ({type_code})?\n\n"
			confirm_msg += f"Monthly Payment: ${monthly_payment:,}\n"
			confirm_msg += f"Term: {term_months} months\n"
			confirm_msg += f"Total Cost: ${total_cost:,}\n\n"
			confirm_msg += "First month payment due now. Proceed?"
			
			if not messagebox.askyesno("Confirm Lease", confirm_msg):
				return
			
			lease_aircraft(
				option["type_code"],
				option["name"],
				option["monthly_payment"],
				option["term_months"]
			)
			messagebox.showinfo("Store", f"Leased {name}. First month payment processed.")
			self.refresh()
		except Exception as exc:
			import traceback
			traceback.print_exc()
			messagebox.showerror("Store", str(exc))
	
	def _on_aircraft_double_click(self, tab: str):
		"""Show aircraft details dialog when double-clicking on an aircraft."""
		if tab == "new":
			tree = self.new_tree
		elif tab == "marketplace":
			tree = self.marketplace_tree
		elif tab == "lease":
			tree = self.lease_tree
		else:
			return
		
		item = tree.focus()
		if not item:
			return
		
		vals = tree.item(item, "values")
		type_code = vals[0]
		
		try:
			from catalog import aircraft_catalog
			from services import get_aircraft_max_duration
			from seat_types import get_default_layout, calculate_cabin_total_seats, calculate_cabin_comfort, get_seat_types
			
			catalog = aircraft_catalog()
			aircraft_info = next((a for a in catalog if a.get("type_code") == type_code), None)
			
			if not aircraft_info:
				messagebox.showerror("Aircraft Details", "Aircraft information not found.")
				return
			
			# Create details dialog
			dialog = tk.Toplevel(self)
			dialog.title(f"Aircraft Details - {aircraft_info.get('name', 'Unknown')}")
			dialog.geometry("850x750")
			dialog.transient(self)
			dialog.grab_set()
			
			# Center the dialog
			dialog.update_idletasks()
			x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
			y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
			dialog.geometry(f"+{x}+{y}")
			
			# Title
			title_frame = ttk.Frame(dialog)
			title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
			ttk.Label(title_frame, text=aircraft_info.get("name", "Unknown"), font=("Segoe UI", 14, "bold")).pack()
			ttk.Label(title_frame, text=f"Type Code: {type_code}", font=("Segoe UI", 10), foreground="#666").pack()
			
			# Stats section
			stats_frame = ttk.LabelFrame(dialog, text="Aircraft Specifications")
			stats_frame.pack(fill=tk.X, padx=20, pady=10)
			
			# Create two columns for stats
			left_col = ttk.Frame(stats_frame)
			left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
			right_col = ttk.Frame(stats_frame)
			right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
			
			price = aircraft_info.get("price", 0)
			capacity = aircraft_info.get("capacity", 0)
			range_nm = aircraft_info.get("range_nm", 0)
			hourly_cost = aircraft_info.get("hourly_cost", 0)
			max_duration = get_aircraft_max_duration(type_code)
			max_seats_per_row = aircraft_info.get("max_seats_per_row", 6)
			max_rows = aircraft_info.get("max_rows", 40)
			oil_capacity = aircraft_info.get("oil_capacity")
			
			stats = [
				("Price", f"${price:,}"),
				("Capacity", f"{capacity} passengers"),
				("Range", f"{range_nm:,} nm"),
				("Hourly Cost", f"${hourly_cost:,}/hr"),
				("Max Duration", f"{max_duration:.1f} hours"),
				("Max Seats/Row", str(max_seats_per_row)),
				("Max Rows", str(max_rows)),
			]
			
			if oil_capacity:
				stats.append(("Oil Capacity", f"{oil_capacity} quarts"))
			
			for i, (label, value) in enumerate(stats):
				col = left_col if i < len(stats) // 2 else right_col
				row = ttk.Frame(col)
				row.pack(fill=tk.X, pady=2)
				ttk.Label(row, text=f"{label}:", width=16, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT)
				ttk.Label(row, text=value, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(8, 0))
			
			# Cabin preview section
			cabin_frame = ttk.LabelFrame(dialog, text="Default Cabin Configuration Preview")
			cabin_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
			
			# Get default layout
			default_layout = get_default_layout(capacity, max_seats_per_row, max_rows)
			total_seats = calculate_cabin_total_seats(default_layout)
			comfort = calculate_cabin_comfort(default_layout)
			
			# Cabin summary
			summary_frame = ttk.Frame(cabin_frame)
			summary_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
			ttk.Label(summary_frame, text=f"Total Seats: {total_seats}", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
			ttk.Label(summary_frame, text=f"Comfort Rating: {comfort:.2f} ⭐", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
			ttk.Label(summary_frame, text=f"Rows: {len(default_layout)}", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
			
			# Cabin visual preview
			preview_frame = ttk.Frame(cabin_frame)
			preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
			
			canvas = tk.Canvas(preview_frame, bg="#ffffff", height=400)
			scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
			canvas.configure(yscrollcommand=scrollbar.set)
			
			inner_frame = ttk.Frame(canvas)
			canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
			
			def configure_canvas(event):
				canvas_width = event.width
				canvas.itemconfig(canvas_window, width=canvas_width)
				canvas.configure(scrollregion=canvas.bbox("all"))
			
			canvas.bind("<Configure>", configure_canvas)
			canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
			scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
			
			# Draw cabin layout
			seat_types_map = {st["code"]: st for st in get_seat_types()}
			
			for row_data in default_layout:
				row_num = row_data.get("row", 0)
				seat_code = row_data.get("seat_type", "SLIM")
				seats = row_data.get("seats", 0)
				seat_type = seat_types_map.get(seat_code, seat_types_map["SLIM"])
				color = seat_type.get("color", "#e0e0e0")
				
				# Row label
				ttk.Label(inner_frame, text=f"Row {row_num}:", width=10, font=("Segoe UI", 9)).grid(row=row_num-1, column=0, padx=5, pady=2, sticky="w")
				
				# Draw seats
				seat_frame = ttk.Frame(inner_frame)
				seat_frame.grid(row=row_num-1, column=1, padx=5, pady=2, sticky="w")
				
				for i in range(seats):
					seat_label = tk.Label(seat_frame, text="", width=3, height=1, bg=color, relief=tk.RAISED, borderwidth=1)
					seat_label.pack(side=tk.LEFT, padx=1)
				
				# Seat type label
				ttk.Label(inner_frame, text=seat_type.get("name", "Slim"), font=("Segoe UI", 8), foreground="#666").grid(row=row_num-1, column=2, padx=5, pady=2, sticky="w")
			
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
			
			# Close button
			btn_frame = ttk.Frame(dialog)
			btn_frame.pack(padx=20, pady=(10, 20))
			ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack()
			
		except Exception as exc:
			import traceback
			traceback.print_exc()
			messagebox.showerror("Aircraft Details", f"Error loading details: {exc}")

	def _on_edit_duration(self):
		item = self.new_tree.focus()
		if not item:
			messagebox.showinfo("Store", "Select an aircraft type to edit.")
			return
		vals = self.new_tree.item(item, "values")
		type_code = vals[0]
		try:
			from services import get_aircraft_max_duration, set_aircraft_max_duration
			current = get_aircraft_max_duration(type_code)
			new_dur_str = simpledialog.askstring("Edit Max Duration", f"Current max duration for {type_code}: {current:.1f} hours\nEnter new max duration (hours):", initialvalue=str(current))
			if new_dur_str is None:
				return
			new_dur = float(new_dur_str)
			set_aircraft_max_duration(type_code, new_dur)
			self.refresh()
			messagebox.showinfo("Store", f"Max duration for {type_code} updated to {new_dur:.1f} hours.")
		except ValueError as exc:
			messagebox.showerror("Store", f"Invalid value: {exc}")
		except Exception as exc:
			messagebox.showerror("Store", str(exc))


# MaintenanceFrame removed - maintenance is now handled in FleetManagerFrame


class ParkingFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Parking Manager")

		form = ttk.LabelFrame(self, text="Buy Parking / Hangars")
		form.pack(fill=tk.X, padx=12, pady=8)
		self.airport_var = tk.StringVar(value="HOME")
		self.spots_var = tk.StringVar(value="1")
		self.hangars_var = tk.StringVar(value="0")
		row = ttk.Frame(form); row.pack(fill=tk.X, padx=8, pady=4)
		ttk.Label(row, text="Airport", width=12).pack(side=tk.LEFT)
		ttk.Entry(row, textvariable=self.airport_var, width=10).pack(side=tk.LEFT, padx=(0, 12))
		ttk.Label(row, text="Spots", width=8).pack(side=tk.LEFT)
		ttk.Entry(row, textvariable=self.spots_var, width=8).pack(side=tk.LEFT, padx=(0, 12))
		ttk.Label(row, text="Hangars", width=8).pack(side=tk.LEFT)
		ttk.Entry(row, textvariable=self.hangars_var, width=8).pack(side=tk.LEFT, padx=(0, 12))
		btn = ttk.Button(form, text="Buy", command=wrap_command_with_sound(self._on_buy))
		btn.pack(side=tk.LEFT, padx=8, pady=6)

		# Costs info
		costs = ttk.Label(form, text="Costs: Spot $100,000   Hangar $750,000")
		costs.pack(side=tk.LEFT, padx=12)

		list_frame = ttk.LabelFrame(self, text="Owned Parking")
		list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		cols = ("airport", "spots", "hangars")
		self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=18)
		for c, h in zip(cols, ["Airport", "Spots", "Hangars"]):
			self.tree.heading(c, text=h)
			self.tree.column(c, width=160, anchor=tk.W)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		self.tree.delete(*self.tree.get_children())
		try:
			from services import list_parking
			for ap, info in list_parking().items():
				spots = info.get("spots", 0)
				hangars = info.get("hangars", 0)
				# Support both old format (int) and new format (list)
				if isinstance(spots, list):
					spot_count = len(spots)
					if spot_count > 0:
						spot_display = f"{spot_count} ({', '.join([s.get('name', 'Unnamed') for s in spots])})"
					else:
						spot_display = "0"
				else:
					spot_display = str(int(spots))
				if isinstance(hangars, list):
					hangar_count = len(hangars)
					if hangar_count > 0:
						hangar_display = f"{hangar_count} ({', '.join([h.get('name', 'Unnamed') for h in hangars])})"
					else:
						hangar_display = "0"
				else:
					hangar_display = str(int(hangars))
				self.tree.insert("", tk.END, values=(ap, spot_display, hangar_display))
		except Exception:
			pass

	def _on_buy(self):
		try:
			from services import buy_parking
			ap = self.airport_var.get().strip().upper()
			spots = int(self.spots_var.get())
			hangars = int(self.hangars_var.get())
			
			# Prompt for names if purchasing spots or hangars
			spot_names = None
			hangar_names = None
			
			if spots > 0 or hangars > 0:
				# Create a dialog to get names
				dialog = tk.Toplevel(self)
				dialog.title("Name Parking Spots / Hangars")
				# Adjust height based on number of items (min 400, +40 per item)
				total_items = spots + hangars
				height = max(400, 300 + total_items * 40)
				dialog.geometry(f"600x{height}")
				dialog.transient(self)
				dialog.grab_set()
				
				# Create scrollable frame if needed
				canvas = tk.Canvas(dialog)
				scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
				scrollable_frame = ttk.Frame(canvas)
				
				scrollable_frame.bind(
					"<Configure>",
					lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
				)
				
				canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
				canvas.configure(yscrollcommand=scrollbar.set)
				
				instruction_text = []
				if spots > 0:
					instruction_text.append(f"{spots} parking spot(s)")
				if hangars > 0:
					instruction_text.append(f"{hangars} hangar(s)")
				ttk.Label(scrollable_frame, text=f"Enter names for {', '.join(instruction_text)}:", font=("Segoe UI", 9)).pack(pady=10)
				
				spot_entries = []
				hangar_entries = []
				entry_frame = ttk.Frame(scrollable_frame)
				entry_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
				
				# Add spot name entries
				for i in range(spots):
					row = ttk.Frame(entry_frame)
					row.pack(fill=tk.X, pady=4)
					ttk.Label(row, text=f"Spot {i+1}:", width=12).pack(side=tk.LEFT)
					entry = ttk.Entry(row, width=30)
					entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
					entry.insert(0, f"Spot {i+1}")  # Default name
					spot_entries.append(entry)
				
				# Add hangar name entries
				for i in range(hangars):
					row = ttk.Frame(entry_frame)
					row.pack(fill=tk.X, pady=4)
					ttk.Label(row, text=f"Hangar {i+1}:", width=12).pack(side=tk.LEFT)
					entry = ttk.Entry(row, width=30)
					entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
					entry.insert(0, f"Hangar {i+1}")  # Default name
					hangar_entries.append(entry)
				
				# Pack canvas and scrollbar
				canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
				scrollbar.pack(side="right", fill="y", pady=10)
				
				result = [None, None]
				
				def on_ok():
					spot_names_list = []
					hangar_names_list = []
					
					for idx, entry in enumerate(spot_entries):
						name = entry.get().strip()
						spot_names_list.append(name if name else f"Spot {idx+1}")
					
					for idx, entry in enumerate(hangar_entries):
						name = entry.get().strip()
						hangar_names_list.append(name if name else f"Hangar {idx+1}")
					
					result[0] = spot_names_list if spot_names_list else None
					result[1] = hangar_names_list if hangar_names_list else None
					dialog.destroy()
				
				def on_cancel():
					dialog.destroy()
				
				button_frame = ttk.Frame(dialog)
				button_frame.pack(pady=10)
				ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
				ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
				
				# Focus on first entry and bind Enter key
				if spot_entries:
					spot_entries[0].focus_set()
					spot_entries[0].bind("<Return>", lambda e: on_ok())
				elif hangar_entries:
					hangar_entries[0].focus_set()
					hangar_entries[0].bind("<Return>", lambda e: on_ok())
				
				dialog.wait_window()
				
				if result[0] is None and result[1] is None:
					return  # User cancelled
				
				spot_names = result[0]
				hangar_names = result[1]
			
			buy_parking(ap, spots, hangars, spot_names, hangar_names)
			self.refresh()
			messagebox.showinfo("Parking", "Purchase successful.")
		except Exception as exc:
			messagebox.showerror("Parking", str(exc))


class FlightsFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Flights")

		form = ttk.LabelFrame(self, text="Start Flight")
		form.pack(fill=tk.X, padx=12, pady=8)

		self.ac_var = tk.StringVar()
		self.route_var = tk.StringVar(value="HOME-DEST")
		self.price_var = tk.StringVar(value="200")
		self.hrs_var = tk.StringVar(value="1.5")

		row1 = ttk.Frame(form); row1.pack(fill=tk.X, padx=8, pady=4)
		ttk.Label(row1, text="Aircraft", width=12, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
		self.ac_combo = ttk.Combobox(row1, textvariable=self.ac_var, width=40, state="readonly")
		self.ac_combo.pack(side=tk.LEFT)
		self.ac_combo.bind("<<ComboboxSelected>>", lambda e: self._update_preview())

		row2 = ttk.Frame(form); row2.pack(fill=tk.X, padx=8, pady=4)
		for label, var, w in [("Route", self.route_var, 18), ("Ticket $", self.price_var, 8), ("Hours", self.hrs_var, 8)]:
			ttk.Label(row2, text=label, width=12).pack(side=tk.LEFT)
			entry = ttk.Entry(row2, textvariable=var, width=w)
			entry.pack(side=tk.LEFT, padx=(0, 12))

		btns = ttk.Frame(form); btns.pack(fill=tk.X, padx=8, pady=6)
		btn_start = tk.Button(btns, text="✈️ Start Flight", command=wrap_command_with_sound(self._on_start),
			bg=GAME_COLORS["button_bg"],
			fg=GAME_COLORS["text_primary"],
			font=("Segoe UI", 10, "bold"),
			relief='raised',
			borderwidth=2,
			padx=12,
			pady=8,
			cursor='hand2',
			activebackground=GAME_COLORS["button_hover"],
			activeforeground=GAME_COLORS["accent_blue"])
		btn_start.pack(side=tk.LEFT)

		# Preview panel for comfort impact
		preview = ttk.LabelFrame(form, text="Impact Preview")
		preview.pack(fill=tk.X, padx=8, pady=4)
		self.preview_var = tk.StringVar(value="Select aircraft and enter values to see impact")
		ttk.Label(preview, textvariable=self.preview_var, font=("Segoe UI", 9)).pack(padx=8, pady=4)
		# Bind variables to update preview
		for var in [self.ac_var, self.price_var, self.hrs_var]:
			var.trace_add("write", lambda *args: self._update_preview())

		list_frame = ttk.LabelFrame(self, text="Active Flights")
		list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		cols = ("id", "ac", "route", "pax", "price", "hrs")
		self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=16)
		for c, h in zip(cols, ["ID", "Aircraft", "Route", "Pax", "Ticket", "Hours"]):
			self.tree.heading(c, text=h)
			self.tree.column(c, width=120, anchor=tk.W)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

		btn_frame = ttk.Frame(list_frame)
		btn_frame.pack(side=tk.RIGHT, padx=8, pady=(0, 8))
		def create_game_button(parent, text, command):
			return tk.Button(parent, text=text, command=wrap_command_with_sound(command),
				bg=GAME_COLORS["button_bg"],
				fg=GAME_COLORS["text_primary"],
				font=("Segoe UI", 9, "bold"),
				relief='raised',
				borderwidth=2,
				padx=10,
				pady=6,
				cursor='hand2',
				activebackground=GAME_COLORS["button_hover"],
				activeforeground=GAME_COLORS["accent_blue"])
		
		btn_weight = create_game_button(btn_frame, "⚖️ View Weight Manifest", self._on_view_weight_manifest)
		btn_weight.pack(side=tk.LEFT, padx=(0, 5))
		btn_end = create_game_button(btn_frame, "✅ End Selected Flight", self._on_end)
		btn_end.pack(side=tk.LEFT, padx=(0, 5))
		btn_cancel = create_game_button(btn_frame, "❌ Cancel Flight", self._on_cancel)
		btn_cancel.pack(side=tk.LEFT)

		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		try:
			from services import list_fleet, list_active_flights
			fleet = list_fleet()
			choices = [f"{ac['id']} - {ac['name']} ({ac['type_code']})" for ac in fleet]
			self.ac_combo["values"] = choices
			if choices and not self.ac_var.get():
				self.ac_var.set(choices[0])
			self.tree.delete(*self.tree.get_children())
			for flt in list_active_flights():
				vals = (
					flt.get("flight_id"), flt.get("aircraft_id"), flt.get("route"),
					flt.get("passengers"), f"$ {flt.get('ticket_price', 0):,}", str(flt.get("duration_hours")),
				)
				self.tree.insert("", tk.END, values=vals)
			self._update_preview()
		except Exception:
			pass

	def _update_preview(self):
		try:
			label = self.ac_var.get()
			if " - " not in label:
				self.preview_var.set("Select aircraft to see impact")
				return
			ac_id = label.split(" - ", 1)[0]
			from services import get_aircraft_cabin_comfort, get_aircraft_cabin_capacity, list_fleet
			from catalog import aircraft_catalog
			fleet = list_fleet()
			ac = next((x for x in fleet if x.get("id") == ac_id), None)
			if not ac:
				self.preview_var.set("Aircraft not found")
				return
			comfort = get_aircraft_cabin_comfort(ac_id)
			actual_capacity = get_aircraft_cabin_capacity(ac_id)
			try:
				price = float(self.price_var.get())
				hrs = float(self.hrs_var.get())
			except ValueError:
				self.preview_var.set(f"Cabin Comfort: {comfort:.2f} ⭐ | Capacity: {actual_capacity} seats (enter price and hours to see impact)")
				return
			cat = {c["type_code"]: c for c in aircraft_catalog()}
			info = cat.get(ac.get("type_code"))
			if not info:
				self.preview_var.set(f"Cabin Comfort: {comfort:.2f} ⭐ | Capacity: {actual_capacity} seats")
				return
			hourly_cost = float(info.get("hourly_cost", 2000))
			# Use actual cabin capacity, fallback to catalog if 0
			cap = actual_capacity if actual_capacity > 0 else int(info.get("capacity", 150))
			# Match the formula in services.py
			base_min_per_seat_per_hour = 15.0
			operating_cost_per_seat_per_hour = (hourly_cost / cap) if cap > 0 else 0
			baseline_per_hour_per_seat = max(base_min_per_seat_per_hour, operating_cost_per_seat_per_hour * 2.0) * 3.5
			comfort_mult = 1.0 + (comfort - 1.0) * 0.5
			baseline = baseline_per_hour_per_seat * hrs * comfort_mult
			comfort_boost = 1.0 + (comfort - 1.0) * 0.15
			price_ratio = baseline / price if price > 0 else 0.1
			demand_ratio = min(1.0, max(0.1, price_ratio * comfort_boost))
			# Calculate passengers based on demand - try to fill to capacity
			pax_requested = cap
			# Apply seasonal demand
			from services import get_seasonal_demand_multiplier
			seasonal_mult = get_seasonal_demand_multiplier()
			demand_ratio *= seasonal_mult
			
			est_pax = max(0, min(int(round(pax_requested * demand_ratio)), cap))
			est_revenue = est_pax * price
			load_factor = (est_pax / cap * 100) if cap > 0 else 0
			
			season_note = f" | Season: {seasonal_mult:.1f}x" if seasonal_mult != 1.0 else ""
			self.preview_var.set(f"Comfort: {comfort:.2f} ⭐ | Capacity: {cap} seats | Baseline fare: ${baseline:,.0f} | Est. boarded: {est_pax}/{cap} ({load_factor:.0f}% load) | Est. revenue: ${est_revenue:,}{season_note}")
		except Exception:
			self.preview_var.set("Error calculating preview")

	def _show_walkaround_dialog(self, aircraft_id: str, route: str, price: int, hrs: float) -> Dict[str, Any]:
		"""Show walkaround inspection dialog. Returns decision dict."""
		from services import walkaround_check, refill_aircraft_oil, calculate_snag_penalties, ground_aircraft
		
		# Perform walkaround
		walkaround = walkaround_check(aircraft_id)
		
		dialog = tk.Toplevel(self)
		dialog.title("Walkaround Inspection")
		dialog.geometry("850x750")
		dialog.transient(self)
		dialog.grab_set()
		
		# Center the dialog
		dialog.update_idletasks()
		x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
		y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
		dialog.geometry(f"+{x}+{y}")
		
		result = {"proceed": False, "ground": False, "refill_oil": False, "penalties": None}
		
		# Title
		title_frame = ttk.Frame(dialog)
		title_frame.pack(padx=20, pady=(20, 10))
		ttk.Label(title_frame, text="Pre-Flight Walkaround Inspection", font=("Segoe UI", 14, "bold")).pack()
		ttk.Label(title_frame, text=f"Aircraft: {aircraft_id} | Route: {route}", font=("Segoe UI", 9), foreground="#666").pack(pady=(4, 0))
		
		# Add a brief instruction
		instruction = ttk.Label(title_frame, 
			text="Inspect the aircraft thoroughly. Check all systems, surfaces, and components before flight.",
			font=("Segoe UI", 8), foreground="#888", wraplength=650)
		instruction.pack(pady=(4, 0))
		
		main_frame = ttk.Frame(dialog)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
		
		# Oil Level Section (only for smaller planes)
		oil_level = walkaround.get("oil_level")
		if oil_level is not None:
			# Smaller plane - show oil tracking
			oil_frame = ttk.LabelFrame(main_frame, text="Oil Level")
			oil_frame.pack(fill=tk.X, pady=(0, 10))
			
			oil_capacity = walkaround.get("oil_capacity", 32.0)
			oil_minimum = walkaround.get("oil_minimum", 12.0)
			oil_low = walkaround.get("oil_low", False)
			oil_critical = walkaround.get("oil_critical", False)
			hours_since_oil_change = walkaround.get("hours_since_oil_change", 0.0)
			oil_change_interval = walkaround.get("oil_change_interval", 50.0)
			oil_change_due = walkaround.get("oil_change_due", False)
			oil_change_overdue = walkaround.get("oil_change_overdue", False)
			oil_percent = (oil_level / oil_capacity * 100) if oil_capacity > 0 else 0
			
			oil_info = ttk.Frame(oil_frame)
			oil_info.pack(fill=tk.X, padx=10, pady=8)
			
			oil_color = "#b00020" if oil_critical else "#ff9800" if oil_low else "#0a7f2e"
			oil_status = "CRITICAL" if oil_critical else "LOW" if oil_low else "OK"
			
			ttk.Label(oil_info, text=f"Oil Level: {oil_level:.1f} qts / {oil_capacity:.1f} qts (min: {oil_minimum:.1f} qts) ({oil_percent:.0f}%)", 
				font=("Segoe UI", 10, "bold"), foreground=oil_color).pack(side=tk.LEFT)
			ttk.Label(oil_info, text=f"Status: {oil_status}", font=("Segoe UI", 10), foreground=oil_color).pack(side=tk.RIGHT)
			
			# Oil change status
			if oil_change_overdue:
				oil_change_warning = ttk.Label(oil_frame,
					text=f"⚠️ OIL CHANGE OVERDUE! {hours_since_oil_change:.1f}h since last change (interval: {oil_change_interval:.0f}h). Fine may apply if problems occur.",
					font=("Segoe UI", 9), foreground="#ff4444", wraplength=650)
				oil_change_warning.pack(padx=10, pady=(0, 8))
			elif oil_change_due:
				oil_change_warning = ttk.Label(oil_frame,
					text=f"⚠️ Oil change due: {hours_since_oil_change:.1f}h since last change (interval: {oil_change_interval:.0f}h).",
					font=("Segoe UI", 9), foreground="#ff9800", wraplength=650)
				oil_change_warning.pack(padx=10, pady=(0, 8))
			else:
				oil_change_status = ttk.Label(oil_frame,
					text=f"✓ Oil change status: {hours_since_oil_change:.1f}h / {oil_change_interval:.0f}h",
					font=("Segoe UI", 9), foreground="#0a7f2e", wraplength=650)
				oil_change_status.pack(padx=10, pady=(0, 8))
			
			if oil_low or oil_critical:
				oil_warning = ttk.Label(oil_frame, 
					text=f"⚠️ Oil level is {'CRITICALLY LOW' if oil_critical else 'LOW'}. Top up oil monthly based on capacity and minimum.",
					font=("Segoe UI", 9), foreground="#ff9800", wraplength=650)
				oil_warning.pack(padx=10, pady=(0, 8))
			
			# Oil buttons
			oil_btn_frame = ttk.Frame(oil_frame)
			oil_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
			if oil_low or oil_critical:
				ttk.Button(oil_btn_frame, text="Top Up Oil", 
					command=lambda: self._refill_oil_in_dialog(dialog, aircraft_id, oil_frame)).pack(side=tk.LEFT, padx=(0, 5))
			if oil_change_due or oil_change_overdue:
				ttk.Button(oil_btn_frame, text="Full Oil Change", 
					command=lambda: self._change_oil_in_dialog(dialog, aircraft_id, oil_frame)).pack(side=tk.LEFT)
			
			# Tire Condition Section (for smaller planes)
			tire_condition = walkaround.get("tire_condition")
			tire_wear = walkaround.get("tire_wear")
			if tire_condition is not None and tire_wear is not None:
				tire_frame = ttk.LabelFrame(main_frame, text="Tire Condition")
				tire_frame.pack(fill=tk.X, pady=(0, 10))
				
				tire_info = ttk.Frame(tire_frame)
				tire_info.pack(fill=tk.X, padx=10, pady=8)
				
				tire_color = "#b00020" if tire_condition == "Critical" else "#ff9800" if tire_condition == "Poor" else "#666" if tire_condition == "Fair" else "#0a7f2e"
				
				ttk.Label(tire_info, text=f"Tire Wear: {tire_wear:.1f}%", 
					font=("Segoe UI", 10, "bold"), foreground=tire_color).pack(side=tk.LEFT)
				ttk.Label(tire_info, text=f"Condition: {tire_condition}", 
					font=("Segoe UI", 10), foreground=tire_color).pack(side=tk.RIGHT)
				
				if tire_condition in ["Poor", "Critical"]:
					tire_warning = ttk.Label(tire_frame, 
						text=f"⚠️ Tires showing {'CRITICAL' if tire_condition == 'Critical' else 'significant'} wear. Consider replacement during next maintenance.",
						font=("Segoe UI", 9), foreground="#ff9800", wraplength=650)
					tire_warning.pack(padx=10, pady=(0, 8))
		# Airliners don't show oil/tire section (managed automatically)
		
		# Snags Section
		snags = walkaround.get("snags", [])
		snags_frame = ttk.LabelFrame(main_frame, text=f"Snags Found ({len(snags)})")
		snags_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
		
		if snags:
			# Scrollable list of snags
			canvas_container = ttk.Frame(snags_frame)
			canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
			
			scrollbar = ttk.Scrollbar(canvas_container, orient="vertical")
			scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
			
			snags_canvas = tk.Canvas(canvas_container, yscrollcommand=scrollbar.set, height=280)
			snags_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
			scrollbar.config(command=snags_canvas.yview)
			
			snags_inner = ttk.Frame(snags_canvas)
			snags_canvas_window = snags_canvas.create_window((0, 0), window=snags_inner, anchor="nw")
			
			def _configure_snags_canvas(event):
				snags_canvas.configure(scrollregion=snags_canvas.bbox("all"))
				canvas_width = event.width
				snags_canvas.itemconfig(snags_canvas_window, width=canvas_width)
			snags_canvas.bind("<Configure>", _configure_snags_canvas)
			
			for snag in snags:
				snag_frame = ttk.Frame(snags_inner)
				snag_frame.pack(fill=tk.X, pady=4)
				
				severity = snag.get("severity", "Minor")
				severity_color = "#b00020" if severity == "Critical" else "#ff9800" if severity == "Major" else "#666"
				
				ttk.Label(snag_frame, text=f"{severity}: {snag.get('component')}", 
					font=("Segoe UI", 10, "bold"), foreground=severity_color).pack(anchor=tk.W)
				# Show detailed description if available
				description = snag.get("description", "")
				if description:
					ttk.Label(snag_frame, text=description, 
						font=("Segoe UI", 9), foreground="#666", wraplength=600).pack(anchor=tk.W, pady=(2, 0))
				
				if snag.get("mel"):
					ttk.Label(snag_frame, text="✓ MEL eligible - can fly under Minimum Equipment List", 
						font=("Segoe UI", 8), foreground="#0a7f2e").pack(anchor=tk.W)
				elif severity == "Critical":
					ttk.Label(snag_frame, text="✗ CRITICAL - Flight prohibited", 
						font=("Segoe UI", 8, "bold"), foreground="#b00020").pack(anchor=tk.W)
		else:
			ttk.Label(snags_frame, text="✓ No snags found - aircraft is in good condition", 
				font=("Segoe UI", 10), foreground="#0a7f2e").pack(pady=20)
		
		# Calculate penalties if continuing (only check oil for smaller planes)
		oil_low = walkaround.get("oil_low", False)
		oil_critical = walkaround.get("oil_critical", False)
		penalties = calculate_snag_penalties(snags, oil_low, oil_critical) if (snags or oil_low or oil_critical) else None
		if penalties and penalties.get("total_penalty", 0) > 0:
			penalties_frame = ttk.LabelFrame(main_frame, text="⚠️ Penalties for Continuing Flight")
			penalties_frame.pack(fill=tk.X, pady=(0, 10))
			
			penalty_text = f"Total Fine: ${penalties['total_penalty']:,}\n"
			penalty_text += f"Reputation Penalty: {penalties['reputation_penalty']:.1f}\n\n"
			penalty_text += "Reasons:\n"
			for reason in penalties.get("reasons", []):
				penalty_text += f"• {reason}\n"
			
			ttk.Label(penalties_frame, text=penalty_text, font=("Segoe UI", 9), 
				foreground="#b00020", justify=tk.LEFT, wraplength=650).pack(padx=10, pady=8)
		
		# Check for critical snags that prohibit flight
		critical_snags = [s for s in snags if s.get("severity") == "Critical" and not s.get("mel")]
		can_proceed = len(critical_snags) == 0
		
		# Buttons
		btn_frame = ttk.Frame(dialog)
		btn_frame.pack(padx=20, pady=(10, 20))
		
		def proceed_flight():
			result["proceed"] = True
			result["penalties"] = penalties
			dialog.destroy()
		
		def ground_aircraft_btn():
			result["ground"] = True
			dialog.destroy()
		
		if can_proceed:
			ttk.Button(btn_frame, text="Continue Flight", command=proceed_flight).pack(side=tk.LEFT, padx=5)
		else:
			ttk.Label(btn_frame, text="CRITICAL snags found - flight cannot proceed", 
				font=("Segoe UI", 9, "bold"), foreground="#b00020").pack(side=tk.LEFT, padx=5)
		
		ttk.Button(btn_frame, text="Ground Aircraft", command=ground_aircraft_btn).pack(side=tk.LEFT, padx=5)
		ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
		
		dialog.wait_window()
		return result
	
	def _refill_oil_in_dialog(self, dialog, aircraft_id: str, oil_frame):
		"""Check oil and optionally top up."""
		try:
			from services import refill_aircraft_oil, walkaround_check
			walkaround = walkaround_check(aircraft_id)
			oil_level = walkaround.get("oil_level", 0.0)
			oil_capacity = walkaround.get("oil_capacity", 32.0)
			oil_minimum = walkaround.get("oil_minimum", 12.0)
			oil_percent = (oil_level / oil_capacity * 100) if oil_capacity > 0 else 0
			
			# Show oil level in popup
			status_msg = f"Oil Level: {oil_level:.1f} / {oil_capacity:.1f} quarts ({oil_percent:.0f}%)\n"
			status_msg += f"Minimum: {oil_minimum:.1f} quarts\n\n"
			
			if oil_level < oil_minimum:
				status_msg += "⚠️ CRITICAL: Oil below minimum!"
			elif oil_percent < 50:
				status_msg += "⚠️ Oil level is low"
			else:
				status_msg += "✓ Oil level is good"
			
			# Ask if they want to add oil
			if oil_level < oil_capacity:
				if messagebox.askyesno("Check Oil", status_msg + "\n\nWould you like to add oil?"):
					try:
						refill_aircraft_oil(aircraft_id)
						messagebox.showinfo("Oil Top-Up", "Oil topped up successfully!")
						# Refresh oil display
						for widget in oil_frame.winfo_children():
							widget.destroy()
						updated_walkaround = walkaround_check(aircraft_id)
						self._update_oil_display_in_dialog(oil_frame, updated_walkaround, dialog, aircraft_id)
					except Exception as exc:
						messagebox.showerror("Oil Top-Up", str(exc))
			else:
				messagebox.showinfo("Check Oil", status_msg)
		except Exception as exc:
			messagebox.showerror("Check Oil", str(exc))
	
	def _change_oil_in_dialog(self, dialog, aircraft_id: str, oil_frame):
		"""Perform full oil change."""
		try:
			from services import change_aircraft_oil, walkaround_check, list_fleet
			fleet = list_fleet()
			aircraft = next((ac for ac in fleet if ac.get("id") == aircraft_id), None)
			if not aircraft:
				messagebox.showerror("Oil Change", "Aircraft not found.")
				return
			
			hours_since = aircraft.get("hours_since_oil_change", 0.0)
			confirm = messagebox.askyesno("Full Oil Change", 
				f"Perform full oil change on {aircraft_id}?\n\n"
				f"Hours since last change: {hours_since:.1f}h\n"
				f"Recommended interval: 50 hours\n\n"
				f"This will cost ${aircraft.get('oil_capacity', 32.0) * 100:.0f} (more expensive than top-up).")
			if confirm:
				change_aircraft_oil(aircraft_id)
				messagebox.showinfo("Oil Change", "Full oil change completed successfully!")
				# Refresh oil display
				for widget in oil_frame.winfo_children():
					widget.destroy()
				updated_walkaround = walkaround_check(aircraft_id)
				self._update_oil_display_in_dialog(oil_frame, updated_walkaround, dialog, aircraft_id)
		except Exception as exc:
			messagebox.showerror("Oil Change", str(exc))
	
	def _update_oil_display_in_dialog(self, oil_frame, walkaround, dialog, aircraft_id):
		"""Update oil display in walkaround dialog."""
		oil_level = walkaround.get("oil_level")
		if oil_level is None:
			return
		
		oil_capacity = walkaround.get("oil_capacity", 32.0)
		oil_minimum = walkaround.get("oil_minimum", 12.0)
		oil_low = walkaround.get("oil_low", False)
		oil_critical = walkaround.get("oil_critical", False)
		hours_since_oil_change = walkaround.get("hours_since_oil_change", 0.0)
		oil_change_interval = walkaround.get("oil_change_interval", 50.0)
		oil_change_due = walkaround.get("oil_change_due", False)
		oil_change_overdue = walkaround.get("oil_change_overdue", False)
		oil_percent = (oil_level / oil_capacity * 100) if oil_capacity > 0 else 0
		
		oil_info = ttk.Frame(oil_frame)
		oil_info.pack(fill=tk.X, padx=10, pady=8)
		ttk.Label(oil_info, text=f"Level: {oil_level:.1f} / {oil_capacity:.1f} quarts ({oil_percent:.0f}%)", 
			font=("Segoe UI", 10)).pack(side=tk.LEFT)
		ttk.Label(oil_info, text=f"Minimum: {oil_minimum:.1f} quarts", 
			font=("Segoe UI", 9), foreground="#666").pack(side=tk.LEFT, padx=(20, 0))
		
		# Oil change status
		if oil_change_overdue:
			oil_change_warning = ttk.Label(oil_frame,
				text=f"⚠️ OIL CHANGE OVERDUE! {hours_since_oil_change:.1f}h since last change (interval: {oil_change_interval:.0f}h). Fine may apply if problems occur.",
				font=("Segoe UI", 9), foreground="#ff4444", wraplength=650)
			oil_change_warning.pack(padx=10, pady=(0, 8))
		elif oil_change_due:
			oil_change_warning = ttk.Label(oil_frame,
				text=f"⚠️ Oil change due: {hours_since_oil_change:.1f}h since last change (interval: {oil_change_interval:.0f}h).",
				font=("Segoe UI", 9), foreground="#ff9800", wraplength=650)
			oil_change_warning.pack(padx=10, pady=(0, 8))
		else:
			oil_change_status = ttk.Label(oil_frame,
				text=f"✓ Oil change status: {hours_since_oil_change:.1f}h / {oil_change_interval:.0f}h",
				font=("Segoe UI", 9), foreground="#0a7f2e", wraplength=650)
			oil_change_status.pack(padx=10, pady=(0, 8))
		
		if oil_low or oil_critical:
			oil_warning = ttk.Label(oil_frame, 
				text=f"⚠️ Oil level is {'CRITICALLY LOW' if oil_critical else 'LOW'}. Top up oil monthly based on capacity and minimum.",
				font=("Segoe UI", 9), foreground="#ff9800", wraplength=650)
			oil_warning.pack(padx=10, pady=(0, 8))
		
		# Oil buttons
		oil_btn_frame = ttk.Frame(oil_frame)
		oil_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
		if oil_low or oil_critical:
			ttk.Button(oil_btn_frame, text="Top Up Oil", 
				command=lambda: self._refill_oil_in_dialog(dialog, aircraft_id, oil_frame)).pack(side=tk.LEFT, padx=(0, 5))
		if oil_change_due or oil_change_overdue:
			ttk.Button(oil_btn_frame, text="Full Oil Change", 
				command=lambda: self._change_oil_in_dialog(dialog, aircraft_id, oil_frame)).pack(side=tk.LEFT)
	
	def _show_random_event(self):
		"""Show a random event popup when starting a flight.
		
		To add new events, simply add a dictionary to the RANDOM_EVENTS list below.
		Each event should have:
		- 'title': Title of the event popup
		- 'message': The event description
		- 'probability': Float between 0.0 and 1.0 (e.g., 0.3 = 30% chance)
		"""
		import random
		
		# Define random events - easy to extend by adding new dictionaries here
		RANDOM_EVENTS = [
			{
				"title": "Extra Luggage Request",
				"message": "A passenger has requested to bring 100lbs of extra luggage onto the plane. The request has been noted.",
				"probability": .25  # 25% chance
			},
			# Add more events here by copying the format above
			# Example:
			# {
			# 	"title": "Event Name",
			# 	"message": "Event description",
			# 	"probability": 0.15  # 15% chance
			# },
		]
		
		# Check each event based on its probability and collect those that trigger
		triggered_events = []
		for event in RANDOM_EVENTS:
			if random.random() < event["probability"]:
				triggered_events.append(event)
		
		# If any events triggered, randomly select one to show
		if triggered_events:
			selected_event = random.choice(triggered_events)
			play_sound("notification")
			messagebox.showinfo(selected_event["title"], selected_event["message"])
	
	def _on_start(self):
		try:
			from services import start_flight, preflight_check, ground_aircraft, update_reputation
			from storage import load_state, save_state
			
			label = self.ac_var.get()
			if " - " not in label:
				messagebox.showwarning("Flights", "Select an aircraft.")
				return
			ac_id = label.split(" - ", 1)[0]
			route = self.route_var.get().strip()
			price = int(self.price_var.get())
			hrs = float(self.hrs_var.get())
			
			# Preflight failure check (basic maintenance checks)
			check = preflight_check(ac_id, hrs)
			issue_note = None
			if check.get("failed"):
				comp = check.get("component")
				mel = check.get("mel")
				sev = check.get("severity")
				if mel:
					proceed = messagebox.askyesno("Preflight Issue", f"{comp} failure ({sev}). Continue under MEL?\nYes = fly; No = ground the aircraft")
					if not proceed:
						ground_aircraft(ac_id, f"Grounded due to {comp}")
						messagebox.showinfo("Flights", "Aircraft grounded.")
						return
					issue_note = f"MEL: {comp} inoperative"
				else:
					messagebox.showinfo("Preflight Issue", f"{comp} failure ({sev}). Flight cannot depart. Aircraft grounded.")
					ground_aircraft(ac_id, f"Grounded due to {comp}")
					return
			
			# Walkaround inspection
			walkaround_result = self._show_walkaround_dialog(ac_id, route, price, hrs)
			
			if walkaround_result.get("ground"):
				ground_aircraft(ac_id, "Grounded after walkaround inspection")
				messagebox.showinfo("Flights", "Aircraft grounded.")
				return
			
			if not walkaround_result.get("proceed"):
				# User cancelled walkaround
				return
			
			# Random event popup (before starting flight)
			self._show_random_event()
			
			# Start flight
			start_flight(ac_id, route, price, hrs)
			
			# Apply penalties if any
			penalties = walkaround_result.get("penalties")
			if penalties:
				state = load_state()
				penalty_amount = penalties.get("total_penalty", 0)
				rep_penalty = penalties.get("reputation_penalty", 0.0)
				
				if penalty_amount > 0:
					state["cash"] = int(state.get("cash", 0)) - penalty_amount
					# Add ledger entry manually
					ledger = state.setdefault("ledger", [])
					entry = {
						"ts": int(time.time()),
						"category": "walkaround_penalty",
						"amount": -penalty_amount,
						"note": f"Walkaround penalties for {ac_id}: {', '.join(penalties.get('reasons', []))}"
					}
					ledger.append(entry)
					# Keep last 1000 entries
					if len(ledger) > 1000:
						ledger[:] = ledger[-1000:]
				
				if rep_penalty != 0:
					update_reputation(rep_penalty, state)
				
				save_state(state)
				
				# Attach penalty info to flight
				flights = state.get("active_flights", [])
				if flights:
					flights[-1]["walkaround_penalties"] = penalties
					state["active_flights"] = flights
					save_state(state)
			
			# Attach preflight note to the most recent active flight
			if issue_note:
				state = load_state()
				if state.get("active_flights"):
					state["active_flights"][-1]["preflight_issue"] = issue_note
					save_state(state)
			
			self.refresh()
			messagebox.showinfo("Flights", "Flight started.")
		except Exception as exc:
			messagebox.showerror("Flights", str(exc))

	def _show_flight_quality_questionnaire(self, flight_id: str):
		"""Show a dialog to rate flight quality. Returns answers dict or None if cancelled."""
		dialog = tk.Toplevel(self)
		dialog.title("Flight Quality Assessment")
		dialog.geometry("650x550")
		dialog.transient(self)
		dialog.grab_set()
		
		# Center the dialog
		dialog.update_idletasks()
		x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
		y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
		dialog.geometry(f"+{x}+{y}")
		
		answers = {}
		
		# Title
		title_frame = ttk.Frame(dialog)
		title_frame.pack(padx=20, pady=(20, 10))
		ttk.Label(title_frame, text="Flight Quality Assessment", font=("Segoe UI", 12, "bold")).pack()
		ttk.Label(title_frame, text="Enter flight performance details (custom fields are optional)", font=("Segoe UI", 9), foreground="#666").pack(pady=(4, 0))
		
		main_frame = ttk.Frame(dialog)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
		
		# Feet per minute on touchdown
		fpm_row = ttk.Frame(main_frame)
		fpm_row.pack(fill=tk.X, pady=8)
		ttk.Label(fpm_row, text="Touchdown Rate (ft/min):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
		fpm_entry = ttk.Entry(fpm_row, width=15)
		fpm_entry.pack(side=tk.LEFT)
		ttk.Label(fpm_row, text="(Lower is better)", font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=(8, 0))
		
		# Departure timing
		dep_row = ttk.Frame(main_frame)
		dep_row.pack(fill=tk.X, pady=8)
		ttk.Label(dep_row, text="Departure Timing (minutes):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
		dep_entry = ttk.Entry(dep_row, width=15)
		dep_entry.pack(side=tk.LEFT)
		ttk.Label(dep_row, text="(Negative = early, Positive = late)", font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=(8, 0))
		
		# Custom observation (optional)
		custom_label_frame = ttk.Frame(main_frame)
		custom_label_frame.pack(fill=tk.X, pady=(8, 4))
		ttk.Label(custom_label_frame, text="Custom Observation (Optional):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT)
		
		custom_text_frame = ttk.Frame(main_frame)
		custom_text_frame.pack(fill=tk.BOTH, expand=True, pady=4)
		custom_text = tk.Text(custom_text_frame, height=6, width=60, wrap=tk.WORD, font=("Segoe UI", 9))
		custom_text.pack(fill=tk.BOTH, expand=True)
		custom_scroll = ttk.Scrollbar(custom_text_frame, orient=tk.VERTICAL, command=custom_text.yview)
		custom_scroll.pack(side=tk.RIGHT, fill=tk.Y)
		custom_text.config(yscrollcommand=custom_scroll.set)
		
		# Custom reputation change (optional)
		custom_rep_row = ttk.Frame(main_frame)
		custom_rep_row.pack(fill=tk.X, pady=8)
		ttk.Label(custom_rep_row, text="Reputation Change (Optional):", width=25, anchor=tk.W, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
		custom_rep_entry = ttk.Entry(custom_rep_row, width=15)
		custom_rep_entry.pack(side=tk.LEFT)
		ttk.Label(custom_rep_row, text="(-5 to +5)", font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT, padx=(8, 0))
		
		# Buttons
		btn_frame = ttk.Frame(dialog)
		btn_frame.pack(padx=20, pady=(10, 20))
		
		def submit():
			# Feet per minute
			fpm_val = fpm_entry.get().strip()
			if fpm_val:
				answers["touchdown_fpm"] = fpm_val
			
			# Departure timing
			dep_val = dep_entry.get().strip()
			if dep_val:
				answers["departure_timing"] = dep_val
			
			# Custom observation (optional)
			custom_obs = custom_text.get("1.0", tk.END).strip()
			if custom_obs:
				answers["custom_observation"] = custom_obs
			
			# Custom reputation change (optional)
			custom_rep_val = custom_rep_entry.get().strip()
			if custom_rep_val:
				answers["custom_rep_change"] = custom_rep_val
			
			# Always submit if we have at least touchdown or departure timing
			# Custom fields are optional and don't prevent submission
			dialog.destroy()
		
		def cancel():
			answers.clear()
			dialog.destroy()
		
		ttk.Button(btn_frame, text="Submit", command=submit).pack(side=tk.LEFT, padx=5)
		ttk.Button(btn_frame, text="Skip", command=cancel).pack(side=tk.LEFT, padx=5)
		
		dialog.wait_window()
		# Return answers if we have at least one field filled (touchdown or departure timing)
		# Custom fields are optional and don't prevent submission
		if answers and (answers.get("touchdown_fpm") or answers.get("departure_timing")):
			return answers
		return None
	
	def _on_view_weight_manifest(self):
		"""Display weight and balance manifest for selected flight."""
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Flights", "Select a flight to view weight manifest.")
			return
		vals = self.tree.item(item, "values")
		flt_id = vals[0]
		
		try:
			from services import get_flight_weight_manifest, list_active_flights, get_aircraft_weight_limits
			
			# Get the flight to get route and passenger info
			flights = list_active_flights()
			flight = next((f for f in flights if f.get("flight_id") == flt_id), None)
			
			if not flight:
				messagebox.showerror("Weight Manifest", "Flight not found.")
				return
			
			# Get weight manifest
			manifest = get_flight_weight_manifest(flt_id)
			
			if not manifest:
				messagebox.showinfo("Weight Manifest", "Weight manifest not available for this flight.")
				return
			
			# Check if weight limits are configured
			aircraft_id = flight.get("aircraft_id")
			weight_limits = get_aircraft_weight_limits(aircraft_id) if aircraft_id else {}
			empty_weight = weight_limits.get("empty_weight")
			max_zfw = weight_limits.get("max_zero_fuel_weight")
			
			# Show warning if limits not configured
			if empty_weight is None or max_zfw is None:
				warning_msg = "⚠️ WEIGHT LIMITS NOT CONFIGURED\n\n" \
					"This aircraft's weight limits have not been configured:\n" \
					"• Empty Weight\n" \
					"• Max Zero Fuel Weight\n" \
					"• Max Takeoff Weight (optional)\n\n" \
					"The weight manifest will still be displayed, but it cannot verify " \
					"that the flight is within safe weight limits.\n\n" \
					"Please configure weight limits in Fleet Manager → Configure Weight Limits " \
					"to ensure accurate weight and balance calculations."
				
				messagebox.showwarning("Weight Limits Not Configured", warning_msg)
			
			# Show manifest dialog
			self._show_weight_manifest_dialog(flight, manifest)
			
		except Exception as exc:
			messagebox.showerror("Weight Manifest", str(exc))
	
	def _show_weight_manifest_dialog(self, flight: Dict[str, Any], manifest: Dict[str, Any]):
		"""Display weight and balance manifest in a dialog."""
		dialog = tk.Toplevel(self)
		dialog.title("Weight and Balance Manifest")
		dialog.geometry("850x750")
		dialog.transient(self)
		dialog.grab_set()
		
		# Center the dialog
		dialog.update_idletasks()
		x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
		y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
		dialog.geometry(f"+{x}+{y}")
		
		# Title
		title_frame = ttk.Frame(dialog)
		title_frame.pack(padx=20, pady=(20, 10))
		ttk.Label(title_frame, text="Weight and Balance Manifest", font=("Segoe UI", 14, "bold")).pack()
		ttk.Label(title_frame, text=f"Flight: {flight.get('route', 'N/A')} | Aircraft: {flight.get('aircraft_id', 'N/A')}", 
			font=("Segoe UI", 9), foreground="#666").pack(pady=(4, 0))
		
		main_frame = ttk.Frame(dialog)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
		
		# Passenger weights table with scrollbar
		passengers_frame = ttk.LabelFrame(main_frame, text=f"Passenger Weights ({manifest.get('passenger_count', 0)} passengers)")
		passengers_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
		
		# Create scrollable container
		pass_container = ttk.Frame(passengers_frame)
		pass_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Create scrollbar
		pass_scrollbar = ttk.Scrollbar(pass_container, orient=tk.VERTICAL)
		pass_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		# Create treeview for passenger weights
		pass_cols = ("passenger", "weight")
		pass_tree = ttk.Treeview(pass_container, columns=pass_cols, show="headings", 
			yscrollcommand=pass_scrollbar.set, height=14)
		pass_tree.heading("passenger", text="Passenger #")
		pass_tree.heading("weight", text="Weight (lbs)")
		pass_tree.column("passenger", width=200, anchor=tk.CENTER)
		pass_tree.column("weight", width=200, anchor=tk.CENTER)
		
		# Configure scrollbar
		pass_scrollbar.config(command=pass_tree.yview)
		
		# Add passenger weights
		passenger_weights = manifest.get("passenger_weights", [])
		for pax in passenger_weights:
			pass_tree.insert("", tk.END, values=(
				f"Passenger {pax.get('passenger_num', 0)}",
				f"{pax.get('weight_lbs', 0.0):.1f}"
			))
		
		pass_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Cargo section
		cargo_frame = ttk.LabelFrame(main_frame, text="Cargo")
		cargo_frame.pack(fill=tk.X, pady=(0, 10))
		
		cargo_info = ttk.Frame(cargo_frame)
		cargo_info.pack(fill=tk.X, padx=10, pady=10)
		cargo_weight = manifest.get("cargo_weight", 0.0)
		ttk.Label(cargo_info, text=f"Cargo Weight: {cargo_weight:.1f} lbs", 
			font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
		
		# Totals section
		totals_frame = ttk.LabelFrame(main_frame, text="Weight Summary")
		totals_frame.pack(fill=tk.X)
		
		totals_info = ttk.Frame(totals_frame)
		totals_info.pack(fill=tk.X, padx=10, pady=10)
		
		total_passenger = manifest.get("total_passenger_weight", 0.0)
		total_cargo = manifest.get("cargo_weight", 0.0)
		empty_weight = manifest.get("empty_weight")
		zero_fuel_weight = manifest.get("zero_fuel_weight")
		max_zfw = manifest.get("max_zero_fuel_weight")
		max_mtow = manifest.get("max_takeoff_weight")
		within_limits = manifest.get("within_limits", True)
		
		# Create a grid for totals
		totals_grid = ttk.Frame(totals_info)
		totals_grid.pack(fill=tk.X)
		
		row = 0
		
		# Empty Weight - Always display
		ttk.Label(totals_grid, text="Empty Weight:", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=(0, 20))
		if empty_weight is not None:
			ttk.Label(totals_grid, text=f"{empty_weight:.1f} lbs", font=("Segoe UI", 10, "bold")).grid(row=row, column=1, sticky=tk.W)
		else:
			ttk.Label(totals_grid, text="Not configured", font=("Segoe UI", 10), foreground="#666").grid(row=row, column=1, sticky=tk.W)
		row += 1
		
		ttk.Label(totals_grid, text="Total Passenger Weight:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky=tk.W, padx=(0, 20), pady=(5, 0))
		ttk.Label(totals_grid, text=f"{total_passenger:.1f} lbs", font=("Segoe UI", 10, "bold")).grid(row=row, column=1, sticky=tk.W, pady=(5, 0))
		row += 1
		
		ttk.Label(totals_grid, text="Total Cargo Weight:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky=tk.W, padx=(0, 20), pady=(5, 0))
		ttk.Label(totals_grid, text=f"{total_cargo:.1f} lbs", font=("Segoe UI", 10, "bold")).grid(row=row, column=1, sticky=tk.W, pady=(5, 0))
		row += 1
		
		# Separator
		sep = ttk.Separator(totals_grid, orient=tk.HORIZONTAL)
		sep.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(10, 10))
		row += 1
		
		# Zero Fuel Weight - Always display
		ttk.Label(totals_grid, text="Zero Fuel Weight:", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, sticky=tk.W, padx=(0, 20))
		if zero_fuel_weight is not None:
			zfw_color = "#0a7f2e" if within_limits else "#b00020"
			ttk.Label(totals_grid, text=f"{zero_fuel_weight:.1f} lbs", font=("Segoe UI", 11, "bold"), foreground=zfw_color).grid(row=row, column=1, sticky=tk.W)
		else:
			# Calculate zero fuel weight if empty weight is available
			if empty_weight is not None:
				calculated_zfw = empty_weight + total_passenger + total_cargo
				ttk.Label(totals_grid, text=f"{calculated_zfw:.1f} lbs (calculated)", font=("Segoe UI", 11, "bold"), foreground="#666").grid(row=row, column=1, sticky=tk.W)
			else:
				ttk.Label(totals_grid, text="Not configured", font=("Segoe UI", 11), foreground="#666").grid(row=row, column=1, sticky=tk.W)
		row += 1
		
		# Show limit if configured
		if max_zfw is not None:
			limit_color = "#0a7f2e" if within_limits else "#b00020"
			status_text = "✓ Within Limits" if within_limits else "✗ EXCEEDS LIMIT"
			ttk.Label(totals_grid, text=f"Max Zero Fuel Weight: {max_zfw:.1f} lbs", 
				font=("Segoe UI", 9), foreground="#666").grid(row=row, column=0, sticky=tk.W, padx=(0, 20), pady=(2, 0))
			ttk.Label(totals_grid, text=status_text, font=("Segoe UI", 9, "bold"), 
				foreground=limit_color).grid(row=row, column=1, sticky=tk.W, pady=(2, 0))
			row += 1
		else:
			# Show warning if limits not configured
			ttk.Label(totals_grid, text="Max Zero Fuel Weight:", 
				font=("Segoe UI", 9), foreground="#666").grid(row=row, column=0, sticky=tk.W, padx=(0, 20), pady=(2, 0))
			ttk.Label(totals_grid, text="Not configured", font=("Segoe UI", 9), foreground="#ff9800").grid(row=row, column=1, sticky=tk.W, pady=(2, 0))
			row += 1
		
		# Show max takeoff weight if configured
		if max_mtow is not None:
			ttk.Label(totals_grid, text=f"Max Takeoff Weight: {max_mtow:.1f} lbs", 
				font=("Segoe UI", 9), foreground="#666").grid(row=row, column=0, sticky=tk.W, padx=(0, 20), pady=(5, 0))
			row += 1
		
		# Show warning if limits not configured
		if empty_weight is None or max_zfw is None:
			warning_frame = ttk.Frame(totals_frame)
			warning_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
			ttk.Label(warning_frame, text="⚠ Weight limits not fully configured for this aircraft. Configure in Fleet Manager → Configure Weight Limits.", 
				font=("Segoe UI", 8), foreground="#ff9800", wraplength=600).pack()
		
		# Close button
		btn_frame = ttk.Frame(dialog)
		btn_frame.pack(padx=20, pady=(10, 20))
		ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack()
		
		dialog.wait_window()
	
	def _on_end(self):
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Flights", "Select a flight to end.")
			return
		vals = self.tree.item(item, "values")
		flt_id = vals[0]
		try:
			from services import end_flight, get_company_reputation
			
			# Show flight quality questionnaire
			quality_answers = self._show_flight_quality_questionnaire(flt_id)
			
			# End the flight with quality answers
			res = end_flight(flt_id, quality_answers)
			self.refresh()
			
			# Refresh main menu to update reputation display (even if not visible)
			main_menu = self.controller.frames.get("MainMenuFrame")
			if main_menu:
				# Force update the reputation display
				try:
					from services import get_company_reputation
					reputation = get_company_reputation()
					rep_color = "#0a7f2e" if reputation >= 60 else "#ff9800" if reputation >= 40 else "#b00020"
					main_menu.reputation_var.set(f"Reputation: {reputation:.1f}/100")
					main_menu.reputation_label.config(foreground=rep_color)
				except Exception:
					# Fallback to full refresh if direct update fails
					main_menu.on_shown()
			
			reasons = res.get("reasons") or []
			reasons_txt = ("\n- " + "\n- ".join(reasons)) if reasons else "\n- none"
			loc = res.get("location") or "HOME"
			rel = res.get("reliability")
			g = res.get("grounded")
			pax_line = f"Pax: {res.get('pax_boarded', 0)} / {res.get('pax_requested', 0)} (baseline fare ~$ {res.get('baseline_price', 0):,})"
			hourly_cost = res.get('hourly_cost', 0)
			dur = res.get('duration_hours', 0)
			cost_line = f"Cost: $ {res['cost']:,} ({hourly_cost:,}/hr × {dur:.1f}hr)" if hourly_cost > 0 else f"Cost: $ {res['cost']:,}"
			comfort = res.get('cabin_comfort', 1.0)
			comfort_line = f"Cabin Comfort: {comfort:.2f} ⭐" if comfort else ""
			
			# Reputation info
			old_rep = res.get('old_reputation', 50.0)
			new_rep = res.get('new_reputation', old_rep)
			rep_change = res.get('reputation_change', 0.0)
			rep_bonus = res.get('reputation_bonus', 0)
			
			rep_line = ""
			if rep_change != 0:
				change_sign = "+" if rep_change > 0 else ""
				rep_line = f"\nReputation: {old_rep:.1f} → {new_rep:.1f} ({change_sign}{rep_change:.1f})"
			if rep_bonus != 0:
				rep_line += f"\nReputation Bonus: ${rep_bonus:,}"
			
			info_tail = f"\nLocation: {loc}\nReliability: {rel:.2f}" + (" (GROUNDED)" if g else "") if rel is not None else f"\nLocation: {loc}"
			
			# Add pilot info
			pilot_info = ""
			pilot_assigned = res.get("pilot_assigned")
			if pilot_assigned:
				pilot_info = f"\nPilot: {pilot_assigned}"
			
			# Add passenger feedback
			feedback_info = ""
			feedback = res.get("passenger_feedback")
			if feedback:
				feedback_type = feedback.get("feedback_type", "neutral")
				feedback_msg = feedback.get("message", "")
				feedback_icon = "⭐" if feedback_type == "excellent" else "✓" if feedback_type == "good" else "⚠" if feedback_type == "poor" else "•"
				feedback_info = f"\n\nPassenger Feedback: {feedback_icon} {feedback_msg}"
			
			# Add achievements
			achievement_info = ""
			new_achievements = res.get("new_achievements", [])
			if new_achievements:
				ach_names = [a.get("name", "") for a in new_achievements]
				achievement_info = f"\n\n🏆 Achievement Unlocked: {', '.join(ach_names)}"
				play_sound("achievement")  # Play achievement sound
			
			# Play success sound for completed flight (if profitable)
			if res.get('net', 0) > 0:
				play_sound("success")
			else:
				play_sound("notification")
			
			messagebox.showinfo(
				"Flight Ended",
				f"Revenue: $ {res['revenue']:,}\n{cost_line}\nPenalty: $ {res['penalty']:,}{rep_line}\nNet: $ {res['net']:,}\n{pax_line}\n{comfort_line}\nReasons:{reasons_txt}{pilot_info}{info_tail}{feedback_info}{achievement_info}"
			)
		except Exception as exc:
			messagebox.showerror("Flights", str(exc))
	
	def _on_cancel(self):
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Flights", "Select a flight to cancel.")
			return
		vals = self.tree.item(item, "values")
		flt_id = vals[0]
		route = vals[2]
		
		# Confirm cancellation
		confirm = messagebox.askyesno(
			"Cancel Flight",
			f"Cancel flight {flt_id} on route {route}?\n\n"
			"This will:\n"
			"• Refund passengers (10% processing fee)\n"
			"• Reduce reputation (disappointed customers)\n"
			"• Aircraft remains at origin"
		)
		if not confirm:
			return
		
		try:
			from services import cancel_flight, get_company_reputation
			
			# Cancel the flight
			res = cancel_flight(flt_id)
			self.refresh()
			
			# Refresh main menu to update reputation display
			main_menu = self.controller.frames.get("MainMenuFrame")
			if main_menu:
				try:
					reputation = get_company_reputation()
					main_menu.reputation_var.set(f"Reputation: {reputation:.1f}")
				except:
					pass
			
			# Show cancellation details
			old_rep = res.get('old_reputation', 50.0)
			new_rep = res.get('new_reputation', old_rep)
			rep_penalty = res.get('reputation_penalty', 0.0)
			refund_cost = res.get('refund_cost', 0)
			passengers = res.get('passengers', 0)
			
			rep_change_sign = "+" if rep_penalty > 0 else ""
			messagebox.showinfo(
				"Flight Cancelled",
				f"Flight {flt_id} has been cancelled.\n\n"
				f"Passengers refunded: {passengers}\n"
				f"Refund processing cost: ${refund_cost:,}\n"
				f"Reputation: {old_rep:.1f} → {new_rep:.1f} ({rep_change_sign}{rep_penalty:.1f})\n\n"
				"Aircraft remains at origin."
			)
		except Exception as exc:
			messagebox.showerror("Flights", str(exc))


class LoansFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Loans")

		# Top: Credit info
		credit_frame = ttk.LabelFrame(self, text="Credit Information")
		credit_frame.pack(fill=tk.X, padx=12, pady=8)
		self.max_credit_var = tk.StringVar(value="Max Credit: Calculating...")
		ttk.Label(credit_frame, textvariable=self.max_credit_var, font=("Segoe UI", 9, "bold")).pack(padx=8, pady=4)

		# Available loan offers
		offers_frame = ttk.LabelFrame(self, text="Available Loan Offers")
		offers_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		
		cols = ("bank", "max_amount", "rate", "term", "monthly", "description")
		self.offers_tree = ttk.Treeview(offers_frame, columns=cols, show="headings", height=14)
		for c, h in zip(cols, ["Bank", "Max Amount", "APR", "Term", "Monthly*", "Description"]):
			self.offers_tree.heading(c, text=h)
			if c == "description":
				self.offers_tree.column(c, width=300, anchor=tk.W)
			else:
				self.offers_tree.column(c, width=120, anchor=tk.W)
		self.offers_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
		self.offers_tree.tag_configure("best_rate", background="#e8f5e9")
		
		# Custom amount entry for selected offer
		custom_frame = ttk.Frame(offers_frame)
		custom_frame.pack(fill=tk.X, padx=8, pady=4)
		ttk.Label(custom_frame, text="Loan Amount $:", width=16).pack(side=tk.LEFT)
		self.loan_amount_var = tk.StringVar(value="")
		entry = ttk.Entry(custom_frame, textvariable=self.loan_amount_var, width=20)
		entry.pack(side=tk.LEFT, padx=(0, 8))
		ttk.Label(custom_frame, text="(Enter amount up to max)", font=("Segoe UI", 8), foreground="#666").pack(side=tk.LEFT)
		btn_take = ttk.Button(custom_frame, text="Take Selected Loan", command=wrap_command_with_sound(self._on_take))
		btn_take.pack(side=tk.LEFT, padx=8)
		btn_refresh = ttk.Button(custom_frame, text="Refresh Offers", command=self.refresh)
		btn_refresh.pack(side=tk.LEFT, padx=4)
		
		# Bind selection to update amount field
		self.offers_tree.bind("<<TreeviewSelect>>", self._on_offer_selected)

		# Current loans
		list_frame = ttk.LabelFrame(self, text="Current Loans")
		list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		cols = ("bank", "principal", "rate", "remaining", "payment")
		self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
		for c, h in zip(cols, ["Bank", "Principal", "APR", "Remaining", "Monthly"]):
			self.tree.heading(c, text=h)
			self.tree.column(c, width=140, anchor=tk.W)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

		repay_row = ttk.Frame(list_frame); repay_row.pack(fill=tk.X, padx=8, pady=4)
		self.repay_var = tk.StringVar(value="50000")
		ttk.Label(repay_row, text="Repay Amount $", width=16).pack(side=tk.LEFT)
		ttk.Entry(repay_row, textvariable=self.repay_var, width=16).pack(side=tk.LEFT)
		btn_repay = ttk.Button(repay_row, text="Repay Selected", command=wrap_command_with_sound(self._on_repay))
		btn_repay.pack(side=tk.LEFT, padx=8)

		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		try:
			from services import list_loans, calculate_max_loan_amount, get_available_loan_offers
			
			# Update credit info
			max_credit = calculate_max_loan_amount()
			existing_loans = list_loans()
			total_debt = sum(int(l.get("remaining_balance", 0)) for l in existing_loans)
			available = max_credit - total_debt
			self.max_credit_var.set(f"Max Credit: ${max_credit:,} | Available: ${available:,} | Current Debt: ${total_debt:,}")
			
			# Refresh loan offers
			offers = get_available_loan_offers()
			self.offers_tree.delete(*self.offers_tree.get_children())
			best_rate = None
			if offers:
				best_rate = offers[0]["interest_rate_apr"]
			for offer in offers:
				tag = "best_rate" if offer["interest_rate_apr"] == best_rate else ""
				vals = (
					offer.get("bank_name", "Unknown"),
					f"${offer.get('max_amount', 0):,}",
					f"{offer.get('interest_rate_apr', 0):.2%}",
					f"{offer.get('term_months', 0)} months",
					f"${offer.get('monthly_payment', 0):,}",
					offer.get("description", ""),
				)
				self.offers_tree.insert("", tk.END, values=vals, tags=(tag,))
			
			# Refresh current loans
			self.tree.delete(*self.tree.get_children())
			for loan in existing_loans:
				bank_name = loan.get("bank_name", "Unknown Bank")
				loan_id = loan.get("loan_id", "")
				vals = (
					bank_name,
					f"$ {loan.get('principal', 0):,}",
					f"{loan.get('interest_rate_apr', 0):.2%}",
					f"$ {loan.get('remaining_balance', 0):,}",
					f"$ {loan.get('monthly_payment', 0):,}",
				)
				self.tree.insert("", tk.END, values=vals, tags=(loan_id,))
		except Exception as exc:
			import traceback
			traceback.print_exc()

	def _on_offer_selected(self, event):
		"""Update loan amount field when an offer is selected."""
		item = self.offers_tree.selection()
		if not item:
			return
		vals = self.offers_tree.item(item[0], "values")
		if vals:
			max_amount_str = vals[1].replace("$", "").replace(",", "").strip()
			try:
				max_amount = int(max_amount_str)
				# Set to 80% of max as default
				default_amount = int(max_amount * 0.8)
				self.loan_amount_var.set(str(default_amount))
			except ValueError:
				pass

	def _on_take(self):
		item = self.offers_tree.selection()
		if not item:
			messagebox.showinfo("Loans", "Select a loan offer first.")
			return
		
		try:
			from services import take_loan, calculate_max_loan_amount, list_loans
			vals = self.offers_tree.item(item[0], "values")
			bank_name = vals[0]
			max_amount_str = vals[1].replace("$", "").replace(",", "").strip()
			rate_str = vals[2].replace("%", "").strip()
			term_str = vals[3].replace("months", "").strip()
			
			# Parse values
			max_amount = int(max_amount_str)
			rate = float(rate_str) / 100.0
			term = int(term_str)
			
			# Get loan amount from entry
			amount_str = self.loan_amount_var.get().replace(",", "").strip()
			if not amount_str:
				messagebox.showwarning("Loans", "Enter a loan amount.")
				return
			
			principal = int(amount_str)
			
			# Validate amount
			if principal <= 0:
				messagebox.showerror("Loans", "Loan amount must be positive.")
				return
			
			if principal > max_amount:
				messagebox.showerror("Loans", f"Loan amount exceeds maximum of ${max_amount:,}.")
				return
			
			# Check available credit
			max_credit = calculate_max_loan_amount()
			existing_loans = list_loans()
			total_debt = sum(int(l.get("remaining_balance", 0)) for l in existing_loans)
			available = max_credit - total_debt
			
			if principal > available:
				messagebox.showerror("Loans", f"Loan amount exceeds available credit of ${available:,}.")
				return
			
			take_loan(principal, rate, term, bank_name)
			self.refresh()
			self.loan_amount_var.set("")
			messagebox.showinfo("Loans", f"Loan of ${principal:,} taken from {bank_name}.")
		except ValueError as exc:
			messagebox.showerror("Loans", f"Invalid input: {exc}")
		except Exception as exc:
			messagebox.showerror("Loans", str(exc))

	def _on_repay(self):
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Loans", "Select a loan first.")
			return
		tags = self.tree.item(item, "tags")
		if not tags:
			messagebox.showerror("Loans", "Could not find loan ID.")
			return
		loan_id = tags[0]
		try:
			from services import repay_loan
			amount = int(self.repay_var.get().replace(",", ""))
			repay_loan(loan_id, amount)
			self.refresh()
			messagebox.showinfo("Loans", "Repayment successful.")
		except Exception as exc:
			messagebox.showerror("Loans", str(exc))


class PilotsFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Pilots")

		form = ttk.LabelFrame(self, text="Hire Pilot")
		form.pack(fill=tk.X, padx=12, pady=8)

		self.name_var = tk.StringVar()
		self.skill_var = tk.StringVar(value="")  # Empty = random
		self.salary_var = tk.StringVar(value="")  # Empty = random

		row = ttk.Frame(form); row.pack(fill=tk.X, padx=8, pady=4)
		ttk.Label(row, text="Name", width=12).pack(side=tk.LEFT)
		ttk.Entry(row, textvariable=self.name_var, width=25).pack(side=tk.LEFT, padx=(0, 12))
		ttk.Label(row, text="Skill (1-5, empty=random)", width=20).pack(side=tk.LEFT)
		ttk.Entry(row, textvariable=self.skill_var, width=8).pack(side=tk.LEFT, padx=(0, 12))
		ttk.Label(row, text="Salary $ (empty=random)", width=18).pack(side=tk.LEFT)
		ttk.Entry(row, textvariable=self.salary_var, width=12).pack(side=tk.LEFT)

		btns = ttk.Frame(form); btns.pack(fill=tk.X, padx=8, pady=4)
		btn_hire = ttk.Button(btns, text="Hire Pilot", command=wrap_command_with_sound(self._on_hire))
		btn_hire.pack(side=tk.LEFT)

		list_frame = ttk.LabelFrame(self, text="Pilots")
		list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		cols = ("name", "skill", "salary", "assigned", "revenue", "flights")
		self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=16)
		for c, h in zip(cols, ["Name", "Skill", "Salary/Day", "Assigned Aircraft", "Total Revenue", "Flights"]):
			self.tree.heading(c, text=h)
			self.tree.column(c, width=150, anchor=tk.W)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

		action_row = ttk.Frame(list_frame); action_row.pack(fill=tk.X, padx=8, pady=4)
		ttk.Label(action_row, text="Assign to Aircraft:", width=16, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
		self.ac_var = tk.StringVar()
		self.ac_combo = ttk.Combobox(action_row, textvariable=self.ac_var, width=30, state="readonly")
		self.ac_combo.pack(side=tk.LEFT, padx=(0, 8))
		btn_assign = ttk.Button(action_row, text="Assign", command=wrap_command_with_sound(self._on_assign))
		btn_assign.pack(side=tk.LEFT, padx=(0, 8))
		btn_unassign = ttk.Button(action_row, text="Unassign", command=wrap_command_with_sound(self._on_unassign))
		btn_unassign.pack(side=tk.LEFT, padx=(0, 8))
		btn_fire = ttk.Button(action_row, text="Fire Pilot", command=wrap_command_with_sound(self._on_fire))
		btn_fire.pack(side=tk.LEFT)

		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		try:
			from services import list_pilots, list_fleet
			self.tree.delete(*self.tree.get_children())
			for pilot in list_pilots():
				ac_id = pilot.get("assigned_aircraft_id")
				ac_name = "Unassigned"
				if ac_id:
					fleet = list_fleet()
					ac = next((a for a in fleet if a.get("id") == ac_id), None)
					if ac:
						ac_name = f"{ac.get('id')} - {ac.get('name')}"
				
				vals = (
					pilot.get("name"),
					f"⭐ {pilot.get('skill_level', 1)}",
					f"$ {pilot.get('salary', 0):,}",
					ac_name,
					f"$ {pilot.get('total_revenue', 0):,}",
					str(pilot.get("total_flights", 0)),
				)
				self.tree.insert("", tk.END, values=vals, tags=(pilot.get("pilot_id"),))
			
			# Update aircraft combo
			fleet = list_fleet()
			choices = ["None (Unassign)"] + [f"{ac['id']} - {ac['name']}" for ac in fleet]
			self.ac_combo["values"] = choices
			if choices and not self.ac_var.get():
				self.ac_var.set(choices[0])
		except Exception:
			pass

	def _on_hire(self):
		try:
			from services import hire_pilot
			name = self.name_var.get().strip()
			if not name:
				messagebox.showwarning("Pilots", "Enter pilot name.")
				return
			skill = None
			if self.skill_var.get().strip():
				skill = int(self.skill_var.get())
				if skill < 1 or skill > 5:
					raise ValueError("Skill must be 1-5")
			salary = None
			if self.salary_var.get().strip():
				salary = int(self.salary_var.get().replace(",", ""))
			hire_pilot(name, skill, salary)
			self.name_var.set("")
			self.skill_var.set("")
			self.salary_var.set("")
			self.refresh()
			messagebox.showinfo("Pilots", f"Pilot {name} hired.")
		except Exception as exc:
			messagebox.showerror("Pilots", str(exc))

	def _on_assign(self):
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Pilots", "Select a pilot first.")
			return
		pilot_id = self.tree.item(item, "tags")[0]
		ac_choice = self.ac_var.get()
		if ac_choice == "None (Unassign)":
			aircraft_id = None
		else:
			if " - " not in ac_choice:
				messagebox.showwarning("Pilots", "Select an aircraft.")
				return
			aircraft_id = ac_choice.split(" - ", 1)[0]
		try:
			from services import assign_pilot_to_aircraft
			assign_pilot_to_aircraft(pilot_id, aircraft_id)
			self.refresh()
			messagebox.showinfo("Pilots", "Pilot assigned.")
		except Exception as exc:
			messagebox.showerror("Pilots", str(exc))

	def _on_unassign(self):
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Pilots", "Select a pilot first.")
			return
		pilot_id = self.tree.item(item, "tags")[0]
		try:
			from services import assign_pilot_to_aircraft
			assign_pilot_to_aircraft(pilot_id, None)
			self.refresh()
			messagebox.showinfo("Pilots", "Pilot unassigned.")
		except Exception as exc:
			messagebox.showerror("Pilots", str(exc))

	def _on_fire(self):
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Pilots", "Select a pilot first.")
			return
		pilot_id = self.tree.item(item, "tags")[0]
		vals = self.tree.item(item, "values")
		name = vals[0]
		if not messagebox.askyesno("Pilots", f"Fire pilot {name}?"):
			return
		try:
			from services import fire_pilot
			fire_pilot(pilot_id)
			self.refresh()
			messagebox.showinfo("Pilots", "Pilot fired.")
		except Exception as exc:
			messagebox.showerror("Pilots", str(exc))


class ReportsFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Reports")

		# Top filters and KPIs
		controls = ttk.Frame(self)
		controls.pack(fill=tk.X, padx=12, pady=8)
		self.period_var = tk.StringVar(value="30d")
		ttk.Label(controls, text="Period:").pack(side=tk.LEFT)
		self.period_combo = ttk.Combobox(controls, textvariable=self.period_var, width=10, state="readonly")
		self.period_combo["values"] = ("All", "Today", "7d", "30d", "90d")
		self.period_combo.pack(side=tk.LEFT, padx=(4, 12))
		self.period_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())
		btn_refresh = ttk.Button(controls, text="Refresh", command=wrap_command_with_sound(self.refresh))
		btn_refresh.pack(side=tk.LEFT)

		kpis = ttk.Frame(self)
		kpis.pack(fill=tk.X, padx=12)
		self.kpi_cash = tk.StringVar(value="$ 0")
		self.kpi_income = tk.StringVar(value="$ 0")
		self.kpi_expense = tk.StringVar(value="$ 0")
		self.kpi_net = tk.StringVar(value="$ 0")
		for label, var in [("Cash", self.kpi_cash), ("Income", self.kpi_income), ("Expenses", self.kpi_expense), ("Net", self.kpi_net)]:
			box = ttk.LabelFrame(kpis, text=label)
			box.pack(side=tk.LEFT, padx=8, pady=6)
			lbl = ttk.Label(box, textvariable=var, font=("Segoe UI", 12, "bold"))
			lbl.pack(padx=12, pady=8)

		# Category breakdown
		breakdown = ttk.LabelFrame(self, text="By Category")
		breakdown.pack(fill=tk.X, padx=12, pady=6)
		self.break_cols = ("type", "total")
		self.break_tree = ttk.Treeview(breakdown, columns=self.break_cols, show="headings", height=10)
		for c, h in zip(self.break_cols, ["Type", "Total"]):
			self.break_tree.heading(c, text=h)
			self.break_tree.column(c, width=200, anchor=tk.W)
		self.break_tree.pack(fill=tk.X, padx=8, pady=6)

		# Route profitability
		route_profit = ttk.LabelFrame(self, text="Route Profitability (Last 30 Days)")
		route_profit.pack(fill=tk.X, padx=12, pady=6)
		self.route_cols = ("route", "flights", "revenue", "cost", "net", "load_factor")
		self.route_tree = ttk.Treeview(route_profit, columns=self.route_cols, show="headings", height=10)
		for c, h in zip(self.route_cols, ["Route", "Flights", "Revenue", "Cost", "Net", "Load %"]):
			self.route_tree.heading(c, text=h)
			self.route_tree.column(c, width=100, anchor=tk.W)
		self.route_tree.pack(fill=tk.X, padx=8, pady=6)
		self.route_tree.tag_configure("profit", foreground="#0a7f2e")
		self.route_tree.tag_configure("loss", foreground="#b00020")

		# Ledger detail
		detail = ttk.LabelFrame(self, text="Ledger")
		detail.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
		cols = ("ts", "type", "amount", "note")
		self.tree = ttk.Treeview(detail, columns=cols, show="headings", height=18)
		for c, h in zip(cols, ["Time", "Type", "Amount", "Note"]):
			self.tree.heading(c, text=h)
			self.tree.column(c, width=160 if c != "note" else 400, anchor=tk.W)
		self.tree.tag_configure("pos", foreground="#0a7f2e")
		self.tree.tag_configure("neg", foreground="#b00020")
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		try:
			from storage import load_state
			import time
			state = load_state()
			cash = state.get("cash", 0)
			entries = state.get("ledger", [])
			# Filter by period
			period = (self.period_var.get() or "All").lower()
			now = int(time.time())
			if period == "today":
				start = (now // 86400) * 86400
				entries = [e for e in entries if int(e.get("ts", 0)) >= start]
			elif period.endswith("d") and period[:-1].isdigit():
				days = int(period[:-1])
				start = now - days * 86400
				entries = [e for e in entries if int(e.get("ts", 0)) >= start]

			# KPIs
			income = sum(e.get("amount", 0) for e in entries if int(e.get("amount", 0)) > 0)
			expense = sum(e.get("amount", 0) for e in entries if int(e.get("amount", 0)) < 0)
			net = income + expense
			self.kpi_cash.set(f"$ {cash:,}")
			self.kpi_income.set(f"$ {income:,}")
			self.kpi_expense.set(f"$ {abs(expense):,}")
			self.kpi_net.set(f"$ {net:,}")

			# Breakdown by type
			self.break_tree.delete(*self.break_tree.get_children())
			totals = {}
			for e in entries:
				etype = e.get("type", "other")
				totals[etype] = totals.get(etype, 0) + int(e.get("amount", 0))
			for etype, amt in sorted(totals.items(), key=lambda x: -abs(x[1])):
				self.break_tree.insert("", tk.END, values=(etype, f"$ {amt:,}"))

			# Route profitability
			try:
				from services import get_route_profitability_stats
				route_stats = get_route_profitability_stats(30)
				self.route_tree.delete(*self.route_tree.get_children())
				for stat in route_stats:
					net = stat.get("net", 0)
					tag = "profit" if net >= 0 else "loss"
					self.route_tree.insert("", tk.END, values=(
						stat.get("route", "UNKNOWN"),
						stat.get("flights", 0),
						f"$ {stat.get('revenue', 0):,}",
						f"$ {stat.get('cost', 0):,}",
						f"$ {net:,}",
						f"{stat.get('avg_load_factor', 0):.1f}%",
					), tags=(tag,))
			except Exception:
				pass

			# Ledger detail
			self.tree.delete(*self.tree.get_children())
			for e in reversed(entries[-1000:]):
				ts = time.strftime('%Y-%m-%d %H:%M', time.localtime(e.get("ts", 0)))
				amt = int(e.get("amount", 0))
				tag = "pos" if amt >= 0 else "neg"
				vals = (ts, e.get("type"), f"$ {amt:,}", e.get("note", ""))
				self.tree.insert("", tk.END, values=vals, tags=(tag,))
		except Exception:
			pass


class CabinConfigFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Cabin Configuration")
		self.current_aircraft_id = None
		self.layout = []

		# Top header: Aircraft selection and info
		top = ttk.Frame(self)
		top.pack(fill=tk.X, padx=12, pady=8)
		ttk.Label(top, text="Aircraft:", width=10, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
		self.ac_var = tk.StringVar()
		self.ac_combo = ttk.Combobox(top, textvariable=self.ac_var, width=35, state="readonly")
		self.ac_combo.pack(side=tk.LEFT, padx=(0, 12))
		self.ac_combo.bind("<<ComboboxSelected>>", lambda e: self._on_aircraft_selected())
		
		# Inline info display
		self.cost_var = tk.StringVar(value="Cost: $0")
		self.comfort_var = tk.StringVar(value="Comfort: 1.00 ⭐")
		self.limits_var = tk.StringVar(value="Limits: -")
		ttk.Label(top, textvariable=self.cost_var, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)
		ttk.Label(top, textvariable=self.comfort_var, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)
		ttk.Label(top, textvariable=self.limits_var, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)

		# Main content area: split into left (map) and right (controls)
		main = ttk.Frame(self)
		main.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
		
		# Left side: Visual seat map (larger)
		map_frame = ttk.LabelFrame(main, text="Cabin Layout")
		map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
		canvas_container = ttk.Frame(map_frame)
		canvas_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
		self.map_canvas = tk.Canvas(canvas_container, bg="#ffffff")
		scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.map_canvas.yview)
		self.map_canvas.configure(yscrollcommand=scrollbar.set)
		self.map_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		# Enable mouse wheel scrolling
		def _on_mousewheel(event):
			self.map_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
		self.map_canvas.bind("<MouseWheel>", _on_mousewheel)

		# Right side: Controls panel (fixed width, organized vertically)
		controls_panel = ttk.Frame(main)
		controls_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))
		controls_panel.config(width=280)

		# Add Rows section
		add_section = ttk.LabelFrame(controls_panel, text="Add Rows")
		add_section.pack(fill=tk.X, pady=(0, 6))
		row1 = ttk.Frame(add_section); row1.pack(fill=tk.X, padx=6, pady=4)
		ttk.Label(row1, text="Rows:", width=8).pack(side=tk.LEFT)
		self.row_var = tk.StringVar(value="1")
		self.row_spin = ttk.Spinbox(row1, from_=1, to=100, textvariable=self.row_var, width=8)
		self.row_spin.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
		row2 = ttk.Frame(add_section); row2.pack(fill=tk.X, padx=6, pady=4)
		ttk.Label(row2, text="Seat Type:", width=8).pack(side=tk.LEFT)
		self.seat_type_var = tk.StringVar()
		self.seat_type_combo = ttk.Combobox(row2, textvariable=self.seat_type_var, width=18, state="readonly")
		self.seat_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
		row3 = ttk.Frame(add_section); row3.pack(fill=tk.X, padx=6, pady=4)
		ttk.Label(row3, text="Seats/Row:", width=8).pack(side=tk.LEFT)
		self.seats_var = tk.StringVar(value="6")
		self.seats_spin = ttk.Spinbox(row3, from_=1, to=10, textvariable=self.seats_var, width=8)
		self.seats_spin.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
		row4 = ttk.Frame(add_section); row4.pack(fill=tk.X, padx=6, pady=6)
		ttk.Button(row4, text="Add Rows", command=wrap_command_with_sound(self._on_add_row)).pack(fill=tk.X)

		# Update Row section
		update_section = ttk.LabelFrame(controls_panel, text="Update Row")
		update_section.pack(fill=tk.X, pady=(0, 6))
		row5 = ttk.Frame(update_section); row5.pack(fill=tk.X, padx=6, pady=4)
		ttk.Label(row5, text="Row #:", width=8).pack(side=tk.LEFT)
		self.update_row_var = tk.StringVar(value="1")
		ttk.Spinbox(row5, from_=1, to=100, textvariable=self.update_row_var, width=8).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
		row6 = ttk.Frame(update_section); row6.pack(fill=tk.X, padx=6, pady=6)
		ttk.Button(row6, text="Update Row", command=wrap_command_with_sound(self._on_update_row)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
		ttk.Button(row6, text="Remove Row", command=wrap_command_with_sound(self._on_remove_row)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

		# Action buttons section
		action_section = ttk.LabelFrame(controls_panel, text="Actions")
		action_section.pack(fill=tk.X, pady=(0, 6))
		ttk.Button(action_section, text="Save Configuration", command=self._on_save).pack(fill=tk.X, padx=6, pady=4)
		ttk.Button(action_section, text="Reset to Default", command=self._on_reset).pack(fill=tk.X, padx=6, pady=2)
		ttk.Button(action_section, text="Clear All", command=self._on_clear_all).pack(fill=tk.X, padx=6, pady=2)
		ttk.Button(action_section, text="Override Limits", command=self._on_override_limits).pack(fill=tk.X, padx=6, pady=(2, 6))

		self.bind("<<FrameShown>>", lambda e: self.refresh())

	def refresh(self):
		try:
			from services import list_fleet
			from seat_types import get_seat_types
			fleet = list_fleet()
			choices = [f"{ac['id']} - {ac['name']} ({ac['type_code']})" for ac in fleet]
			self.ac_combo["values"] = choices
			if choices and not self.ac_var.get():
				self.ac_var.set(choices[0])
				self._on_aircraft_selected()
			seat_types = get_seat_types()
			self.seat_type_combo["values"] = [f"{st['code']} - {st['name']}" for st in seat_types]
			if not self.seat_type_var.get() and seat_types:
				self.seat_type_var.set(f"{seat_types[0]['code']} - {seat_types[0]['name']}")
		except Exception:
			pass

	def _on_aircraft_selected(self):
		label = self.ac_var.get()
		if " - " not in label:
			return
		ac_id = label.split(" - ", 1)[0]
		self.current_aircraft_id = ac_id
		try:
			from services import list_fleet, get_aircraft_cabin_limits
			fleet = list_fleet()
			ac = next((x for x in fleet if x.get("id") == ac_id), None)
			if ac:
				self.layout = list(ac.get("cabin_layout", []))
				# Update limits and spinboxes
				limits = get_aircraft_cabin_limits(ac_id)
				self.row_spin.config(to=limits["max_rows"])
				self.seats_spin.config(to=limits["max_seats_per_row"])
				self.limits_var.set(f"Limits: Max {limits['max_seats_per_row']} seats/row, {limits['max_rows']} rows")
				self._update_display()
		except Exception:
			pass

	def _update_display(self):
		from seat_types import calculate_cabin_cost, calculate_cabin_comfort, get_seat_types
		cost = calculate_cabin_cost(self.layout)
		comfort = calculate_cabin_comfort(self.layout)
		self.cost_var.set(f"Cost: ${cost:,}")
		self.comfort_var.set(f"Comfort: {comfort:.2f} ⭐")
		self._draw_seat_map()

	def _draw_seat_map(self):
		self.map_canvas.delete("all")
		if not self.layout:
			self.map_canvas.create_text(200, 150, text="No cabin layout configured", fill="#666666")
			self.map_canvas.configure(scrollregion=self.map_canvas.bbox("all"))
			return
		from seat_types import get_seat_types
		seat_types = {st["code"]: st for st in get_seat_types()}
		y = 20
		row_height = 25
		for row in self.layout:
			row_num = row.get("row", 0)
			seat_code = row.get("seat_type", "SLIM")
			seats = int(row.get("seats", 6))
			st = seat_types.get(seat_code, seat_types["SLIM"])
			color = st.get("color", "#e0e0e0")
			x = 20
			# Draw row label
			self.map_canvas.create_text(x, y + row_height/2, text=f"Row {row_num}", anchor="w", font=("Segoe UI", 9))
			x += 60
			# Draw seats
			for i in range(seats):
				self.map_canvas.create_rectangle(x, y, x + 25, y + row_height - 4, fill=color, outline="black", width=1)
				x += 27
			# Draw seat type label
			self.map_canvas.create_text(x + 10, y + row_height/2, text=st["name"], anchor="w", font=("Segoe UI", 9))
			y += row_height + 2
		# Update scroll region to include all content
		self.map_canvas.configure(scrollregion=self.map_canvas.bbox("all"))

	def _on_update_row(self):
		if not self.current_aircraft_id:
			messagebox.showinfo("Cabin", "Select an aircraft first.")
			return
		try:
			from services import get_aircraft_cabin_limits
			limits = get_aircraft_cabin_limits(self.current_aircraft_id)
			row_num = int(self.update_row_var.get())
			seat_type_str = self.seat_type_var.get()
			if " - " not in seat_type_str:
				messagebox.showwarning("Cabin", "Select a seat type.")
				return
			seat_code = seat_type_str.split(" - ", 1)[0]
			seats = int(self.seats_var.get())
			# Validate limits
			if seats > limits["max_seats_per_row"]:
				messagebox.showerror("Cabin", f"Too many seats per row ({seats}). Maximum is {limits['max_seats_per_row']}.")
				return
			if len(self.layout) >= limits["max_rows"] and row_num not in [r.get("row") for r in self.layout]:
				messagebox.showerror("Cabin", f"Too many rows. Maximum is {limits['max_rows']} rows.")
				return
			# Find and update row
			found = False
			for row in self.layout:
				if row.get("row") == row_num:
					row["seat_type"] = seat_code
					row["seats"] = seats
					found = True
					break
			if not found:
				self.layout.append({"row": row_num, "seat_type": seat_code, "seats": seats})
			# Sort by row number
			self.layout.sort(key=lambda r: r.get("row", 0))
			self._update_display()
		except Exception as exc:
			messagebox.showerror("Cabin", str(exc))

	def _on_add_row(self):
		if not self.current_aircraft_id:
			messagebox.showinfo("Cabin", "Select an aircraft first.")
			return
		try:
			from services import get_aircraft_cabin_limits
			limits = get_aircraft_cabin_limits(self.current_aircraft_id)
			num_rows_to_add = int(self.row_var.get())
			if num_rows_to_add <= 0:
				messagebox.showwarning("Cabin", "Number of rows must be positive.")
				return
			seat_type_str = self.seat_type_var.get()
			if " - " not in seat_type_str:
				messagebox.showwarning("Cabin", "Select a seat type.")
				return
			seat_code = seat_type_str.split(" - ", 1)[0]
			seats = int(self.seats_var.get())
			# Validate limits
			if seats > limits["max_seats_per_row"]:
				messagebox.showerror("Cabin", f"Too many seats per row ({seats}). Maximum is {limits['max_seats_per_row']}.")
				return
			# Find starting row number
			if not self.layout:
				start_row = 1
			else:
				start_row = max(r.get("row", 0) for r in self.layout) + 1
			# Check if adding these rows would exceed max
			if len(self.layout) + num_rows_to_add > limits["max_rows"]:
				messagebox.showerror("Cabin", f"Adding {num_rows_to_add} rows would exceed maximum of {limits['max_rows']} rows.")
				return
			# Create the rows
			for i in range(num_rows_to_add):
				self.layout.append({"row": start_row + i, "seat_type": seat_code, "seats": seats})
			# Sort by row number
			self.layout.sort(key=lambda r: r.get("row", 0))
			self._update_display()
		except Exception as exc:
			messagebox.showerror("Cabin", str(exc))

	def _on_remove_row(self):
		if not self.current_aircraft_id:
			return
		try:
			row_num = int(self.update_row_var.get())
			self.layout = [r for r in self.layout if r.get("row") != row_num]
			self._update_display()
		except Exception:
			pass

	def _on_reset(self):
		if not self.current_aircraft_id:
			return
		if messagebox.askyesno("Reset", "Reset cabin layout to default?"):
			try:
				from services import list_fleet, get_aircraft_cabin_limits
				from catalog import aircraft_catalog
				from seat_types import get_default_layout
				fleet = list_fleet()
				ac = next((x for x in fleet if x.get("id") == self.current_aircraft_id), None)
				if ac:
					cat = {c["type_code"]: c for c in aircraft_catalog()}
					info = cat.get(ac.get("type_code"))
					capacity = int(info.get("capacity", 150)) if info else 150
					limits = get_aircraft_cabin_limits(self.current_aircraft_id)
					self.layout = get_default_layout(capacity, limits["max_seats_per_row"], limits["max_rows"])
					self._update_display()
			except Exception as exc:
				messagebox.showerror("Cabin", str(exc))

	def _on_clear_all(self):
		if not self.current_aircraft_id:
			messagebox.showinfo("Cabin", "Select an aircraft first.")
			return
		if messagebox.askyesno("Clear All", "Clear entire cabin layout? This will remove all rows."):
			self.layout = []
			self._update_display()

	def _on_override_limits(self):
		if not self.current_aircraft_id:
			messagebox.showinfo("Cabin", "Select an aircraft first.")
			return
		try:
			from services import list_fleet, get_aircraft_cabin_limits, set_aircraft_cabin_limits
			fleet = list_fleet()
			ac = next((x for x in fleet if x.get("id") == self.current_aircraft_id), None)
			if not ac:
				return
			type_code = ac.get("type_code")
			current = get_aircraft_cabin_limits(self.current_aircraft_id)
			# Create dialog
			dialog = tk.Toplevel(self)
			dialog.title("Override Cabin Limits")
			dialog.geometry("450x250")
			ttk.Label(dialog, text=f"Override limits for {type_code}").pack(pady=8)
			ttk.Label(dialog, text=f"Current: {current['max_seats_per_row']} seats/row, {current['max_rows']} rows").pack()
			row1 = ttk.Frame(dialog)
			row1.pack(pady=8)
			ttk.Label(row1, text="Max Seats/Row:").pack(side=tk.LEFT, padx=4)
			seats_var = tk.StringVar(value=str(current["max_seats_per_row"]))
			ttk.Spinbox(row1, from_=1, to=20, textvariable=seats_var, width=8).pack(side=tk.LEFT, padx=4)
			row2 = ttk.Frame(dialog)
			row2.pack(pady=8)
			ttk.Label(row2, text="Max Rows:").pack(side=tk.LEFT, padx=4)
			rows_var = tk.StringVar(value=str(current["max_rows"]))
			ttk.Spinbox(row2, from_=1, to=100, textvariable=rows_var, width=8).pack(side=tk.LEFT, padx=4)
			btns = ttk.Frame(dialog)
			btns.pack(pady=8)
			def save_override():
				set_aircraft_cabin_limits(type_code, int(seats_var.get()), int(rows_var.get()))
				dialog.destroy()
				self._on_aircraft_selected()  # Refresh limits
				messagebox.showinfo("Cabin", "Limits updated.")
			ttk.Button(btns, text="Save", command=save_override).pack(side=tk.LEFT, padx=4)
			ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=4)
		except Exception as exc:
			messagebox.showerror("Cabin", str(exc))

	def _on_save(self):
		if not self.current_aircraft_id:
			messagebox.showinfo("Cabin", "Select an aircraft first.")
			return
		try:
			from services import configure_aircraft_cabin
			configure_aircraft_cabin(self.current_aircraft_id, self.layout)
			messagebox.showinfo("Cabin", "Cabin configuration saved.")
			self._update_display()
		except Exception as exc:
			messagebox.showerror("Cabin", str(exc))


class AirportServicesFrame(BaseFrame):

	def __init__(self, parent, controller):
		super().__init__(parent, controller)
		self.title_var.set("Airport Services")
		
		# Top: Aircraft selection with better styling
		top_frame = ttk.LabelFrame(self, text="Select Aircraft")
		top_frame.pack(fill=tk.X, padx=16, pady=10)
		
		selection_row = ttk.Frame(top_frame)
		selection_row.pack(fill=tk.X, padx=12, pady=10)
		
		ttk.Label(selection_row, text="Aircraft:", font=("Segoe UI", 10, "bold"), width=10).pack(side=tk.LEFT)
		self.ac_var = tk.StringVar()
		self.ac_combo = ttk.Combobox(selection_row, textvariable=self.ac_var, width=45, state="readonly", font=("Segoe UI", 9))
		self.ac_combo.pack(side=tk.LEFT, padx=(8, 16))
		self.ac_combo.bind("<<ComboboxSelected>>", lambda e: self._on_aircraft_selected())
		
		# Show aircraft location with icon
		location_container = ttk.Frame(selection_row)
		location_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
		ttk.Label(location_container, text="📍", font=("Segoe UI", 10)).pack(side=tk.LEFT)
		self.location_var = tk.StringVar(value="Location: -")
		ttk.Label(location_container, textvariable=self.location_var, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 0))
		
		# Main content: Services in a grid layout
		main_container = ttk.Frame(self)
		main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
		
		# Left: Services list with better styling
		services_frame = ttk.LabelFrame(main_container, text="Available Services")
		services_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
		
		# Create a scrollable frame for services
		canvas_container = ttk.Frame(services_frame)
		canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		scrollbar = ttk.Scrollbar(canvas_container, orient="vertical")
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		self.services_canvas = tk.Canvas(canvas_container, yscrollcommand=scrollbar.set, bg="#f5f5f5", highlightthickness=0)
		self.services_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.config(command=self.services_canvas.yview)
		
		# Frame inside canvas for services
		self.services_inner_frame = ttk.Frame(self.services_canvas)
		self.services_canvas_window = self.services_canvas.create_window((0, 0), window=self.services_inner_frame, anchor="nw")
		
		# Bind canvas scrolling
		def _configure_canvas(event):
			self.services_canvas.configure(scrollregion=self.services_canvas.bbox("all"))
			canvas_width = event.width
			self.services_canvas.itemconfig(self.services_canvas_window, width=canvas_width)
		self.services_canvas.bind("<Configure>", _configure_canvas)
		
		def _on_mousewheel(event):
			self.services_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
		self.services_canvas.bind("<MouseWheel>", _on_mousewheel)
		
		# Right: Recent services display in a nice panel
		recent_frame = ttk.LabelFrame(main_container, text="Recent Services")
		recent_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
		recent_frame.config(width=300)
		
		recent_inner = ttk.Frame(recent_frame)
		recent_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		self.recent_var = tk.StringVar(value="Select an aircraft to see recent services")
		recent_label = ttk.Label(recent_inner, textvariable=self.recent_var, font=("Segoe UI", 9), 
			wraplength=280, justify=tk.LEFT, foreground="#444")
		recent_label.pack(anchor=tk.W, pady=4)
		
		# Store fuel input variables for refueling service
		self.fuel_vars = {}
		
		# Custom Items Section - below main container
		custom_items_container = ttk.Frame(self)
		custom_items_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 16))
		
		# Left: Purchase custom item
		purchase_frame = ttk.LabelFrame(custom_items_container, text="Purchase Custom Item")
		purchase_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
		
		purchase_inner = ttk.Frame(purchase_frame)
		purchase_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
		
		# Airport selection for purchase
		ttk.Label(purchase_inner, text="Airport:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
		self.purchase_airport_var = tk.StringVar()
		self.purchase_airport_entry = ttk.Entry(purchase_inner, textvariable=self.purchase_airport_var, width=20, font=("Segoe UI", 9))
		self.purchase_airport_entry.pack(fill=tk.X, pady=(0, 8))
		
		# Item name
		ttk.Label(purchase_inner, text="Item Name:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
		self.item_name_var = tk.StringVar()
		self.item_name_entry = ttk.Entry(purchase_inner, textvariable=self.item_name_var, width=20, font=("Segoe UI", 9))
		self.item_name_entry.pack(fill=tk.X, pady=(0, 8))
		
		# Item cost
		ttk.Label(purchase_inner, text="Cost ($):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
		self.item_cost_var = tk.StringVar(value="1000")
		self.item_cost_entry = ttk.Entry(purchase_inner, textvariable=self.item_cost_var, width=20, font=("Segoe UI", 9))
		self.item_cost_entry.pack(fill=tk.X, pady=(0, 12))
		
		# Purchase button
		btn_purchase_item = ttk.Button(purchase_inner, text="Purchase Custom Item", command=self._on_purchase_custom_item)
		btn_purchase_item.pack(fill=tk.X, pady=(0, 8))
		
		ttk.Label(purchase_inner, text="Note: Requires hangar at airport", font=("Segoe UI", 8), foreground="#666").pack(anchor=tk.W)
		
		# Middle: Stored custom items
		stored_frame = ttk.LabelFrame(custom_items_container, text="Stored Custom Items")
		stored_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
		
		# Scrollable frame for stored items
		stored_canvas_container = ttk.Frame(stored_frame)
		stored_canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		stored_scrollbar = ttk.Scrollbar(stored_canvas_container, orient="vertical")
		stored_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		self.stored_canvas = tk.Canvas(stored_canvas_container, yscrollcommand=stored_scrollbar.set, bg="#f5f5f5", highlightthickness=0)
		self.stored_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		stored_scrollbar.config(command=self.stored_canvas.yview)
		
		self.stored_inner_frame = ttk.Frame(self.stored_canvas)
		self.stored_canvas_window = self.stored_canvas.create_window((0, 0), window=self.stored_inner_frame, anchor="nw")
		
		def _configure_stored_canvas(event):
			self.stored_canvas.configure(scrollregion=self.stored_canvas.bbox("all"))
			canvas_width = event.width
			self.stored_canvas.itemconfig(self.stored_canvas_window, width=canvas_width)
		self.stored_canvas.bind("<Configure>", _configure_stored_canvas)
		
		def _on_stored_mousewheel(event):
			self.stored_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
		self.stored_canvas.bind("<MouseWheel>", _on_stored_mousewheel)
		
		# Right: Install custom items
		install_frame = ttk.LabelFrame(custom_items_container, text="Install Custom Item")
		install_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Scrollable frame for installable items
		install_canvas_container = ttk.Frame(install_frame)
		install_canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		install_scrollbar = ttk.Scrollbar(install_canvas_container, orient="vertical")
		install_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		self.install_canvas = tk.Canvas(install_canvas_container, yscrollcommand=install_scrollbar.set, bg="#f5f5f5", highlightthickness=0)
		self.install_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		install_scrollbar.config(command=self.install_canvas.yview)
		
		self.install_inner_frame = ttk.Frame(self.install_canvas)
		self.install_canvas_window = self.install_canvas.create_window((0, 0), window=self.install_inner_frame, anchor="nw")
		
		def _configure_install_canvas(event):
			self.install_canvas.configure(scrollregion=self.install_canvas.bbox("all"))
			canvas_width = event.width
			self.install_canvas.itemconfig(self.install_canvas_window, width=canvas_width)
		self.install_canvas.bind("<Configure>", _configure_install_canvas)
		
		def _on_install_mousewheel(event):
			self.install_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
		self.install_canvas.bind("<MouseWheel>", _on_install_mousewheel)
		
		self.bind("<<FrameShown>>", lambda e: self.refresh())
	
	def refresh(self):
		# Clear existing service widgets and fuel variables
		for widget in self.services_inner_frame.winfo_children():
			widget.destroy()
		self.fuel_vars.clear()
		
		try:
			from services import list_fleet, list_airport_services, get_aircraft_services
			from catalog import aircraft_catalog
			import time
			
			# Update aircraft combo
			fleet = list_fleet()
			choices = [f"{ac['id']} - {ac['name']} ({ac['type_code']})" for ac in fleet]
			self.ac_combo["values"] = choices
			
			# Set default aircraft if none selected, but don't trigger refresh
			if choices and not self.ac_var.get():
				self.ac_var.set(choices[0])
			
			# Update location display for currently selected aircraft
			selected_ac = self._get_selected_aircraft()
			if selected_ac:
				location = selected_ac.get("location", "HOME")
				self.location_var.set(f"Location: {location}")
			else:
				self.location_var.set("Location: -")
			
			# Get available services
			services = list_airport_services()
			if not services:
				ttk.Label(self.services_inner_frame, text="No services available", font=("Segoe UI", 10)).pack(pady=20)
				return
			
			cat = {c["type_code"]: c for c in aircraft_catalog()}
			
			# Get selected aircraft info for cost calculation
			selected_ac = self._get_selected_aircraft()
			
			for service in services:
				# Create a card-like frame for each service
				service_card = ttk.Frame(self.services_inner_frame, relief=tk.RAISED, borderwidth=1)
				service_card.pack(fill=tk.X, padx=6, pady=8)
				
				# Service header
				header_frame = ttk.Frame(service_card)
				header_frame.pack(fill=tk.X, padx=12, pady=(10, 4))
				
				# Service name
				ttk.Label(header_frame, text=service["name"], font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
				
				# Spacer
				ttk.Frame(header_frame, width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)
				
				# Cost/Purchase section
				action_frame = ttk.Frame(header_frame)
				action_frame.pack(side=tk.RIGHT)
				
				# Special handling for refueling
				if service["type"] == "refueling":
					# Create unique keys for this service's variables
					service_key = service["type"]
					
					# Fuel quantity input
					quantity_frame = ttk.Frame(service_card)
					quantity_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
					
					ttk.Label(quantity_frame, text="Quantity:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
					
					# Create and store variables
					if service_key not in self.fuel_vars:
						self.fuel_vars[service_key] = {}
					
					self.fuel_vars[service_key]["quantity"] = tk.StringVar(value="1000")
					self.fuel_vars[service_key]["unit"] = tk.StringVar(value="litres")
					self.fuel_vars[service_key]["total"] = tk.StringVar(value="$0")
					
					quantity_entry = ttk.Entry(quantity_frame, textvariable=self.fuel_vars[service_key]["quantity"], 
						width=12, font=("Segoe UI", 9))
					quantity_entry.pack(side=tk.LEFT, padx=(0, 4))
					
					# Unit selection
					unit_combo = ttk.Combobox(quantity_frame, textvariable=self.fuel_vars[service_key]["unit"], 
						values=["litres", "gallons"], state="readonly", width=8, font=("Segoe UI", 9))
					unit_combo.pack(side=tk.LEFT, padx=(0, 12))
					unit_combo.bind("<<ComboboxSelected>>", lambda e, s=service, k=service_key: self._update_fuel_cost(s, k))
					quantity_entry.bind("<KeyRelease>", lambda e, s=service, k=service_key: self._update_fuel_cost(s, k))
					
					# Price display
					price_frame = ttk.Frame(quantity_frame)
					price_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
					
					price_label = ttk.Label(price_frame, text="", font=("Segoe UI", 9), foreground="#666")
					price_label.pack(side=tk.LEFT)
					self.fuel_vars[service_key]["price_label"] = price_label
					
					# Total cost
					total_label = ttk.Label(action_frame, textvariable=self.fuel_vars[service_key]["total"], 
						font=("Segoe UI", 12, "bold"), foreground="#0a7f2e")
					total_label.pack(side=tk.LEFT, padx=(0, 8))
					
					# Purchase button
					btn = ttk.Button(action_frame, text="Purchase Fuel", command=lambda s=service, k=service_key: self._on_purchase_fuel(s, k))
					btn.pack(side=tk.LEFT)
					if not selected_ac:
						btn.config(state="disabled")
						quantity_entry.config(state="disabled")
						unit_combo.config(state="disabled")
					
					# Initial update
					self._update_fuel_cost(service, service_key)
				else:
					# Regular service cost calculation
					if selected_ac:
						info = cat.get(selected_ac.get("type_code"))
						hourly_cost = float(info.get("hourly_cost", 2000)) if info else 2000.0
						base_cost = service.get("base_cost", 0)
						cost_per_hour = service.get("cost_per_hour", 0)
						if base_cost > 0 and cost_per_hour > 0:
							cost = int(base_cost + (cost_per_hour * hourly_cost / 100))
						else:
							cost = base_cost if base_cost > 0 else 1000
						cost_label = f"${cost:,}"
					else:
						cost_label = "Select aircraft"
					
					ttk.Label(action_frame, text=cost_label, font=("Segoe UI", 12, "bold"), foreground="#0a7f2e", width=12).pack(side=tk.LEFT, padx=(0, 8))
					
					# Purchase button
					btn = ttk.Button(action_frame, text="Purchase", command=lambda s=service["type"]: self._on_purchase_service(s))
					btn.pack(side=tk.LEFT)
					if not selected_ac:
						btn.config(state="disabled")
				
				# Description
				desc_frame = ttk.Frame(service_card)
				desc_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
				desc_text = service.get("description", "Service available")
				ttk.Label(desc_frame, text=desc_text, font=("Segoe UI", 9), foreground="#666", wraplength=600).pack(anchor=tk.W)
			
			# Update canvas scroll region
			self.services_inner_frame.update_idletasks()
			self.services_canvas.configure(scrollregion=self.services_canvas.bbox("all"))
			
			self._update_recent_services()
			self._refresh_custom_items()
		except Exception as e:
			import traceback
			# Show error but don't crash - display a message
			error_label = ttk.Label(self.services_inner_frame, 
				text=f"Error loading services: {str(e)}", 
				font=("Segoe UI", 9), foreground="#b00020", wraplength=600)
			error_label.pack(pady=20, padx=20)
			traceback.print_exc()
	
	def _get_selected_aircraft(self):
		"""Get the currently selected aircraft with fresh data from the fleet."""
		label = self.ac_var.get()
		if not label or " - " not in label:
			return None
		ac_id = label.split(" - ", 1)[0]
		try:
			from services import list_fleet
			# Always get fresh fleet data to ensure location is current
			fleet = list_fleet()
			aircraft = next((x for x in fleet if x.get("id") == ac_id), None)
			return aircraft
		except Exception:
			return None
	
	def _on_aircraft_selected(self):
		selected_ac = self._get_selected_aircraft()
		if selected_ac:
			location = selected_ac.get("location", "HOME")
			self.location_var.set(f"Location: {location}")
			# Update fuel cost if refueling service exists (don't call refresh to avoid duplicates)
			if "refueling" in self.fuel_vars:
				from services import list_airport_services
				services = list_airport_services()
				fuel_service = next((s for s in services if s["type"] == "refueling"), None)
				if fuel_service:
					self._update_fuel_cost(fuel_service, "refueling")
		else:
			self.location_var.set("Location: -")
		# Refresh custom items when aircraft selection changes
		self._refresh_custom_items()
	
	def _update_fuel_cost(self, service, service_key):
		"""Update fuel cost display based on quantity and unit."""
		try:
			if service_key not in self.fuel_vars:
				return
			
			vars = self.fuel_vars[service_key]
			quantity_str = vars["quantity"].get()
			quantity = float(quantity_str) if quantity_str else 0
			unit = vars["unit"].get()
			
			# Get airport-specific fuel prices
			selected_ac = self._get_selected_aircraft()
			if not selected_ac:
				vars["total"].set("$0")
				vars["price_label"].config(text="Select aircraft")
				return
			
			location = selected_ac.get("location", "HOME")
			from services import get_fuel_prices
			fuel_prices = get_fuel_prices(location)
			price_per_litre = fuel_prices["price_per_litre"]
			price_per_gallon = fuel_prices["price_per_gallon"]
			
			if quantity <= 0:
				vars["total"].set("$0")
				vars["price_label"].config(text=f"${price_per_litre:.2f}/L (${price_per_gallon:.2f}/gal) at {location}")
				return
			
			if unit == "gallons":
				price_per_unit = price_per_gallon
				total = quantity * price_per_unit
				vars["price_label"].config(text=f"${price_per_gallon:.2f}/gal (${price_per_litre:.2f}/L) at {location}")
			else:
				price_per_unit = price_per_litre
				total = quantity * price_per_unit
				vars["price_label"].config(text=f"${price_per_litre:.2f}/L (${price_per_gallon:.2f}/gal) at {location}")
			
			vars["total"].set(f"${total:,.2f}")
		except (ValueError, KeyError) as e:
			if service_key in self.fuel_vars:
				self.fuel_vars[service_key]["total"].set("$0")
				if "price_label" in self.fuel_vars[service_key]:
					self.fuel_vars[service_key]["price_label"].config(text="")
	
	def _on_purchase_fuel(self, service, service_key):
		"""Handle fuel purchase with quantity."""
		selected_ac = self._get_selected_aircraft()
		if not selected_ac:
			messagebox.showinfo("Services", "Please select an aircraft first.")
			return
		
		if service_key not in self.fuel_vars:
			messagebox.showerror("Services", "Service data not found.")
			return
		
		try:
			vars = self.fuel_vars[service_key]
			quantity_str = vars["quantity"].get()
			quantity = float(quantity_str)
			if quantity <= 0:
				messagebox.showwarning("Services", "Please enter a valid quantity greater than 0.")
				return
			
			unit = vars["unit"].get()
			
			# Get airport-specific fuel prices
			location = selected_ac.get("location", "HOME")
			from services import get_fuel_prices
			fuel_prices = get_fuel_prices(location)
			price_per_unit = fuel_prices["price_per_gallon"] if unit == "gallons" else fuel_prices["price_per_litre"]
			total_cost = quantity * price_per_unit
			
			# Confirm purchase
			confirm_msg = f"Purchase {quantity:,.0f} {unit} of fuel for {selected_ac.get('id')}?\n\n"
			confirm_msg += f"Price: ${price_per_unit:.2f} per {unit}\n"
			confirm_msg += f"Total Cost: ${total_cost:,.2f}\n"
			confirm_msg += f"Location: {selected_ac.get('location', 'HOME')}"
			
			if messagebox.askyesno("Purchase Fuel", confirm_msg):
				from services import purchase_airport_service
				purchase_airport_service(selected_ac.get("id"), "refueling", quantity, unit)
				messagebox.showinfo("Services", f"Fuel purchase successful: {quantity:,.0f} {unit} for ${total_cost:,.2f}")
				self.refresh()
				self._update_recent_services()
		except ValueError:
			messagebox.showerror("Services", "Please enter a valid number for quantity.")
		except Exception as exc:
			messagebox.showerror("Services", str(exc))
	
	def _on_purchase_service(self, service_type: str):
		selected_ac = self._get_selected_aircraft()
		if not selected_ac:
			messagebox.showinfo("Services", "Please select an aircraft first.")
			return
		
		ac_id = selected_ac.get("id")
		try:
			from services import purchase_airport_service, list_airport_services
			from catalog import aircraft_catalog
			
			# Get service info for confirmation
			services = list_airport_services()
			service = next((s for s in services if s["type"] == service_type), None)
			if not service:
				messagebox.showerror("Services", "Service not found.")
				return
			
			# Calculate cost
			cat = {c["type_code"]: c for c in aircraft_catalog()}
			info = cat.get(selected_ac.get("type_code"))
			hourly_cost = float(info.get("hourly_cost", 2000)) if info else 2000.0
			base_cost = service.get("base_cost", 0)
			cost_per_hour = service.get("cost_per_hour", 0)
			if base_cost > 0 and cost_per_hour > 0:
				cost = int(base_cost + (cost_per_hour * hourly_cost / 100))
			else:
				cost = base_cost if base_cost > 0 else 1000
			
			# Confirm purchase
			if messagebox.askyesno("Purchase Service", f"Purchase {service['name']} for {selected_ac.get('id')}?\n\nCost: ${cost:,}\nLocation: {selected_ac.get('location', 'HOME')}"):
				purchase_airport_service(ac_id, service_type)
				messagebox.showinfo("Services", f"{service['name']} purchased successfully.")
				self.refresh()
				self._update_recent_services()
		except Exception as exc:
			messagebox.showerror("Services", str(exc))
	
	def _update_recent_services(self):
		selected_ac = self._get_selected_aircraft()
		if not selected_ac:
			self.recent_var.set("Select an aircraft to see recent services")
			return
		
		try:
			from services import get_aircraft_services, list_airport_services
			import time
			
			services = get_aircraft_services(selected_ac.get("id"))
			service_list = list_airport_services()
			service_map = {s["type"]: s["name"] for s in service_list}
			
			# Check for livery (stored separately on aircraft)
			livery = selected_ac.get("livery")
			recent_list = []
			
			if livery:
				livery_name = livery.get("name", "Custom Livery")
				painted_ts = livery.get("painted_timestamp", 0)
				if painted_ts:
					time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(painted_ts))
					recent_list.append(f"Livery: '{livery_name}' ({time_str})")
			
			if not services and not livery:
				self.recent_var.set("No recent services purchased for this aircraft.")
				return
			
			# Format recent services
			for service_type, service_data in sorted(services.items(), 
				key=lambda x: (x[1].get("timestamp") if isinstance(x[1], dict) else x[1]), reverse=True)[:5]:
				service_name = service_map.get(service_type, service_type)
				
				if isinstance(service_data, dict) and "timestamp" in service_data:
					# New format (for refueling with quantity)
					timestamp = service_data.get("timestamp")
					time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))
					if service_type == "refueling" and "quantity" in service_data:
						quantity = service_data.get("quantity", 0)
						unit = service_data.get("unit", "litres")
						recent_list.append(f"{service_name}: {quantity:,.0f} {unit} ({time_str})")
					else:
						recent_list.append(f"{service_name} ({time_str})")
				else:
					# Old format (just timestamp)
					timestamp = service_data
					time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))
					recent_list.append(f"{service_name} ({time_str})")
			
			# Add installed custom items
			from services import list_installed_custom_items
			installed_items = list_installed_custom_items(selected_ac.get("id"))
			for item in installed_items:
				item_name = item.get("name", "Custom Item")
				recent_list.append(f"Custom Item: '{item_name}' (Installed)")
			
			if recent_list:
				self.recent_var.set("\n".join([f"• {item}" for item in recent_list]))
			else:
				self.recent_var.set("No recent services purchased for this aircraft.")
		except Exception:
			self.recent_var.set("Error loading recent services.")
	
	def _refresh_custom_items(self):
		"""Refresh the custom items sections (stored and installable)."""
		# Clear stored items
		for widget in self.stored_inner_frame.winfo_children():
			widget.destroy()
		
		# Clear installable items
		for widget in self.install_inner_frame.winfo_children():
			widget.destroy()
		
		try:
			from services import list_stored_custom_items, list_installed_custom_items
			
			# Get selected aircraft from dropdown
			selected_ac = self._get_selected_aircraft()
			aircraft_location = None
			if selected_ac:
				aircraft_location = (selected_ac.get("location") or "HOME").upper()
			
			# Show stored items
			stored_items = list_stored_custom_items()
			if not stored_items:
				ttk.Label(self.stored_inner_frame, text="No custom items stored", font=("Segoe UI", 9), foreground="#666").pack(pady=20)
			else:
				for item in stored_items:
					item_card = ttk.Frame(self.stored_inner_frame, relief=tk.RAISED, borderwidth=1)
					item_card.pack(fill=tk.X, padx=6, pady=6)
					
					# Item info
					info_frame = ttk.Frame(item_card)
					info_frame.pack(fill=tk.X, padx=10, pady=8)
					
					item_name = item.get("name", "Unnamed Item")
					item_airport = item.get("airport", "UNKNOWN")
					item_cost = item.get("cost", 0)
					
					ttk.Label(info_frame, text=item_name, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
					ttk.Label(info_frame, text=f"Stored at: {item_airport}", font=("Segoe UI", 9), foreground="#666").pack(anchor=tk.W)
					ttk.Label(info_frame, text=f"Cost: ${item_cost:,}", font=("Segoe UI", 9), foreground="#666").pack(anchor=tk.W)
			
			# Show installed items on selected aircraft - ONLY if aircraft is selected AND has installed items
			if selected_ac:
				installed_items = list_installed_custom_items(selected_ac.get("id"))
				if installed_items:
					installed_frame = ttk.LabelFrame(self.install_inner_frame, text=f"Installed on {selected_ac.get('id')}")
					installed_frame.pack(fill=tk.X, padx=6, pady=(10, 6))
					
					for item in installed_items:
						item_card = ttk.Frame(installed_frame, relief=tk.RAISED, borderwidth=1)
						item_card.pack(fill=tk.X, padx=6, pady=6)
						
						info_frame = ttk.Frame(item_card)
						info_frame.pack(fill=tk.X, padx=10, pady=8)
						
						item_id = item.get("item_id")
						item_name = item.get("name", "Unnamed Item")
						
						ttk.Label(info_frame, text=item_name, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
						ttk.Label(info_frame, text="✓ Installed (unique to this aircraft)", font=("Segoe UI", 8), foreground="#0a7f2e").pack(anchor=tk.W)
						
						btn_frame = ttk.Frame(item_card)
						btn_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
						
						btn_uninstall = ttk.Button(btn_frame, text="Uninstall", 
							command=lambda iid=item_id: self._on_uninstall_custom_item(iid))
						btn_uninstall.pack(side=tk.LEFT)
			
			# Show installable items (stored at same airport as selected aircraft)
			if selected_ac and aircraft_location:
				installable_items = list_stored_custom_items(aircraft_location)
				if not installable_items:
					# Only show "no items" message if there are also no installed items
					if not (selected_ac and list_installed_custom_items(selected_ac.get("id"))):
						ttk.Label(self.install_inner_frame, text=f"No items stored at {aircraft_location}", font=("Segoe UI", 9), foreground="#666").pack(pady=20)
				else:
					ttk.Label(self.install_inner_frame, text=f"Items at {aircraft_location}:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 4))
					
					for item in installable_items:
						# Double-check that item is not installed (safety check)
						if item.get("installed_on"):
							continue  # Skip items that are already installed
						
						item_card = ttk.Frame(self.install_inner_frame, relief=tk.RAISED, borderwidth=1)
						item_card.pack(fill=tk.X, padx=6, pady=6)
						
						# Item info
						info_frame = ttk.Frame(item_card)
						info_frame.pack(fill=tk.X, padx=10, pady=8)
						
						item_id = item.get("item_id")
						item_name = item.get("name", "Unnamed Item")
						
						ttk.Label(info_frame, text=item_name, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
						ttk.Label(info_frame, text="Available for installation", font=("Segoe UI", 8), foreground="#0a7f2e").pack(anchor=tk.W)
						
						# Install button
						btn_frame = ttk.Frame(item_card)
						btn_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
						
						btn_install = ttk.Button(btn_frame, text="Install on Aircraft", 
							command=lambda iid=item_id: self._on_install_custom_item(iid))
						btn_install.pack(side=tk.LEFT)
			elif not selected_ac:
				ttk.Label(self.install_inner_frame, text="Select an aircraft to see installable items", font=("Segoe UI", 9), foreground="#666").pack(pady=20)
			
			# Update canvas scroll regions
			self.stored_inner_frame.update_idletasks()
			self.stored_canvas.configure(scrollregion=self.stored_canvas.bbox("all"))
			
			self.install_inner_frame.update_idletasks()
			self.install_canvas.configure(scrollregion=self.install_canvas.bbox("all"))
		except Exception as e:
			import traceback
			ttk.Label(self.stored_inner_frame, text=f"Error: {str(e)}", font=("Segoe UI", 9), foreground="#b00020").pack(pady=20)
			traceback.print_exc()
	
	def _on_purchase_custom_item(self):
		"""Handle purchasing a custom item."""
		try:
			airport = self.purchase_airport_var.get().strip().upper()
			item_name = self.item_name_var.get().strip()
			cost_str = self.item_cost_var.get().strip()
			
			if not airport:
				messagebox.showwarning("Purchase", "Please enter an airport code.")
				return
			if not item_name:
				messagebox.showwarning("Purchase", "Please enter an item name.")
				return
			
			try:
				cost = int(float(cost_str))
			except ValueError:
				messagebox.showerror("Purchase", "Cost must be a valid number.")
				return
			
			if cost <= 0:
				messagebox.showerror("Purchase", "Cost must be greater than 0.")
				return
			
			from services import purchase_custom_item
			item_id = purchase_custom_item(airport, item_name, cost)
			messagebox.showinfo("Purchase", f"Custom item '{item_name}' purchased and stored at {airport}.")
			
			# Clear form
			self.purchase_airport_var.set("")
			self.item_name_var.set("")
			self.item_cost_var.set("1000")
			
			# Refresh display
			self._refresh_custom_items()
		except Exception as exc:
			messagebox.showerror("Purchase", str(exc))
	
	def _on_install_custom_item(self, item_id: str):
		"""Handle installing a custom item on the selected aircraft."""
		selected_ac = self._get_selected_aircraft()
		if not selected_ac:
			messagebox.showwarning("Install", "Please select an aircraft first.")
			return
		
		try:
			from services import install_custom_item
			install_custom_item(item_id, selected_ac.get("id"))
			messagebox.showinfo("Install", f"Custom item installed on {selected_ac.get('id')}.")
			self._refresh_custom_items()
			self._update_recent_services()
		except Exception as exc:
			messagebox.showerror("Install", str(exc))
	
	def _on_uninstall_custom_item(self, item_id: str):
		"""Handle uninstalling a custom item from the selected aircraft."""
		try:
			from services import uninstall_custom_item
			uninstall_custom_item(item_id)
			messagebox.showinfo("Uninstall", "Custom item uninstalled and returned to storage.")
			self._refresh_custom_items()
			self._update_recent_services()
		except Exception as exc:
			messagebox.showerror("Uninstall", str(exc))


def ensure_storage_seed():
	try:
		# Basic seed so the app can show status without crashing
		from storage import load_state, save_state
		state = load_state()
		changed = False
		if "cash" not in state:
			state["cash"] = 5_000_000
			changed = True
		if "company" not in state:
			state["company"] = {"name": ""}
			changed = True
		if "fleet" not in state:
			state["fleet"] = []
			changed = True
		if changed:
			save_state(state)
	except Exception:
		# storage may not exist yet; ignore
		pass


if __name__ == "__main__":
	# Make sure data directory exists alongside this file
	base_dir = os.path.dirname(os.path.abspath(__file__))
	data_dir = os.path.join(base_dir, "data")
	if not os.path.isdir(data_dir):
		os.makedirs(data_dir, exist_ok=True)

	ensure_storage_seed()
	app = App()
	app.mainloop()


