import random
from typing import Any, Dict, List, Optional, Tuple

from ..core import InfoType, OperatorType, Rule, State
from ..operators import simulate_calculate, simulate_code, simulate_search
from ..utils import format_question


class QuestionGenerator:
    """Orchestrates the generation of multihop questions using various strategies."""

    def __init__(self, rules: List[Rule]):
        """Initializes the generator with a set of available rules."""
        self.rules = rules
        print(f"QuestionGenerator initialized with {len(self.rules)} rules.")

    def _find_applicable_rules(self, current_config: List[State]) -> List[Tuple[Rule, List[State]]]:
        """
        Finds all rules that can be applied given the current configuration (list of states).
        Returns a list of tuples, where each tuple contains (applicable_rule, list_of_input_states).
        """
        applicable_options: List[Tuple[Rule, List[State]]] = []
        # Optimization: Create a map of available states by type for faster lookup
        states_by_type: Dict[InfoType, List[State]] = {}
        for state in reversed(current_config):  # Check recent states first
            if state.info_type not in states_by_type:
                states_by_type[state.info_type] = []
            states_by_type[state.info_type].append(state)

        for rule in self.rules:
            # Check if enough states of the required types are available
            possible_inputs_list: List[List[State]] = []  # Stores potential input states for each position
            possible = True
            for req_type in rule.input_types:
                if req_type in states_by_type and states_by_type[req_type]:
                    possible_inputs_list.append(states_by_type[req_type])
                else:
                    possible = False
                    break  # Required type not available
            if not possible:
                continue  # Cannot fulfill this rule's input requirements

            # Find a valid combination of input states (simplistic: use the most recent state for each type)
            # A more complex approach could explore combinations or allow user guidance.
            selected_input_states: List[State] = []
            used_state_ids = set()  # Ensure a state isn't used twice for the *same* rule application
            combination_possible = True
            for i, req_type in enumerate(rule.input_types):
                found_match = False
                # Iterate through available states of the required type (most recent first)
                for state in possible_inputs_list[i]:
                    if id(state) not in used_state_ids:
                        selected_input_states.append(state)
                        used_state_ids.add(id(state))
                        found_match = True
                        break
                if not found_match:
                    combination_possible = False
                    break  # Couldn't find a unique state for this input slot

            if combination_possible and len(selected_input_states) == len(rule.input_types):
                # Ensure the order matches input_types (may need adjustment based on selection logic)
                # Our simple logic picks the first available for each type slot, maintaining order implicitly.
                applicable_options.append((rule, selected_input_states))

        return applicable_options

    def _execute_rule(self, rule: Rule, input_states: List[State]) -> Optional[State]:
        """
        Executes the simulation function corresponding to the rule's operator.
        Handles passing arguments and interpreting results.
        Returns the new State or None if execution fails.
        """
        print(f"Executing Rule: {rule.operator.name} with inputs {[s.value for s in input_states]}")
        input_values = [s.value for s in input_states]  # Extract values from input states
        new_state: Optional[State] = None

        try:
            # --- Dispatch to the appropriate simulation function ---
            if rule.operator == OperatorType.SEARCH:
                # Query construction needs improvement - highly dependent on rule intent
                # Simple placeholder using description template elements
                query = rule.description_template  # Start with template
                input_vals_str = [str(v) for v in input_values]  # String representations of inputs

                # --- Attempt more specific query patterns ---
                # Basic substitution first
                for i, val_str in enumerate(input_vals_str):
                    query = query.replace(f"{{input{i}}}", val_str)
                # Remove the {output} placeholder if it remains
                query = query.replace("{output}", rule.output_type.name.lower().replace("_", " "))

                # Override with structured queries if pattern matches description
                desc_lower = rule.description_template.lower()
                if "birth date of" in desc_lower and len(input_vals_str) == 1:
                    query = f"birth date of {input_vals_str[0]}"
                elif "birth place of" in desc_lower and len(input_vals_str) == 1:
                    query = f"birth place of {input_vals_str[0]}"
                elif "capital city of" in desc_lower and len(input_vals_str) == 1:
                    query = f"capital of {input_vals_str[0]}"
                elif "where" in desc_lower and "located" in desc_lower and len(input_vals_str) == 1:
                    query = f"where is {input_vals_str[0]} located"
                elif "population of" in desc_lower and len(input_vals_str) == 1:
                    query = f"population of {input_vals_str[0]}"
                elif "creator of" in desc_lower and len(input_vals_str) == 1:
                    query = f"creator of {input_vals_str[0]}"
                elif "start date of" in desc_lower and len(input_vals_str) == 1:
                    query = f"start date of {input_vals_str[0]}"
                elif "city for the location" in desc_lower and len(input_vals_str) == 1:
                    query = f"city containing {input_vals_str[0]}"
                elif "country for the location" in desc_lower and len(input_vals_str) == 1:
                    query = f"country containing {input_vals_str[0]}"
                elif "country of" in desc_lower and len(input_vals_str) == 1:
                    query = f"country of {input_vals_str[0]}"
                # ... add more specific query patterns as needed ...

                # Final query cleanup (optional)
                query = (
                    query.replace("Find the ", "").replace("Identify the ", "").strip()
                )  # Remove common leading phrases if query looks ok

                new_state = simulate_search(query, rule.output_type)

            elif rule.operator == OperatorType.CALCULATE:
                # Infer operation from description (needs robust mapping)
                operation = "unknown"
                desc = rule.description_template.lower()
                if "duration" in desc and "between" in desc:
                    operation = "difference_years"
                elif "sum" in desc:
                    operation = "sum"
                elif "dividing" in desc:
                    operation = "divide"
                # ... add more operation mappings ...
                new_state = simulate_calculate(operation, input_values)  # Pass raw values

            elif rule.operator == OperatorType.RUN_CODE:
                # This requires defining the code and input mapping within the rule or here
                # Example for the "max value" rule:
                if "maximum value" in rule.description_template and rule.input_types[0] == InfoType.TABLE_DATA:
                    code_snippet = "result = max(data['numbers']) if data.get('numbers') else None"
                    # Assume the input state's value is the list and map it to 'numbers' key
                    if isinstance(input_values[0], list):
                        data_input = {"numbers": input_values[0]}
                        new_state = simulate_code(code_snippet, data_input)
                    else:
                        print("  -> Error: RUN_CODE expected list input for max value rule.")
                # Example for the "filter list" rule:
                elif "filter the list" in rule.description_template and rule.input_types[0] == InfoType.TABLE_DATA:
                    # Define criteria (e.g., > 5 or starts with 'A') - should be part of rule ideally
                    code_snippet = """
items = data.get('items', [])
filtered_list = []
for item in items:
    if isinstance(item, (int, float)) and item > 5:
        filtered_list.append(item)
    elif isinstance(item, str) and item.upper().startswith('A'):
        filtered_list.append(item)
result = filtered_list
                     """
                    if isinstance(input_values[0], list):
                        data_input = {"items": input_values[0]}
                        new_state = simulate_code(code_snippet, data_input)
                    else:
                        print("  -> Error: RUN_CODE expected list input for filter rule.")
                else:
                    print(f"  -> Specific RUN_CODE simulation logic not implemented for: {rule.description_template}")

            # --- Add other operators: TABLE_LOOKUP, EXTRACT_INFO ---
            # elif rule.operator == OperatorType.TABLE_LOOKUP: ...
            # elif rule.operator == OperatorType.EXTRACT_INFO: ...

            # Store provenance information in the new state if created
            if new_state:
                new_state.source_rule = rule
                new_state.source_inputs = input_states

            return new_state

        except Exception as e:
            # Catch unexpected errors during execution simulation
            print(f"!! Error executing rule {rule.operator.name}: {e}")
            import traceback

            traceback.print_exc()  # Print full traceback for debugging
            return None
