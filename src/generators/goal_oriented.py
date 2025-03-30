import random
from typing import List, Optional, Tuple

from ..core import InfoType, OperatorType, Rule, State
from ..utils import format_question
from .base_generator import QuestionGenerator


class GoalOrientedGenerator(QuestionGenerator):
    """Implements the goal-oriented generation strategy."""

    def _score_rule_for_goal(self, rule: Rule, target_type: InfoType) -> float:
        """Assigns a score based on how well a rule's output matches the target type."""
        if rule.output_type == target_type:
            return 1.0  # Perfect match

        # Heuristics: Types that are good precursors to the target
        if target_type == InfoType.DURATION and rule.output_type == InfoType.DATE:
            return 0.7  # Dates are needed for duration calculation
        if target_type == InfoType.CITY_NAME and rule.output_type == InfoType.LOCATION_NAME:
            return 0.6  # Location can often lead to City
        if target_type == InfoType.COUNTRY_NAME and rule.output_type in [InfoType.CITY_NAME, InfoType.LOCATION_NAME]:
            return 0.6  # City/Location can lead to Country
        if target_type == InfoType.NUMERICAL_VALUE and rule.output_type == InfoType.TABLE_DATA:
            return 0.5  # Code operating on tables might produce numbers
        if target_type == InfoType.PERSON_NAME and rule.output_type == InfoType.ARTWORK_NAME:
            return 0.5  # Artwork can lead to creator (Person)
        # Add more heuristics as needed

        # General fallback
        return 0.1  # Low score for unrelated types

    def generate(
        self, seed_state: State, target_type: InfoType, max_hops: int
    ) -> Optional[Tuple[str, List[Rule], List[State]]]:
        """
        Generates using forward chaining, prioritizing rules leading towards a target type.
        Uses weighted random selection based on rule scores.
        Stops if target type is reached or max_hops exceeded.
        """
        print(f"\n--- Generating: Goal-Oriented Walk (Target: {target_type.name}, Max Hops: {max_hops}) ---")
        print(f"Seed: {seed_state}")
        configuration: List[State] = [seed_state]
        applied_rules: List[Rule] = []
        target_reached = False

        for hop in range(max_hops):
            print(f"\n-- Hop {hop + 1} (Aiming for: {target_type.name}) --")
            # Find all applicable rules
            applicable_options = self._find_applicable_rules(configuration)
            if not applicable_options:
                print("No applicable rules found. Stopping generation.")
                break

            # Score applicable rules based on the goal
            scored_options = []
            scores = []
            for rule, inputs in applicable_options:
                score = self._score_rule_for_goal(rule, target_type)
                if score > 0:  # Only consider rules with non-zero score
                    scored_options.append((rule, inputs))
                    scores.append(score)
                # print(f"  Rule: {rule.operator.name} -> {rule.output_type.name}, Score: {score:.2f}") # Debug

            if not scored_options:
                print("No applicable rules found contributing to the goal. Stopping generation.")
                break

            # Strategy: Weighted random choice based on scores
            chosen_rule, input_states_for_rule = random.choices(scored_options, weights=scores, k=1)[0]
            print(
                f"Selected Rule (Weighted Choice): {chosen_rule} (Score: {scores[scored_options.index((chosen_rule, input_states_for_rule))]:.2f})"
            )

            # Execute the rule
            new_state = self._execute_rule(chosen_rule, input_states_for_rule)

            # Process result
            if new_state:
                # Check type compatibility (allow SEARCH flexibility)
                if new_state.info_type == chosen_rule.output_type or chosen_rule.operator == OperatorType.SEARCH:
                    configuration.append(new_state)
                    applied_rules.append(chosen_rule)

                    # Check if target type was reached
                    if new_state.info_type == target_type:
                        print(f"Target type {target_type.name} reached at hop {hop + 1}.")
                        target_reached = True
                        break  # Stop generation once target is reached
                else:
                    print(
                        f"Warning: Rule produced type {new_state.info_type.name}, expected {chosen_rule.output_type.name}. Stopping branch."
                    )
                    break
            else:
                print("Rule execution failed or returned None. Stopping generation.")
                break

        # Format final question
        if not applied_rules:
            print("Failed to generate any hops.")
            return None

        question_text = format_question(seed_state, applied_rules, configuration)
        status = "Target Reached" if target_reached else "Max Hops Reached"
        print(f"\n--- Generated Question (Goal-Oriented Walk - Status: {status}) ---")
        print(question_text)
        print("----------------------------------------------------------------")
        return question_text, applied_rules, configuration
