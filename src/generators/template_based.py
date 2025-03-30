from typing import List, Optional, Tuple

from ..core import OperatorType, Rule, State
from ..utils import format_question
from .base_generator import QuestionGenerator


class TemplateBasedGenerator(QuestionGenerator):
    """Implements the template-based generation strategy."""

    def generate(self, seed_state: State, template: List[str]) -> Optional[Tuple[str, List[Rule], List[State]]]:
        """
        Generates a question by trying to follow a predefined template of steps.
        Matches template steps to rule descriptions (case-insensitive substring match).

        Args:
            seed_state: The initial State.
            template: A list of strings, where each string describes a desired step
                    (e.g., "Find birth date", "Calculate duration").

        Returns:
            A tuple (formatted_question, applied_rules, configuration) or None.
        """
        print(f"\n--- Generating: Template Based (Template: {template}) ---")
        print(f"Seed: {seed_state}")
        configuration: List[State] = [seed_state]
        applied_rules: List[Rule] = []

        for i, step_pattern in enumerate(template):
            print(f"\n-- Step {i + 1}: Target '{step_pattern}' --")
            step_pattern_lower = step_pattern.lower()
            found_rule_for_step = False

            # 1. Find rules potentially matching the template description
            matching_rules = [r for r in self.rules if step_pattern_lower in r.description_template.lower()]
            if not matching_rules:
                print(f"No rules found matching description pattern: '{step_pattern}'")
                return None  # Template cannot be fulfilled

            # 2. Find which of these matching rules are actually applicable now
            applicable_options_for_step: List[Tuple[Rule, List[State]]] = []
            current_applicable = self._find_applicable_rules(configuration)
            rule_to_inputs_map = {id(rule): inputs for rule, inputs in current_applicable}

            for rule in matching_rules:
                if id(rule) in rule_to_inputs_map:
                    applicable_options_for_step.append((rule, rule_to_inputs_map[id(rule)]))

            if not applicable_options_for_step:
                print(f"Found rules matching description, but none are applicable with current states.")
                # Debugging info:
                available_types = {s.info_type.name for s in configuration}
                required_types = {rt.name for r in matching_rules for rt in r.input_types}
                print(f"  Available types: {available_types}")
                print(f"  Required types by matching rules: {required_types}")
                return None  # Cannot fulfill template step

            # 3. Strategy: Select the first applicable rule matching the template step
            chosen_rule, input_states_for_rule = applicable_options_for_step[0]
            print(f"Selected Rule: {chosen_rule}")

            # 4. Execute the rule
            new_state = self._execute_rule(chosen_rule, input_states_for_rule)

            # 5. Process result
            if new_state:
                if new_state.info_type == chosen_rule.output_type or chosen_rule.operator == OperatorType.SEARCH:
                    configuration.append(new_state)
                    applied_rules.append(chosen_rule)
                    found_rule_for_step = True
                else:
                    print(
                        f"Warning: Rule produced type {new_state.info_type.name}, expected {chosen_rule.output_type.name}. Stopping."
                    )
                    return None
            else:
                print("Rule execution failed or returned None. Stopping generation.")
                return None

            if not found_rule_for_step:  # Should not happen if applicable_options_for_step was found
                print(f"Error: Could not execute applicable rule for step '{step_pattern}'. Stopping.")
                return None

        # Format the final question
        question_text = format_question(seed_state, applied_rules, configuration)
        print("\n--- Generated Question (Template Based) ---")
        print(question_text)
        print("-------------------------------------------")
        return question_text, applied_rules, configuration
