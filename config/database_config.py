#config/database_config.py
import os

# The base directory of your project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the SQLite database
DATABASE_PATH = os.path.join(BASE_DIR, "new_world_profit_calculator_db.sqlite")

# Connection URI for SQLite
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
