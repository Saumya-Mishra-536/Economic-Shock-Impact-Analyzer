# maps business types to their commodity inputs and weights
# weights represent how much that commodity contributes to the business cost

BUSINESS_PROFILES = {
    "🥖 Bakery": {
        "description": "bread, cakes, pastries — wheat and sugar heavy",
        "commodities": {
            "WHEAT":       {"ticker": "ZW=F", "weight": 0.40},
            "SUGAR":       {"ticker": "SB=F", "weight": 0.25},
            "CORN":        {"ticker": "ZC=F", "weight": 0.20},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.15},
        }
    },
    "👗 Textile": {
        "description": "fabric, garments, clothing — cotton and energy heavy",
        "commodities": {
            "COTTON":      {"ticker": "CT=F", "weight": 0.50},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.25},
            "ALUMINUM":    {"ticker": "ALI=F","weight": 0.15},
            "COPPER":      {"ticker": "HG=F", "weight": 0.10},
        }
    },
    "🌾 Farm": {
        "description": "agriculture, crops, produce",
        "commodities": {
            "WHEAT":       {"ticker": "ZW=F", "weight": 0.30},
            "CORN":        {"ticker": "ZC=F", "weight": 0.30},
            "COTTON":      {"ticker": "CT=F", "weight": 0.20},
            "SUGAR":       {"ticker": "SB=F", "weight": 0.20},
        }
    },
    "🍽 Restaurant": {
        "description": "food service, cafe, dining",
        "commodities": {
            "WHEAT":       {"ticker": "ZW=F", "weight": 0.30},
            "SUGAR":       {"ticker": "SB=F", "weight": 0.20},
            "COFFEE":      {"ticker": "KC=F", "weight": 0.25},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.25},
        }
    },
    "🏗 Construction": {
        "description": "building, infrastructure, real estate",
        "commodities": {
            "ALUMINUM":    {"ticker": "ALI=F","weight": 0.35},
            "COPPER":      {"ticker": "HG=F", "weight": 0.30},
            "CRUDE_OIL":   {"ticker": "CL=F", "weight": 0.20},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.15},
        }
    },
    "⛽ Transport & Logistics": {
        "description": "delivery, shipping, fleet operations",
        "commodities": {
            "CRUDE_OIL":   {"ticker": "CL=F", "weight": 0.60},
            "BRENT":       {"ticker": "BZ=F", "weight": 0.25},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.15},
        }
    },
    "🏭 Manufacturing": {
        "description": "factory, industrial production",
        "commodities": {
            "ALUMINUM":    {"ticker": "ALI=F","weight": 0.30},
            "COPPER":      {"ticker": "HG=F", "weight": 0.25},
            "CRUDE_OIL":   {"ticker": "CL=F", "weight": 0.25},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.20},
        }
    },
    "☕ Cafe & Beverages": {
        "description": "coffee shop, juice bar, beverages",
        "commodities": {
            "COFFEE":      {"ticker": "KC=F", "weight": 0.40},
            "SUGAR":       {"ticker": "SB=F", "weight": 0.25},
            "NATURAL_GAS": {"ticker": "NG=F", "weight": 0.20},
            "WHEAT":       {"ticker": "ZW=F", "weight": 0.15},
        }
    },
    "🛠 Custom": {
        "description": "define your own cost basket",
        "commodities": {}
    }
}

# all available tickers for custom mode
ALL_COMMODITIES = {
    "Crude Oil":   {"ticker": "CL=F",  "unit": "$/barrel"},
    "Brent Crude": {"ticker": "BZ=F",  "unit": "$/barrel"},
    "Natural Gas": {"ticker": "NG=F",  "unit": "$/mmbtu"},
    "Gold":        {"ticker": "GC=F",  "unit": "$/oz"},
    "Copper":      {"ticker": "HG=F",  "unit": "$/lb"},
    "Corn":        {"ticker": "ZC=F",  "unit": "$/bushel"},
    "Wheat":       {"ticker": "ZW=F",  "unit": "$/bushel"},
    "Sugar":       {"ticker": "SB=F",  "unit": "cents/lb"},
    "Coffee":      {"ticker": "KC=F",  "unit": "cents/lb"},
    "Cotton":      {"ticker": "CT=F",  "unit": "cents/lb"},
    "Aluminum":    {"ticker": "ALI=F", "unit": "$/tonne"},
}

def get_profile(name):
    return BUSINESS_PROFILES.get(name, None)

def get_all_profiles():
    return list(BUSINESS_PROFILES.keys())