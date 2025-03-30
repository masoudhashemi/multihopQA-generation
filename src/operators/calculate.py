import datetime
from typing import Any, List, Optional

from ..core import InfoType, State


def simulate_calculate(operation: str, args: List[Any]) -> Optional[State]:
    """Simulates mathematical calculations."""
    print(f"  Simulating CALCULATE: {operation} with args {args}")
    value: Any = None
    info_type: InfoType = InfoType.NUMERICAL_VALUE  # Default, might change

    try:
        # Ensure args have values, not State objects for calculation
        arg_values = [a.value if isinstance(a, State) else a for a in args]

        if (
            operation == "difference_years"
            and len(arg_values) == 2
            and all(isinstance(a, datetime.date) for a in arg_values)
        ):
            delta = abs(arg_values[0] - arg_values[1])
            value = delta.days / 365.25
            info_type = InfoType.DURATION
        elif operation == "sum" and len(arg_values) >= 2 and all(isinstance(a, (int, float)) for a in arg_values):
            value = sum(arg_values)
        elif operation == "divide" and len(arg_values) == 2 and all(isinstance(a, (int, float)) for a in arg_values):
            if arg_values[1] == 0:
                print("  -> Error: Division by zero.")
                return None
            value = arg_values[0] / arg_values[1]
        elif operation == "convert_days_to_years" and len(arg_values) == 1 and isinstance(arg_values[0], (int, float)):
            value = arg_values[0] / 365.25
            info_type = InfoType.DURATION
        # Add more operations as needed
        else:
            print(f"  -> Unknown/invalid calculation or args: {operation} {arg_values}")
            return None

        print(f"  -> Result: {value} (as type {info_type.name})")
        return State(value, info_type)
    except Exception as e:
        print(f"  -> Calculation Error: {e}")
        return None
