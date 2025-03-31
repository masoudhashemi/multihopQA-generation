import random
from typing import Any, List, Optional, Tuple

from ..core import InfoType, OperatorType, Rule, State
from ..utils import format_question
from .base_generator import QuestionGenerator


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
        ]

    def _find_seed_value_for_type(self, info_type: InfoType) -> Optional[Any]:
        """Provides a sample seed value for a given seedable type (basic)."""
        # This should ideally draw from a larger pool or use generation techniques
        seed_values = {
            InfoType.PERSON_NAME: "Marie Curie",
            InfoType.LOCATION_NAME: "Mount Everest",
            InfoType.ARTWORK_NAME: "Starry Night",
            InfoType.COUNTRY_NAME: "Brazil",
            InfoType.CITY_NAME: "Tokyo",
            InfoType.EVENT_NAME: "Apollo 11 landing",
        }
        return seed_values.get(info_type)

    def _find_backward_plan(self, current_target_type: InfoType, depth_remaining: int, parent_rule_operator: Optional[OperatorType] = None) -> Optional[List[Rule]]:
        """
        Recursive helper to find a sequence of rules leading to the target type.
        Returns plan in EXECUTION order.
        Tries to avoid repeating the same operator type as the parent rule.
        """
        # print(f"Entering _find_backward_plan for {current_target_type.name} with depth {depth_remaining}, parent={parent_rule_operator}")
        
        # We want to use exactly depth_remaining steps if possible
        if depth_remaining == 0:
            # We should be at a seedable type now
            if self._is_seedable_type(current_target_type):
                # print(f"  -> Base case reached: Seedable type {current_target_type.name}")
                return []  # Reached a seed, plan segment for this branch is empty (success)
            else:
                # print(f"  -> No rules produce non-seedable type {current_target_type.name}")
                return None  # Need exact depth, so return None if we can't seed this type
        
        if depth_remaining < 0:
            # print(f"  -> Depth limit exceeded for {current_target_type.name}")
            return None

        # Find rules that produce the current_target_type
        producer_rules = self._find_rules_producing(current_target_type)
        
        # Filter out rules with the same operator type as the parent, if applicable
        if parent_rule_operator is not None:
            filtered_producer_rules = [
                rule for rule in producer_rules if rule.operator != parent_rule_operator
            ]
            # Fallback: If filtering removed all options, use the original list
            if filtered_producer_rules:
                producer_rules = filtered_producer_rules
            else:
                print(f"  Warning: Could not avoid repeating operator {parent_rule_operator} to produce {current_target_type.name}. All producers are {parent_rule_operator}.")

        # If no rules produce this type, check if it's a seedable base case
        if not producer_rules:
            if self._is_seedable_type(current_target_type):
                # Base case reached, but we still need to use more steps - can't meet exact depth requirement
                if depth_remaining > 0:
                    return None
                # print(f"  -> Base case reached: Seedable type {current_target_type.name}")
                return []  # Reached a seed, plan segment for this branch is empty (success)
            else:
                # print(f"  -> No rules produce non-seedable type {current_target_type.name}")
                return None  # Dead end

        # Try rules in random order to find *a* valid plan
        random.shuffle(producer_rules)

        for rule in producer_rules:
            # print(f"  Trying rule {rule.operator.name} to produce {current_target_type.name}")

            # Handle rules with any number of inputs
            if rule.input_types:  # If the rule has inputs
                # Try to find a plan for each input type
                all_input_plans: List[List[Rule]] = []
                all_plans_successful = True

                for input_type in rule.input_types:
                    # Recursively find a plan for this input, passing the current rule's operator
                    input_plan = self._find_backward_plan(input_type, depth_remaining - 1, parent_rule_operator=rule.operator)

                    # If we couldn't find a plan for this input, this rule won't work
                    if input_plan is None:
                        all_plans_successful = False
                        break

                    # Otherwise, add this input's plan to our collection
                    all_input_plans.append(input_plan)

                # If we found plans for all inputs, combine them and include this rule
                if all_plans_successful:
                    # Merge all the input plans - while avoiding duplicates
                    # Track rules we've already included
                    combined_plan: List[Rule] = []
                    seen_rules = set()  # Using a set to track unique rules by ID

                    # Process each input's plan
                    for plan in all_input_plans:
                        for plan_rule in plan:
                            rule_id = id(plan_rule)  # Use ID to identify unique rule instances
                            if rule_id not in seen_rules:
                                combined_plan.append(plan_rule)
                                seen_rules.add(rule_id)

                    # Then add the current rule at the end (it executes after all its inputs)
                    combined_plan.append(rule)

                    # Return the full plan
                    return combined_plan

            else:  # If rule has no inputs (unusual, but possible)
                if depth_remaining == 1:  # Perfect match for our depth requirement
                    return [rule]  # Just return this rule as the plan
                else:
                    return None  # Can't satisfy depth requirement

        # If no rule led to a successful plan for this target type
        # print(f"  -> No successful plan found for {current_target_type.name} via any producer rule.")
        return None

    def generate(self, target_type: InfoType, max_hops: int) -> Optional[Tuple[str, List[Rule], List[State]]]:
        """
        Attempts to generate a question by planning backward from the target type.
        Finds a sequence of rules, identifies a seed type/value, then executes forward.
        Always tries to create exactly max_hops steps.
        NOTE: This implementation is simplified, especially regarding multi-input rules.
        """
        print(f"\n--- Generating: Backward Chaining (Target: {target_type.name}, Max Hops: {max_hops}) ---")

        # 1. Find a potential plan (sequence of rules) backward from the target
        # Plan is returned in execution order (Seed Rule -> ... -> Target Rule)
        print("Finding backward plan...")
        plan = self._find_backward_plan(target_type, max_hops)

        if plan is None:
            print(f"Failed to find a backward plan with exactly {max_hops} hops to a seedable type.")
            return None

        if not plan:  # Plan is [] means target is seedable, requiring 0 hops.
            print(f"Target type {target_type.name} is directly seedable. Cannot generate multi-hop question.")
            return None
            
        # Verify we've created the correct number of hops
        if len(plan) != max_hops:
            print(f"Warning: Failed to create plan with exactly {max_hops} hops. Got {len(plan)} hops instead.")
            return None

        # Plan is already in execution order
        print(f"Found Backward Plan (Execution Order) with exactly {len(plan)} hops:")
        for i, rule in enumerate(plan):
            print(
                f"  Step {i+1}: {rule.operator.name} - Inputs: {[t.name for t in rule.input_types]} -> Output: {rule.output_type.name}"
            )

        # 2. Identify the required seed type (input to the first rule in the execution plan)
        # If first rule has no input types, something is wrong with the rule or plan
        if not plan[0].input_types:
            print(f"Error: First rule in plan ({plan[0].operator.name}) requires no input?")
            return None
        # Based on our planning logic, assume the first rule's first input is our seed
        # Note: With multi-input rules, some seeds might need to come later
        seed_type_needed = plan[0].input_types[0]

        # 3. Find a seed value for this type
        seed_value = self._find_seed_value_for_type(seed_type_needed)
        if seed_value is None:
            print(f"Could not find a sample seed value for the required type: {seed_type_needed.name}")
            return None

        seed_state = State(seed_value, seed_type_needed)
        print(f"Using Seed: {seed_state}")

        # 4. Execute the plan forward
        configuration: List[State] = [seed_state]
        applied_rules: List[Rule] = []
        execution_successful = True

        for i, rule_to_execute in enumerate(plan):
            print(f"\n-- Executing Plan Step {i + 1}: {rule_to_execute.operator.name} --")

            # Find the *actual* input states from the current configuration
            input_states_for_rule: List[State] = []
            possible = True
            used_state_ids_forward = set()  # Ensure unique states per rule execution

            # Check if we need multiple inputs of the same type
            required_input_types = rule_to_execute.input_types
            type_counts = {}
            for req_type in required_input_types:
                type_counts[req_type] = type_counts.get(req_type, 0) + 1

            # For each required input type (respecting multiplicity)
            for req_type in required_input_types:
                found_state_for_input = None

                # Look for the most recent, unused state of the required type
                for state in reversed(configuration):
                    if state.info_type == req_type and id(state) not in used_state_ids_forward:
                        found_state_for_input = state
                        used_state_ids_forward.add(id(state))
                        break  # Found most recent unused state for this input type

                # If we found it, add it
                if found_state_for_input:
                    input_states_for_rule.append(found_state_for_input)
                # If not found but the type is seedable, we could create a dynamic seed
                elif self._is_seedable_type(req_type):
                    new_seed_value = self._find_seed_value_for_type(req_type)
                    if new_seed_value:
                        print(f"  -> Creating additional seed for {req_type.name}: {new_seed_value}")
                        new_seed_state = State(new_seed_value, req_type)
                        configuration.append(new_seed_state)
                        input_states_for_rule.append(new_seed_state)
                    else:
                        print(f"Error: Cannot create a seed value for required type {req_type.name}")
                        possible = False
                        break
                # If we need another instance of a rule's output type:
                elif any(r.output_type == req_type for r in plan[:i]):
                    # Try to find a rule that can produce this type
                    producer_rules = [r for r in plan[:i] if r.output_type == req_type]
                    if producer_rules:
                        # Use the first rule we found earlier that can produce this type
                        repeat_rule = producer_rules[0]
                        print(f"  -> Need another {req_type.name}. Re-executing a rule to create it")

                        # Find inputs for this rule
                        repeat_inputs = []
                        repeat_possible = True
                        repeat_used_ids = set()

                        for repeat_req_type in repeat_rule.input_types:
                            repeat_found = None
                            # Look for an unused instance of this input type
                            for state in reversed(configuration):
                                if (
                                    state.info_type == repeat_req_type
                                    and id(state) not in repeat_used_ids
                                    and id(state) not in used_state_ids_forward
                                ):
                                    repeat_found = state
                                    repeat_used_ids.add(id(state))
                                    break

                            if repeat_found:
                                repeat_inputs.append(repeat_found)
                            elif self._is_seedable_type(repeat_req_type):
                                # Create another seed if needed
                                another_seed_value = self._find_seed_value_for_type(repeat_req_type)
                                if another_seed_value:
                                    print(
                                        f"  -> Creating another seed for {repeat_req_type.name}: {another_seed_value}"
                                    )
                                    another_seed = State(another_seed_value, repeat_req_type)
                                    configuration.append(another_seed)
                                    repeat_inputs.append(another_seed)
                                else:
                                    repeat_possible = False
                                    break
                            else:
                                repeat_possible = False
                                break

                        if repeat_possible and len(repeat_inputs) == len(repeat_rule.input_types):
                            # Execute the rule again
                            print(f"  -> Re-executing rule {repeat_rule.operator.name} to get another {req_type.name}")
                            additional_state = self._execute_rule(repeat_rule, repeat_inputs)
                            if additional_state:
                                configuration.append(additional_state)
                                input_states_for_rule.append(additional_state)
                                # We don't add this to applied_rules because we're building the question from the original plan
                            else:
                                print(f"  -> Failed to create additional {req_type.name}")
                                possible = False
                                break
                        else:
                            print(f"  -> Could not find/create inputs for rule to produce additional {req_type.name}")
                            possible = False
                            break
                    else:
                        print(f"  -> Need another {req_type.name} but no rule in plan can produce it")
                        possible = False
                        break
                else:
                    print(
                        f"Error during forward execution: Cannot find required input type {req_type.name} for rule {rule_to_execute.operator.name}"
                    )
                    possible = False
                    break

            if not possible:
                execution_successful = False
                break

            if len(input_states_for_rule) != len(rule_to_execute.input_types):
                print(
                    f"Error: Mismatch between found inputs ({len(input_states_for_rule)}) and required inputs ({len(rule_to_execute.input_types)}) for rule {rule_to_execute.operator.name}"
                )
                execution_successful = False
                break

            print(f"  Inputs: {[s.value for s in input_states_for_rule]}")
            new_state = self._execute_rule(rule_to_execute, input_states_for_rule)

            if new_state:
                configuration.append(new_state)
                applied_rules.append(rule_to_execute)
            else:
                print(f"Forward execution failed at rule: {rule_to_execute.operator.name}")
                execution_successful = False
                break

        # 5. Format the result if execution was successful
        if not execution_successful or not applied_rules:
            print("Failed to execute the backward plan successfully.")
            return None

        # Check if the final state matches the original target type
        if configuration[-1].info_type != target_type:
            print(
                f"Warning: Plan execution finished, but final type ({configuration[-1].info_type.name}) does not match target ({target_type.name})."
            )
            # Still return the result, but warn the user.

        question_text = format_question(seed_state, applied_rules, configuration)
        print("\n--- Generated Question (Backward Chaining) ---")
        print(question_text)
        print("-----------------------------------------------")
        return question_text, applied_rules, configuration
