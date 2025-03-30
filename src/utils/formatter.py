from typing import Dict, List

from ..core import Rule, State


def format_question(seed_state: State, applied_rules: List[Rule], configuration: List[State]) -> str:
    """Formats the generated steps into a readable natural language question."""
    if not applied_rules:
        # Handle the case where no hops were generated
        return f"Starting with {seed_state.value} (type: {seed_state.info_type.name}), what can you determine about it?"

    steps_text: List[str] = []
    # Create a map to refer to states by their step number for clarity
    # state_ref_map maps state object ID to its reference string (e.g., "result from step 1")
    state_ref_map: Dict[int, str] = {id(seed_state): f"the initial entity ('{seed_state.value}')"}
    for i, state in enumerate(configuration[1:], start=1):  # Start from index 1 (hop 1 result)
        state_ref_map[id(state)] = f"the result from step {i}"

    for i, rule in enumerate(applied_rules):
        step_num = i + 1
        step_desc = rule.description_template
        output_state = configuration[step_num]  # State produced by this rule (at index step_num)
        input_states = output_state.source_inputs  # States used by this rule

        # Replace input placeholders like {input0}, {input1}
        if input_states:
            for j, input_state in enumerate(input_states):
                placeholder = f"{{input{j}}}"
                # Get the reference string for the input state
                input_ref = state_ref_map.get(id(input_state), f"an earlier result ('{input_state.value}')")
                step_desc = step_desc.replace(placeholder, input_ref)

        # Determine phrasing for the final step vs intermediate steps
        if step_num == len(applied_rules):  # Final step asks the question
            # Replace {output} placeholder with a "what is..." question phrase
            output_question_phrase = f"what is the resulting {rule.output_type.name.lower().replace('_', ' ')}"
            step_desc = step_desc.replace("{output}", output_question_phrase)
            # Ensure it ends with a question mark
            step_desc = step_desc.strip()
            if not step_desc.endswith("?"):
                # Add question mark, handling potential trailing prepositions
                if step_desc.endswith(" of") or step_desc.endswith(" for") or step_desc.endswith(" in"):
                    step_desc += " X?"  # Placeholder if preposition seems dangling
                else:
                    step_desc += "?"
        else:  # Intermediate step describes the action
            # Replace {output} placeholder with a descriptive phrase like "the resulting X"
            output_desc_phrase = f"the resulting {rule.output_type.name.lower().replace('_', ' ')}"
            step_desc = step_desc.replace("{output}", output_desc_phrase)

        steps_text.append(f"{step_num}. {step_desc}")

    # Combine seed info and steps into the final question format
    intro = f"Consider the starting entity: '{seed_state.value}'. Please perform the following sequence of operations:"
    return intro + "\n" + "\n".join(steps_text)
