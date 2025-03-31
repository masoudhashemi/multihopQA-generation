import random
from typing import List, Optional, Tuple

from ..core import OperatorType, Rule, State
from ..utils import format_question
from .base_generator import QuestionGenerator


class ForwardChainingGenerator(QuestionGenerator):
    """Implements the forward chaining generation strategy."""

    def generate(self, seed_state: State, max_hops: int) -> Optional[Tuple[str, List[Rule], List[State]]]:
        """
        Generates a question using simple forward chaining with diversity promotion.
        At each step, selects an applicable rule using weighted random choice
        that favors operator novelty and using older input states.

        Args:
            seed_state: The initial State to start generation from.
            max_hops: The maximum number of steps (hops) to generate.

        Returns:
            A tuple containing (formatted_question, list_of_applied_rules, final_configuration)
            or None if generation fails.
        """
        print(f"\n--- Generating: Forward Chaining (Diversity Promoted, Max Hops: {max_hops}) ---")
        print(f"Seed: {seed_state}")
        configuration: List[State] = [seed_state]
        applied_rules: List[Rule] = []

        for hop in range(max_hops):
            print(f"\n-- Hop {hop + 1} --")
            # Find rules applicable to the current configuration
            applicable_options = self._find_applicable_rules(configuration)

            # Filter out rules already applied in this sequence
            applied_rule_ids = {id(rule) for rule in applied_rules}
            unique_applicable_options: List[Tuple[Rule, List[State]]] = [
                (rule, inputs) for rule, inputs in applicable_options if id(rule) not in applied_rule_ids
            ]

            if not unique_applicable_options:
                if not applicable_options:
                    print("No applicable rules found. Stopping generation.")
                else:
                    print("No *unique* applicable rules found. Stopping generation.")
                break

            # --- Strategy: Use base class method for weighted selection ---
            selection_result = self._select_rule_with_diversity(unique_applicable_options, configuration, applied_rules)

            if not selection_result:
                print("Weighted selection failed (no options returned). Stopping generation.")
                break

            chosen_rule, input_states_for_rule = selection_result
            # --- End of weighted selection ---

            # Execute the chosen rule
            new_state = self._execute_rule(chosen_rule, input_states_for_rule)

            # Process the result
            if new_state:
                # Basic check: Did the simulation return roughly the expected type?
                # Allow for some flexibility (e.g., SEARCH might return TEXT_SNIPPET)
                if new_state.info_type == chosen_rule.output_type or chosen_rule.operator == OperatorType.SEARCH:
                    configuration.append(new_state)
                    applied_rules.append(chosen_rule)
                else:
                    # If type mismatch is significant (e.g., expected number, got text)
                    print(
                        f"Warning: Rule produced type {new_state.info_type.name}, "
                        f"expected {chosen_rule.output_type.name}. Stopping branch."
                    )
                    break
            else:
                print("Rule execution failed or returned None. Stopping generation.")
                break  # Stop if the tool simulation failed

        # Final check and formatting
        if not applied_rules:
            print("Failed to generate any hops.")
            return None

        question_text = format_question(seed_state, applied_rules, configuration)
        print("\n--- Generated Question (Forward Chaining - Diversity Promoted) ---")
        print(question_text)
        print("-------------------------------------------------------------------")
        return question_text, applied_rules, configuration
