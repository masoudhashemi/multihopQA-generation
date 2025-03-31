import random
from typing import List, Optional, Tuple

from ..core import OperatorType, Rule, State
from ..utils import format_question
from .base_generator import QuestionGenerator


class ConstrainedRandomWalkGenerator(QuestionGenerator):
    """Implements the constrained random walk generation strategy."""

    def generate(
        self, seed_state: State, max_hops: int, max_complexity: int
    ) -> Optional[Tuple[str, List[Rule], List[State]]]:
        """
        Generates using forward chaining with constraints and diversity promotion.
        Selects rules staying within complexity budget, not yet used, and
        favors diversity using weighted random choice.

        Args:
            seed_state: The initial State.
            max_hops: Maximum number of generation steps.
            max_complexity: The maximum allowed sum of complexities for applied rules.

        Returns:
            A tuple (formatted_question, applied_rules, configuration) or None.
        """
        print(
            f"\n--- Generating: Constrained Random Walk (Diversity, Max Hops: {max_hops}, Max Complexity: {max_complexity}) ---"
        )
        print(f"Seed: {seed_state}")
        configuration: List[State] = [seed_state]
        applied_rules: List[Rule] = []
        current_complexity: int = 0

        for hop in range(max_hops):
            print(f"\n-- Hop {hop + 1} (Current Complexity: {current_complexity}/{max_complexity}) --")
            # Find all applicable rules
            all_applicable_options = self._find_applicable_rules(configuration)

            # Filter based on complexity constraint
            constrained_options: List[Tuple[Rule, List[State]]] = []
            for rule, inputs in all_applicable_options:
                if current_complexity + rule.complexity <= max_complexity:
                    constrained_options.append((rule, inputs))

            # Filter out rules already applied in this sequence from the constrained options
            applied_rule_ids = {id(rule) for rule in applied_rules}
            unique_constrained_options = [
                (rule, inputs) for rule, inputs in constrained_options if id(rule) not in applied_rule_ids
            ]

            if not unique_constrained_options:
                if not all_applicable_options:
                    print("No applicable rules found. Stopping generation.")
                elif not constrained_options:
                    print(
                        f"No applicable rules found within complexity budget "
                        f"({max_complexity - current_complexity} remaining). Stopping."
                    )
                else:
                    print("No *unique* applicable rules found within complexity budget. Stopping generation.")
                break

            # --- Strategy: Use base class method for weighted selection on unique, constrained options ---
            selection_result = self._select_rule_with_diversity(
                unique_constrained_options, configuration, applied_rules
            )

            if not selection_result:
                print("Weighted selection failed (no options returned). Stopping generation.")
                break

            chosen_rule, input_states_for_rule = selection_result
            # --- End of weighted selection ---
            print(f"Selected Rule (via Diversity): {chosen_rule} (Cost: {chosen_rule.complexity})")

            # Execute the rule
            new_state = self._execute_rule(chosen_rule, input_states_for_rule)

            # Process result
            if new_state:
                if new_state.info_type == chosen_rule.output_type or chosen_rule.operator == OperatorType.SEARCH:
                    configuration.append(new_state)
                    applied_rules.append(chosen_rule)
                    current_complexity += chosen_rule.complexity  # Add complexity cost
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
        print(
            f"\n--- Generated Question (Constrained Random Walk - Diversity - Total Complexity: {current_complexity}) ---"
        )
        print(question_text)
        print("--------------------------------------------------------------------------------------------------")
        return question_text, applied_rules, configuration
