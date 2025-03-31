import random
from typing import Any, Dict, List, Optional, Tuple

from ..core import InfoType, OperatorType, Rule, State
from ..operators import simulate_calculate, simulate_code, simulate_search
from ..operators.search import simulate_search_relationship, simulate_contextual_search
from ..operators.table_ops import simulate_aggregate_table, simulate_filter_table, simulate_table_lookup
from ..operators.text_ops import simulate_extract_info
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

    def _select_rule_with_diversity(
        self,
        candidate_options: List[Tuple[Rule, List[State]]],
        configuration: List[State],
        applied_rules: List[Rule],
        goal_scores: Optional[Dict[int, float]] = None,  # Added optional goal scores (key: id(rule))
    ) -> Optional[Tuple[Rule, List[State]]]:
        """
        Selects a rule from candidate options using weighted random choice favoring diversity.
        Optionally combines diversity score with provided goal scores.

        Args:
            candidate_options: List of (Rule, input_states) tuples to choose from.
            configuration: The current list of states generated so far.
            applied_rules: The list of rules applied so far.
            goal_scores: Optional dictionary mapping rule ID to its goal relevance score.

        Returns:
            A tuple (chosen_rule, input_states_for_rule) or None if no options available.
        """
        if not candidate_options:
            return None

        combined_scores = []
        config_indices = {id(state): i for i, state in enumerate(configuration)}
        last_operator = applied_rules[-1].operator if applied_rules else None
        max_possible_age = len(configuration) - 1

        print(f"  Calculating combined scores (Diversity * Goal) for {len(candidate_options)} options...")
        for rule, input_states in candidate_options:
            diversity_score = 1.0  # Baseline positive score

            # 1. Operator Novelty Bonus
            op_novelty_bonus = 0.0
            if last_operator and rule.operator != last_operator:
                op_novelty_bonus = 1.0  # Bonus for different operator
                diversity_score += op_novelty_bonus

            # 2. Input Recency Bonus (using older states is better)
            input_recency_bonus = 0.0
            if input_states:
                total_age = 0
                num_valid_states = 0
                for state in input_states:
                    state_index = config_indices.get(id(state), -1)
                    if state_index != -1:
                        age = max_possible_age - state_index
                        total_age += age
                        num_valid_states += 1
                if num_valid_states > 0:
                    avg_age = total_age / num_valid_states
                    if max_possible_age > 0:
                        input_recency_bonus = 0.5 * (avg_age / max_possible_age)
                    else:
                        input_recency_bonus = 0  # Avoid division by zero at hop 1
                    diversity_score += input_recency_bonus

            # Get goal score if provided
            current_goal_score = 1.0
            if goal_scores is not None:
                current_goal_score = goal_scores.get(id(rule), 0.0)  # Default to 0 if rule not in goal_scores

            # Combine scores (multiplication ensures both need to be good)
            final_score = diversity_score * current_goal_score

            print(
                f"    - Rule '{rule.description_template[:30]}...': Score={final_score:.2f} (Div={diversity_score:.2f}, Goal={current_goal_score:.2f})"
            )
            combined_scores.append(final_score)

        # Ensure scores are positive for random.choices
        positive_scores = [max(s, 0.01) for s in combined_scores]  # Use a small floor

        # Check if all scores became zero (or near zero floor)
        if sum(positive_scores) <= len(positive_scores) * 0.01:  # Check if effectively all scores are at the floor
            print("  Warning: All candidate rules have near-zero combined scores. Cannot select.")
            return None

        # Select using weighted random choice based on combined scores
        chosen_rule, input_states_for_rule = random.choices(candidate_options, weights=positive_scores, k=1)[0]
        print(f"  Selected Rule (Weighted by Diversity*Goal): {chosen_rule}")
        return chosen_rule, input_states_for_rule

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
                # Simple Arithmetic
                if "sum of" in desc:
                    operation = "sum"
                elif "difference between" in desc and "absolute" not in desc:
                    operation = "subtract"
                elif "product of" in desc:
                    operation = "multiply"
                elif "dividing" in desc:
                    operation = "divide"
                elif "absolute difference" in desc:
                    operation = "abs_difference"
                elif "percentage" in desc:
                    operation = "percentage"
                # Date/Time
                elif "duration in years between" in desc:
                    operation = "difference_years"
                elif "number of days between" in desc:
                    operation = "difference_days"
                elif "days after" in desc:
                    operation = "date_plus_days"
                elif "extract the year" in desc:
                    operation = "extract_year"
                # Comparison
                elif "greater than" in desc:
                    operation = "greater_than"
                elif "earlier than" in desc:
                    operation = "earlier_than"
                elif "are equal" in desc or "is equal to" in desc:
                    operation = "are_equal"
                # List/Table Operations
                elif "sum of the primary numerical list" in desc:
                    operation = "list_sum"
                elif "average of the primary numerical list" in desc:
                    operation = "list_avg"
                elif "maximum value in the primary numerical list" in desc:
                    operation = "list_max"
                elif "count the number of items" in desc:
                    operation = "list_count"

                # Check if operation was identified
                if operation == "unknown":
                    print(
                        f"  -> Warning: Could not determine calculation operation from description: '{rule.description_template}'"
                    )
                else:
                    new_state = simulate_calculate(operation, input_values, rule.output_type)  # Pass output type too

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

            # --- NEW: Table and Text Operators ---
            elif rule.operator == OperatorType.TABLE_LOOKUP:
                new_state = simulate_table_lookup(input_values, rule.output_type)

            elif rule.operator == OperatorType.FILTER_TABLE:
                new_state = simulate_filter_table(input_values, rule.output_type)

            elif rule.operator == OperatorType.AGGREGATE_TABLE:
                # The aggregation function name is now the second input value
                new_state = simulate_aggregate_table(input_values, rule.output_type)

            elif rule.operator == OperatorType.EXTRACT_INFO:
                new_state = simulate_extract_info(rule.description_template, input_values, rule.output_type)

            elif rule.operator == OperatorType.SEARCH_RELATIONSHIP:
                if len(input_values) == 2:
                    new_state = simulate_search_relationship(
                        input_values[0], input_values[1], rule.output_type
                    )
                else:
                    print(f"  -> Error: SEARCH_RELATIONSHIP requires exactly 2 inputs, got {len(input_values)}.")
                    new_state = None

            elif rule.operator == OperatorType.SEARCH_CONTEXTUAL:
                if len(input_values) == 2:
                    new_state = simulate_contextual_search(
                        input_values[0], input_values[1], rule.output_type
                    )
                else:
                    print(f"  -> Error: SEARCH_CONTEXTUAL requires exactly 2 inputs, got {len(input_values)}.")
                    new_state = None

            # --- Add other operators here if needed ---
            # else:
            #    print(f"Warning: No execution logic defined for operator {rule.operator.name}")

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
