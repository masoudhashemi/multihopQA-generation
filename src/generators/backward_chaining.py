import json  # Import json module
import os  # Import os module for path joining
import random
from typing import Any, List, Optional, Tuple

from ..core import InfoType, OperatorType, Rule, State
from ..utils import format_question
from .base_generator import QuestionGenerator

# Sample data is now loaded from files
# from ..data import PLANETS_TABLE, MARIE_CURIE_BIO

# Define path to the data directory relative to this file's location
# Assumes this file is in src/generators/ and data is in data/
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
PLANETS_FILE = os.path.join(DATA_DIR, "planets.json")
CURIE_FILE = os.path.join(DATA_DIR, "curie.txt")


class BackwardChainingGenerator(QuestionGenerator):
    """Implements the backward chaining generation strategy."""

    def _find_rules_producing(self, target_type: InfoType) -> List[Rule]:
        """Finds all rules that output the given target_type."""
        return [rule for rule in self.rules if rule.output_type == target_type]

    def _is_seedable_type(self, info_type: InfoType) -> bool:
        """Checks if a type can typically be used as a starting seed."""
        # Define which types are considered good starting points
        return info_type in [
            InfoType.PERSON_NAME,
            InfoType.LOCATION_NAME,
            InfoType.ARTWORK_NAME,
            InfoType.COUNTRY_NAME,
            InfoType.CITY_NAME,
            InfoType.EVENT_NAME,
            InfoType.TABLE_DATA,
            InfoType.TEXT_SNIPPET,
        ]

    def _load_sample_data(self):
        """Loads sample data from files, caching it for efficiency."""
        if hasattr(self, "_sample_data_cache"):
            return self._sample_data_cache

        print("Loading sample data for seeding...")
        sample_data = {}
        try:
            with open(PLANETS_FILE, "r") as f:
                sample_data[InfoType.TABLE_DATA] = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load planets data from {PLANETS_FILE}: {e}")
            sample_data[InfoType.TABLE_DATA] = None

        try:
            with open(CURIE_FILE, "r") as f:
                sample_data[InfoType.TEXT_SNIPPET] = f.read()
        except Exception as e:
            print(f"Warning: Could not load Curie bio from {CURIE_FILE}: {e}")
            sample_data[InfoType.TEXT_SNIPPET] = None

        # Add simple seeds here too, maybe load from another file?
        sample_data.update(
            {
                InfoType.PERSON_NAME: "Marie Curie",
                InfoType.LOCATION_NAME: "Mount Everest",
                InfoType.ARTWORK_NAME: "Starry Night",
                InfoType.COUNTRY_NAME: "Brazil",
                InfoType.CITY_NAME: "Tokyo",
                InfoType.EVENT_NAME: "Apollo 11 landing",
            }
        )

        self._sample_data_cache = sample_data
        return sample_data

    def _find_seed_value_for_type(self, info_type: InfoType) -> Optional[Any]:
        """Provides a sample seed value for a given seedable type by loading from files."""
        sample_data = self._load_sample_data()
        value = sample_data.get(info_type)
        if value is None:
            print(f"Warning: No sample seed value found/loaded for type {info_type.name}")
        # Return a copy for mutable types like lists/dicts to avoid shared state issues
        if isinstance(value, (list, dict)):
            import copy

            return copy.deepcopy(value)
        return value

    def _find_all_backward_plans(
        self,
        current_target_type: InfoType,
        depth_remaining: int,
        parent_rule_operator: Optional[OperatorType] = None,
        max_plans: int = 10,  # Limit the number of plans found to avoid combinatorial explosion
    ) -> List[List[Rule]]:
        """
        Recursive helper to find ALL valid sequences of rules leading to the target type.
        Returns a list of plans, each plan in EXECUTION order.
        Tries to avoid repeating the same operator type as the parent rule.
        """
        # print(f"Entering _find_all_backward_plans for {current_target_type.name} with depth {depth_remaining}, parent={parent_rule_operator}")
        found_plans: List[List[Rule]] = []

        # Base case: Reached required depth
        if depth_remaining == 0:
            if self._is_seedable_type(current_target_type):
                # print(f"  -> Base case reached: Seedable type {current_target_type.name}")
                return [[]]  # Success: Found one plan (the empty plan for this branch)
            else:
                # print(f"  -> Cannot seed non-seedable type {current_target_type.name} at depth 0")
                return []  # Failure: No plans found for this branch

        if depth_remaining < 0:
            # print(f"  -> Depth limit exceeded for {current_target_type.name}")
            return []  # Failure

        # Find rules that produce the current_target_type
        producer_rules = self._find_rules_producing(current_target_type)

        # Filter out rules with the same operator type as the parent, if applicable
        if parent_rule_operator is not None:
            filtered_producer_rules = [rule for rule in producer_rules if rule.operator != parent_rule_operator]
            if filtered_producer_rules:
                producer_rules = filtered_producer_rules
            # else: # Keep original list if filtering removed all options
            #     print(f"  Warning: Could not avoid repeating operator {parent_rule_operator}...")

        # If no rules produce this type, check if it's a seedable base case (but depth != 0)
        if not producer_rules:
            # Cannot reach required depth if we seed now
            # print(f"  -> No producers for {current_target_type.name}, cannot reach depth {depth_remaining}.")
            return []  # Failure

        # Try all suitable producer rules
        random.shuffle(producer_rules)  # Still shuffle to explore different branches first

        for rule in producer_rules:
            # print(f"  Trying rule {rule.operator.name} for {current_target_type.name}, depth {depth_remaining}")

            # Handle rules with any number of inputs
            if not rule.input_types:  # Rule has no inputs
                if depth_remaining == 1:
                    # print(f"    -> Found plan using no-input rule {rule.operator.name}")
                    found_plans.append([rule])
                # else: Cannot satisfy depth requirement
                #     print(f"    -> No-input rule {rule.operator.name} doesn't match depth {depth_remaining}")
                continue  # Try next rule

            # Rule has inputs: Find all possible combinations of plans for its inputs
            # List of lists: Outer list corresponds to input types, inner lists are plans for that type
            all_plans_per_input: List[List[List[Rule]]] = []
            possible_for_this_rule = True
            for input_type in rule.input_types:
                # Recursively find all plans for this input
                sub_plans = self._find_all_backward_plans(
                    input_type,
                    depth_remaining - 1,
                    parent_rule_operator=rule.operator,
                    max_plans=max_plans - len(found_plans),
                )
                if not sub_plans:
                    # print(f"    -> Failed to find any plan for input {input_type.name} needed by {rule.operator.name}")
                    possible_for_this_rule = False
                    break  # If any input is impossible, this rule path fails
                all_plans_per_input.append(sub_plans)

            if not possible_for_this_rule:
                continue  # Try the next rule

            # Combine the sub-plans: Generate all combinations of selecting one plan for each input
            # Example: input1 has plans [P1a, P1b], input2 has [P2a]. Combinations: (P1a, P2a), (P1b, P2a)
            import itertools

            plan_combinations = list(itertools.product(*all_plans_per_input))
            # print(f"    -> Found {len(plan_combinations)} combinations of sub-plans for rule {rule.operator.name}")

            for combo in plan_combinations:
                # Merge the plans in the current combination, ensuring uniqueness and order
                combined_plan: List[Rule] = []
                seen_rule_ids = set()
                for input_plan in combo:  # combo is a tuple of plans, one for each input
                    for plan_rule in input_plan:
                        if id(plan_rule) not in seen_rule_ids:
                            combined_plan.append(plan_rule)
                            seen_rule_ids.add(id(plan_rule))

                # Add the current rule itself at the end
                if (
                    id(rule) not in seen_rule_ids
                ):  # Avoid adding if already present via sub-plan (unlikely but possible)
                    combined_plan.append(rule)

                # Check if this combined plan has the exact required length *at this point*
                # This check might be tricky due to shared sub-plans. Focus on final length check in `generate`.
                # if len(combined_plan) == max_hops - depth_remaining + 1:
                #     print(f"    -> Successfully combined plan of length {len(combined_plan)} using rule {rule.operator.name}")
                found_plans.append(combined_plan)

                # Stop if we hit the plan limit
                if len(found_plans) >= max_plans:
                    # print(f"  Reached plan limit ({max_plans}), stopping search for {current_target_type.name}.")
                    return found_plans  # Return early

            # If we've already hit the limit from combinations of this rule's inputs, stop trying other rules
            if len(found_plans) >= max_plans:
                break

        # print(f"Returning {len(found_plans)} plans for {current_target_type.name} at depth {depth_remaining}")
        return found_plans

    # Placeholder for the diversity scoring function
    def _score_plan_diversity(self, plan: List[Rule]) -> float:
        """Calculates a diversity score for a given plan (sequence of rules)."""
        if not plan:
            return 0.0

        # Metric 1: Operator Variety (Ratio of unique operators to total hops)
        operators_used = {rule.operator for rule in plan}
        operator_variety = len(operators_used) / len(plan)

        # Metric 2: InfoType Variety (Ratio of unique input/output types to total types mentioned)
        types_mentioned = set()
        total_type_slots = 0
        for rule in plan:
            for itype in rule.input_types:
                types_mentioned.add(itype)
                total_type_slots += 1
            types_mentioned.add(rule.output_type)
            total_type_slots += 1
        type_variety = len(types_mentioned) / total_type_slots if total_type_slots > 0 else 0

        # Combine metrics (e.g., weighted average)
        # Give operator variety slightly more weight maybe
        score = 0.6 * operator_variety + 0.4 * type_variety

        # print(f"Plan score: {score:.3f} (OpVar: {operator_variety:.3f}, TypeVar: {type_variety:.3f})")
        return score

    def generate(self, target_type: InfoType, max_hops: int) -> Optional[Tuple[str, List[Rule], List[State]]]:
        """
        Generates using backward chaining, finding multiple plans and selecting the most diverse.
        Finds a sequence of rules, identifies a seed type/value, then executes forward.
        Always tries to create exactly max_hops steps.
        """
        print(f"\n--- Generating: Backward Chaining (Diversity, Target: {target_type.name}, Max Hops: {max_hops}) ---")

        # 1. Find *all* potential plans backward from the target
        print("Finding all backward plans...")
        all_possible_plans = self._find_all_backward_plans(target_type, max_hops, max_plans=20)  # Limit search

        # Filter plans to keep only those with the exact number of hops required
        valid_plans = [p for p in all_possible_plans if len(p) == max_hops]

        if not valid_plans:
            print(f"Failed to find any backward plans with exactly {max_hops} hops to a seedable type.")
            print(f"(Found {len(all_possible_plans)} plans of other lengths)")
            return None

        print(f"Found {len(valid_plans)} valid plan(s) with exactly {max_hops} hops.")

        # 2. Score and select the most diverse plan
        if len(valid_plans) == 1:
            chosen_plan = valid_plans[0]
            print("Only one valid plan found.")
        else:
            print("Scoring plans for diversity...")
            scored_plans = [(plan, self._score_plan_diversity(plan)) for plan in valid_plans]
            # Sort by score descending
            scored_plans.sort(key=lambda item: item[1], reverse=True)
            chosen_plan = scored_plans[0][0]  # Select the plan with the highest score
            print(f"Selected plan with highest diversity score: {scored_plans[0][1]:.3f}")

        print("Selected Plan (Execution Order):")
        for i, rule in enumerate(chosen_plan):
            print(
                f"  Step {i+1}: {rule.operator.name} - Inputs: {[t.name for t in rule.input_types]} -> Output: {rule.output_type.name}"
            )

        # 3. Identify the required seed type
        if not chosen_plan[0].input_types:
            print(f"Error: First rule in chosen plan ({chosen_plan[0].operator.name}) requires no input?")
            return None
        seed_type_needed = chosen_plan[0].input_types[0]  # Simplistic assumption

        # 4. Find a seed value
        seed_value = self._find_seed_value_for_type(seed_type_needed)
        if seed_value is None:
            print(f"Could not find a sample seed value for the required type: {seed_type_needed.name}")
            return None

        seed_state = State(seed_value, seed_type_needed)
        print(f"Using Seed: {seed_state}")

        # 5. Execute the chosen plan forward
        configuration: List[State] = [seed_state]
        applied_rules: List[Rule] = []
        execution_successful = True

        for i, rule_to_execute in enumerate(chosen_plan):
            print(f"\n-- Executing Plan Step {i + 1}: {rule_to_execute.operator.name} --")

            # Find the *actual* input states from the current configuration
            input_states_for_rule: List[State] = []
            possible = True
            used_state_ids_forward = set()  # Ensure unique states per rule execution

            required_input_types = rule_to_execute.input_types
            # (Handling finding inputs remains the same as before)
            for req_type in required_input_types:
                found_state_for_input = None
                for state in reversed(configuration):
                    if state.info_type == req_type and id(state) not in used_state_ids_forward:
                        found_state_for_input = state
                        used_state_ids_forward.add(id(state))
                        break

                if found_state_for_input:
                    input_states_for_rule.append(found_state_for_input)
                # Allow dynamic seeding only for very basic types, not complex ones like Text/Table
                elif self._is_seedable_type(req_type) and req_type not in [InfoType.TABLE_DATA, InfoType.TEXT_SNIPPET]:
                    # Dynamic seed creation if needed (handle with care)
                    new_seed_val = self._find_seed_value_for_type(req_type)
                    if new_seed_val:
                        print(f"  -> Dynamically creating simple seed for {req_type.name}: {new_seed_val}")
                        new_seed_state = State(new_seed_val, req_type)
                        # Add to config *before* using it if needed elsewhere
                        configuration.append(new_seed_state)
                        input_states_for_rule.append(new_seed_state)
                        used_state_ids_forward.add(id(new_seed_state))
                    else:
                        print(f"Error: Cannot dynamically create seed for {req_type.name}")
                        possible = False
                        break
                else:
                    # If we need an intermediate result that wasn't found (e.g., rule output used twice)
                    # This indicates a flaw in the simple forward execution or plan. Handle gracefully.
                    print(
                        f"Error: Could not find required input state of type {req_type.name} for rule {rule_to_execute.operator.name}"
                    )
                    possible = False
                    break

            if not possible or len(input_states_for_rule) != len(required_input_types):
                print("Error: Failed to find all necessary input states for forward execution.")
                execution_successful = False
                break

            # Execute the rule
            print(f"  Inputs: {[s.value for s in input_states_for_rule]}")
            new_state = self._execute_rule(rule_to_execute, input_states_for_rule)

            # Process result
            if new_state:
                # Check type compatibility (allow SEARCH flexibility)
                # In backward chaining, the plan *should* guarantee the type, but check anyway
                if (
                    new_state.info_type == rule_to_execute.output_type
                    or rule_to_execute.operator == OperatorType.SEARCH
                ):
                    # Add to config only if not already present (e.g., dynamic seed)
                    if id(new_state) not in {id(s) for s in configuration}:
                        configuration.append(new_state)
                    applied_rules.append(rule_to_execute)
                else:
                    print(
                        f"Warning: Rule produced type {new_state.info_type.name}, "
                        f"expected {rule_to_execute.output_type.name} based on plan. Stopping."
                    )
                    execution_successful = False
                    break
            else:
                print("Rule execution failed or returned None. Stopping execution.")
                execution_successful = False
                break

        # Format final question
        if not execution_successful or len(applied_rules) != max_hops:
            print("Failed to successfully execute the full backward plan.")
            return None

        question_text = format_question(seed_state, applied_rules, configuration)
        print(f"\n--- Generated Question (Backward Chaining - Diversity Selected Plan) ---")
        print(question_text)
        print("-------------------------------------------------------------------------")
        return question_text, applied_rules, configuration
