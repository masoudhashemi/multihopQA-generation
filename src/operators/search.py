import datetime
import random
import re
from typing import Any, Optional

from ..core import InfoType, State


def simulate_search(query: str, target_type: InfoType) -> Optional[State]:
    """
    Simulates a web search or knowledge base lookup.
    Returns a plausible State matching the target_type or None if simulation fails.
    """
    print(f"  Simulating SEARCH: '{query}' (expecting {target_type.name})")
    # --- Dummy Responses (Replace with actual API calls) ---
    query = query.lower()
    value: Any = None
    info_type: InfoType = target_type  # Assume we get the type we ask for initially

    # Simple pattern matching for demonstration
    patterns = {
        r"birth date of albert einstein": (datetime.date(1879, 3, 14), InfoType.DATE),
        r"birth date of leonardo da vinci": (datetime.date(1452, 4, 15), InfoType.DATE),
        r"birth date of marie curie": (datetime.date(1867, 11, 7), InfoType.DATE),
        r"population of paris": (2_100_000, InfoType.NUMERICAL_VALUE),
        r"capital of france": ("Paris", InfoType.CITY_NAME),
        r"capital of brazil": ("Brasília", InfoType.CITY_NAME),
        r"height of eiffel tower": (330.0, InfoType.NUMERICAL_VALUE),
        r"where is mona lisa located": ("Louvre Museum", InfoType.LOCATION_NAME),
        r"creator of mona lisa": ("Leonardo da Vinci", InfoType.PERSON_NAME),
        r"currency of japan": ("Japanese Yen", InfoType.TEXT_SNIPPET),  # Example non-target type
        r"start date of.*ww2": (datetime.date(1939, 9, 1), InfoType.DATE),
        r"city containing.*louvre museum": ("Paris", InfoType.CITY_NAME),
        r"country containing.*louvre museum": ("France", InfoType.COUNTRY_NAME),
        r"country of paris": ("France", InfoType.COUNTRY_NAME),
    }

    for pattern, (result_val, result_type) in patterns.items():
        if re.search(pattern, query):
            value = result_val
            info_type = result_type  # Use the type defined in our dummy data
            break
    else:  # Fallback if no specific pattern matched
        print(f"  -> No specific simulation pattern for '{query}'. Providing generic fallback.")
        if target_type == InfoType.NUMERICAL_VALUE:
            value = random.uniform(1, 1000)
        elif target_type == InfoType.DATE:
            value = datetime.date.today() - datetime.timedelta(days=random.randint(365, 3650))
        elif target_type == InfoType.CITY_NAME:
            value = "SimCity"
        elif target_type == InfoType.PERSON_NAME:
            value = f"Sim Person for '{query}'"
        elif target_type == InfoType.LOCATION_NAME:
            value = f"Sim Location for '{query}'"
        else:
            value = f"Simulated text result for '{query}'"
            info_type = InfoType.TEXT_SNIPPET

    if value is not None:
        # Check if the simulated type matches the target type (loosely)
        actual_type = info_type
        if target_type == InfoType.NUMERICAL_VALUE and not isinstance(value, (int, float)):
            actual_type = InfoType.TEXT_SNIPPET
        elif target_type == InfoType.DATE and not isinstance(value, datetime.date):
            actual_type = InfoType.TEXT_SNIPPET
        # Add more type checks as needed

        print(f"  -> Found: {value} (as type {actual_type.name})")
        # Return state with the *actual* type found by the simulation
        return State(value, actual_type)
    else:
        print(f"  -> Found: Nothing")
        return None
