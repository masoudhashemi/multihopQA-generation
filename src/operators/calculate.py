import datetime
import statistics
from typing import Any, List, Optional

from ..core import InfoType, State


def simulate_calculate(operation: str, args: List[Any], expected_output_type: InfoType) -> Optional[State]:
    """Simulates mathematical calculations."""
    print(f"  Simulating CALCULATE: {operation} with args {args}")
    value: Any = None
    info_type: InfoType = expected_output_type  # Use expected type by default

    try:
        # Ensure args have values, not State objects for calculation
        arg_values = [a.value if isinstance(a, State) else a for a in args]

        # --- Simple Arithmetic ---
        if operation == "sum" and len(arg_values) >= 2 and all(isinstance(a, (int, float)) for a in arg_values):
            value = sum(arg_values)
            info_type = InfoType.NUMERICAL_VALUE
        elif operation == "subtract" and len(arg_values) == 2 and all(isinstance(a, (int, float)) for a in arg_values):
            value = arg_values[0] - arg_values[1]
            info_type = InfoType.NUMERICAL_VALUE
        elif operation == "multiply" and len(arg_values) == 2 and all(isinstance(a, (int, float)) for a in arg_values):
            value = arg_values[0] * arg_values[1]
            info_type = InfoType.NUMERICAL_VALUE
        elif operation == "divide" and len(arg_values) == 2 and all(isinstance(a, (int, float)) for a in arg_values):
            if arg_values[1] == 0:
                print("  -> Error: Division by zero.")
                return None
            value = arg_values[0] / arg_values[1]
            info_type = InfoType.NUMERICAL_VALUE
        elif (
            operation == "abs_difference"
            and len(arg_values) == 2
            and all(isinstance(a, (int, float)) for a in arg_values)
        ):
            value = abs(arg_values[0] - arg_values[1])
            info_type = InfoType.NUMERICAL_VALUE
        elif (
            operation == "percentage" and len(arg_values) == 2 and all(isinstance(a, (int, float)) for a in arg_values)
        ):
            if arg_values[1] == 0:
                print("  -> Error: Percentage division by zero.")
                return None
            value = (arg_values[0] / arg_values[1]) * 100
            info_type = InfoType.NUMERICAL_VALUE

        # --- Date/Time ---
        elif (
            operation == "difference_years"
            and len(arg_values) == 2
            and all(isinstance(a, datetime.date) for a in arg_values)
        ):
            delta = abs(arg_values[0] - arg_values[1])
            value = delta.days / 365.25  # Approximate years
            info_type = InfoType.DURATION  # Keep DURATION if defined
        elif (
            operation == "difference_days"
            and len(arg_values) == 2
            and all(isinstance(a, datetime.date) for a in arg_values)
        ):
            delta = abs(arg_values[0] - arg_values[1])
            value = delta.days
            info_type = InfoType.NUMERICAL_VALUE
        elif (
            operation == "date_plus_days"
            and len(arg_values) == 2
            and isinstance(arg_values[0], datetime.date)
            and isinstance(arg_values[1], (int, float))
        ):
            value = arg_values[0] + datetime.timedelta(days=int(arg_values[1]))
            info_type = InfoType.DATE
        elif operation == "extract_year" and len(arg_values) == 1 and isinstance(arg_values[0], datetime.date):
            value = arg_values[0].year
            info_type = InfoType.NUMERICAL_VALUE

        # --- Comparison ---
        elif (
            operation == "greater_than"
            and len(arg_values) == 2
            and all(isinstance(a, (int, float)) for a in arg_values)
        ):
            value = arg_values[0] > arg_values[1]
            info_type = InfoType.BOOLEAN
        elif (
            operation == "earlier_than"
            and len(arg_values) == 2
            and all(isinstance(a, datetime.date) for a in arg_values)
        ):
            value = arg_values[0] < arg_values[1]
            info_type = InfoType.BOOLEAN
        elif operation == "are_equal" and len(arg_values) == 2:
            value = arg_values[0] == arg_values[1]
            info_type = InfoType.BOOLEAN

        # --- List/Table Operations --- (Removed: Use AGGREGATE_TABLE operator)
        # elif operation in ["list_sum", "list_avg", "list_max", "list_count"] and len(arg_values) == 1:
        # ... (Removed code block) ...

        # --- Fallback for legacy or unknown ---
        elif operation == "convert_days_to_years" and len(arg_values) == 1 and isinstance(arg_values[0], (int, float)):
            value = arg_values[0] / 365.25
            info_type = InfoType.DURATION
        else:
            print(f"  -> Unknown/invalid calculation or args: {operation} {arg_values}")
            return None

        # Final check: Ensure we have a result
        if value is None:  # Simplified check now that list ops are gone
            print(f"  -> Calculation resulted in None unexpectedly for {operation}.")
            return None

        print(f"  -> Result: {value} (as type {info_type.name})")
        # Ensure the returned state type matches the expected output type from the rule, if possible
        # This is a basic check; more robust type validation/conversion might be needed.
        final_type = info_type if info_type == expected_output_type else expected_output_type
        return State(value, final_type)
    except Exception as e:
        print(f"  -> Calculation Error: {e}")
        import traceback

        traceback.print_exc()
        return None
