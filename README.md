new-world-profit-calculator/
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Global settings, constants
│   └── database_config.py    # Database connection settings
│
├── database/
│   ├── __init__.py
│   ├── models.py             # Database table models (e.g., PriceLog, Item, Recipe, Reagent)
│   ├── operations.py         # CRUD operations, including recipe queries
│   └── init_db.py            # Script to initialize the database and tables
│
├── data_input/
│   ├── __init__.py
│   └── json_parser.py        # Parse the provided JSON price data
│
├── analysis/
│   ├── __init__.py
│   ├── price_trends.py       # Analyze price trends over time for specific items
│   ├── profitability.py      # Determine profitability of crafting vs. buying/selling
│   └── recommendations.py    # Generate buy/sell recommendations based on analyses
│
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Miscellaneous helper functions
│
└── main.py                   # Driver script to run the EcoEnchanter



