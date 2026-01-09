import json
import os
from typing import Any, Dict


DATA_FILE_NAME = "data.json"


def _data_path() -> str:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	data_dir = os.path.join(base_dir, "data")
	if not os.path.isdir(data_dir):
		os.makedirs(data_dir, exist_ok=True)
	return os.path.join(data_dir, DATA_FILE_NAME)


def load_state() -> Dict[str, Any]:
	path = _data_path()
	if not os.path.isfile(path):
		return {}
	try:
		with open(path, "r", encoding="utf-8") as f:
			return json.load(f)
	except json.JSONDecodeError:
		# Corrupt file; back it up and start fresh
		try:
			os.replace(path, path + ".bak")
		except Exception:
			pass
		return {}


def save_state(state: Dict[str, Any]) -> None:
	path = _data_path()
	tmp = path + ".tmp"
	with open(tmp, "w", encoding="utf-8") as f:
		json.dump(state, f, indent=2)
	os.replace(tmp, path)


