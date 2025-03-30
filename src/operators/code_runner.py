from typing import Any, Dict, Optional

from ..core import InfoType, State


def simulate_code(code_snippet: str, data_input: Dict[str, Any]) -> Optional[State]:
    """
    Simulates running a Python code snippet in a restricted environment.
    !! WARNING: This is a placeholder. Real execution is complex and risky. !!
    """
    print(f"  Simulating RUN_CODE (Placeholder - No actual execution):")
    print(f"  --- CODE --- \n{code_snippet}\n  --- DATA --- \n{data_input}\n  ------------")

    # --- Dummy responses based on simple code patterns ---
    result_value: Any = None
    result_type: InfoType = InfoType.CODE_OUTPUT  # Default

    # Example: Simulate finding max in a list passed via data_input
    if "max(" in code_snippet and "numbers" in data_input and isinstance(data_input["numbers"], list):
        try:
            result_value = max(data_input["numbers"]) if data_input["numbers"] else None
            result_type = InfoType.NUMERICAL_VALUE
        except TypeError:  # Handle non-numeric list
            result_value = "Error: Non-numeric data"
            result_type = InfoType.TEXT_SNIPPET
        except Exception as e:
            result_value = f"Error: {e}"
            result_type = InfoType.TEXT_SNIPPET

    # Example: Simulate filtering items
    elif "filter" in code_snippet and "items" in data_input and isinstance(data_input["items"], list):
        # Dummy filter: return items > 5 if numeric, or items starting with 'A' if string
        try:
            filtered_list = []
            for item in data_input["items"]:
                if isinstance(item, (int, float)) and item > 5:
                    filtered_list.append(item)
                elif isinstance(item, str) and item.upper().startswith("A"):
                    filtered_list.append(item)
            result_value = filtered_list
            result_type = InfoType.TABLE_DATA  # List output treated as table data
        except Exception as e:
            result_value = f"Error filtering: {e}"
            result_type = InfoType.TEXT_SNIPPET

    else:
        print("  -> Code simulation pattern not recognized.")
        result_value = f"Simulated output for code: {code_snippet[:30]}..."
        # Keep default result_type CODE_OUTPUT

    if result_value is not None:
        print(f"  -> Simulated Result: {result_value} (as type {result_type.name})")
        return State(result_value, result_type)
    else:
        print("  -> Code simulation did not produce a result.")
        return None
