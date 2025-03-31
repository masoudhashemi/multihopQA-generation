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
        Generates using forward chaining, prioritizing rules leading towards a target type
        and promoting diversity. Uses weighted random selection based on combined scores
        (Goal * Diversity) from rules not yet applied.
        Continues until exactly max_hops are generated or no more unique rules can be applied.
        """
        print(f"\n--- Generating: Goal-Oriented Walk (Diversity, Target: {target_type.name}, Max Hops: {max_hops}) ---")
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

            # Filter out rules already applied in this sequence
            applied_rule_ids = {id(rule) for rule in applied_rules}
            unique_applicable_options = [
                (rule, inputs) for rule, inputs in applicable_options if id(rule) not in applied_rule_ids
            ]

            if not unique_applicable_options:
                print("No *unique* applicable rules found. Stopping generation.")
                break

            # Calculate goal scores for unique applicable options
            current_goal_scores = None  # Pass None to diversity selector if target reached
            if not target_reached:
                print("  Calculating goal scores...")
                current_goal_scores = {}
                for rule, _ in unique_applicable_options:
                    score = self._score_rule_for_goal(rule, target_type)
                    current_goal_scores[id(rule)] = score
                    print(f"    - Rule '{rule.description_template[:30]}...': Goal Score={score:.2f}")
            else:
                print("  Target already reached. Using only diversity scoring for remaining hops.")

            # --- Strategy: Use base class method for weighted selection (Goal * Diversity) ---
            selection_result = self._select_rule_with_diversity(
                unique_applicable_options,
                configuration,
                applied_rules,
                goal_scores=current_goal_scores,  # Pass calculated scores (or None)
            )

            if not selection_result:
                print("Weighted selection failed (no options returned). Stopping generation.")
                break

            chosen_rule, input_states_for_rule = selection_result
            # --- End of weighted selection ---

            # Execute the rule
            new_state = self._execute_rule(chosen_rule, input_states_for_rule)

            # Process result
            if new_state:
                # Check type compatibility (allow SEARCH flexibility)
                if new_state.info_type == chosen_rule.output_type or chosen_rule.operator == OperatorType.SEARCH:
                    configuration.append(new_state)
                    applied_rules.append(chosen_rule)

                    # Check if target type was reached, but don't stop generation
                    if new_state.info_type == target_type and not target_reached:
                        print(
                            f"Target type {target_type.name} reached at hop {hop + 1}, continuing to complete requested {max_hops} hops."
                        )
                        target_reached = True
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
        print(f"\n--- Generated Question (Goal-Oriented Walk - Diversity - Status: {status}) ---")
        print(f"Generated question with exact {len(applied_rules)}/{max_hops} hops.")
        print(question_text)
        print("----------------------------------------------------------------")
        return question_text, applied_rules, configuration
