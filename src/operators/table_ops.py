import statistics
from typing import Any, Dict, List, Optional

from ..core import InfoType, State

# Assume table data is List[Dict[str, Any]]


def simulate_table_lookup(args: List[Any], expected_output_type: InfoType) -> Optional[State]:
    """Simulates looking up a value in a table (list of dicts)."""
    if len(args) != 4:
        print("  -> Error: TABLE_LOOKUP expects 4 arguments (table, key_column_name, key_value, target_column_name).")
        return None

    table_data, key_column_name, key_value, target_column_name = args
    print(f"  Simulating TABLE_LOOKUP: Find '{target_column_name}' where '{key_column_name}' matches '{key_value}'")

    if not isinstance(table_data, list) or not all(isinstance(row, dict) for row in table_data):
        print(f"  -> Error: Invalid table format. Expected List[Dict], got {type(table_data)}.")
        return None
    if not table_data:
        print("  -> Error: Input table is empty.")
        return None
    if not isinstance(key_column_name, str):
        print(f"  -> Error: Key column name must be a string, got {type(key_column_name)}.")
        return None
    if not isinstance(target_column_name, str):
        print(f"  -> Error: Target column name must be a string, got {type(target_column_name)}.")
        return None

    # Check if key column exists in the first row (basic validation)
    if key_column_name not in table_data[0]:
        print(f"  -> Error: Key column '{key_column_name}' not found in table header.")
        return None
    # Check if target column exists (basic validation)
    if target_column_name not in table_data[0]:
        print(f"  -> Error: Target column '{target_column_name}' not found in table header.")
        return None

    found_value = None
    for row in table_data:
        if key_column_name not in row:  # Should not happen if header is consistent
            continue
        # Attempt simple type coercion for matching key_value
        row_key_str = str(row.get(key_column_name))
        key_value_str = str(key_value)
        if row_key_str == key_value_str:
            if target_column_name not in row:
                # This also should not happen if header is consistent
                print(
                    f"  -> Error: Target column '{target_column_name}' not found in the matching row (inconsistent table?)."
                )
                return None
            found_value = row.get(target_column_name)
            print(f"  -> Found value: {found_value}")
            break  # Found the first match

    if found_value is None:
        print(f"  -> Error: No row found where key '{key_column_name}' matches '{key_value}'.")
        return None

    # Return value with the type expected by the rule
    return State(found_value, expected_output_type)


def simulate_filter_table(args: List[Any], expected_output_type: InfoType) -> Optional[State]:
    """Simulates filtering a table (list of dicts) based on a column value and comparison."""
    if len(args) != 4:
        print("  -> Error: FILTER_TABLE expects 4 arguments (table, column_name, comparison_type, filter_value).")
        return None

    table_data, column_name, comparison_type_str, filter_value = args
    print(f"  Simulating FILTER_TABLE: Keep rows where '{column_name}' {comparison_type_str} '{filter_value}'")

    if not isinstance(table_data, list) or not all(isinstance(row, dict) for row in table_data):
        print(f"  -> Error: Invalid table format. Expected List[Dict], got {type(table_data)}.")
        return None
    if not isinstance(column_name, str):
        print(f"  -> Error: Column name must be a string, got {type(column_name)}.")
        return None
    if not isinstance(comparison_type_str, str):
        print(f"  -> Error: Comparison type must be a string, got {type(comparison_type_str)}.")
        return None

    comp = comparison_type_str.lower().replace("_", " ")  # Normalize comparison string
    valid_comparisons = ["equals", "==", "is", "greater than", ">", "less than", "<"]
    if comp not in valid_comparisons:
        print(f"  -> Error: Invalid comparison type '{comp}'. Valid types: {valid_comparisons}")
        return None

    filtered_table = []
    for row in table_data:
        if column_name not in row:
            continue  # Skip row if filter column is missing

        row_value = row.get(column_name)
        match = False
        try:
            # Attempt numerical comparison first if possible
            num_row_val = None
            num_filter_val = None
            if isinstance(row_value, (int, float)) and isinstance(filter_value, (int, float)):
                num_row_val = row_value
                num_filter_val = filter_value
            else:
                # Try converting strings to numbers if comparison needs it
                if comp in ["greater than", ">", "less than", "<"]:
                    num_row_val = float(row_value)
                    num_filter_val = float(filter_value)

            if num_row_val is not None and num_filter_val is not None:
                if comp in ["greater than", ">"] and num_row_val > num_filter_val:
                    match = True
                elif comp in ["less than", "<"] and num_row_val < num_filter_val:
                    match = True
                elif comp in ["equals", "==", "is"] and num_row_val == num_filter_val:
                    match = True  # Numerical equality

            # If numerical didn't apply or didn't match, try string equality
            if not match and comp in ["equals", "==", "is"]:
                if str(row_value) == str(filter_value):  # String equality
                    match = True

        except (ValueError, TypeError) as e:
            # Handle cases where conversion or comparison fails for the row
            # print(f"  -> Warning: Comparison failed for row value '{row_value}' ({type(row_value)}) vs '{filter_value}' ({type(filter_value)}): {e}")
            pass  # Skip row if types are incompatible for the comparison

        if match:
            filtered_table.append(row)

    print(f"  -> Filtered table contains {len(filtered_table)} rows.")
    if not filtered_table:
        print("  -> Warning: Filter resulted in an empty table.")

    return State(filtered_table, InfoType.TABLE_DATA)  # Always returns TABLE_DATA


def simulate_aggregate_table(args: List[Any], expected_output_type: InfoType) -> Optional[State]:
    """Simulates aggregating a column in a table (list of dicts)."""
    if len(args) != 3:
        print("  -> Error: AGGREGATE_TABLE expects 3 arguments (table, agg_function_name, column_name).")
        return None

    table_data, agg_function_name, column_name = args

    # Basic validation for agg function name
    if not isinstance(agg_function_name, str):
        print(f"  -> Error: Aggregation function name must be a string, got {type(agg_function_name)}.")
        return None
    agg_type = agg_function_name.lower()
    valid_aggs = ["sum", "average", "avg", "mean"]  # Add count, max, min? Requires rule changes
    if agg_type not in valid_aggs:
        print(f"  -> Error: Unsupported aggregation type '{agg_type}'. Supported: {valid_aggs}")
        return None

    print(f"  Simulating AGGREGATE_TABLE: Perform '{agg_type}' on column '{column_name}'")

    if not isinstance(table_data, list) or not all(isinstance(row, dict) for row in table_data):
        print(f"  -> Error: Invalid table format. Expected List[Dict], got {type(table_data)}.")
        return None
    if not isinstance(column_name, str):
        print(f"  -> Error: Column name must be a string, got {type(column_name)}.")
        return None

    values_to_aggregate = []
    for row in table_data:
        if column_name in row:
            val = row[column_name]
            # Ensure values are numeric for aggregation
            if isinstance(val, (int, float)):
                values_to_aggregate.append(val)
            else:
                print(f"  -> Warning: Skipping non-numeric value '{val}' in column '{column_name}'.")

    if not values_to_aggregate:
        print(f"  -> Error: No valid numeric values found in column '{column_name}' to aggregate.")
        return None

    result = None
    if agg_type == "sum":
        result = sum(values_to_aggregate)
    elif agg_type in ["average", "avg", "mean"]:
        result = statistics.mean(values_to_aggregate)
    # Add cases for count, max, min if those functions are added to rules
    else:
        # This case should be caught by initial validation, but included for safety
        print(f"  -> Error: Unknown aggregation type '{agg_type}'.")
        return None

    print(f"  -> Aggregation result: {result}")
    # Aggregation typically results in a number, use the expected type from rule
    return State(result, expected_output_type)
