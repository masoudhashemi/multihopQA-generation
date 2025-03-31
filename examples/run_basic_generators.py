import os
import random
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.core import InfoType, Rule, State
from src.core.rules import RULES_DB
from src.generators import (
    BackwardChainingGenerator,
    ConstrainedRandomWalkGenerator,
    ForwardChainingGenerator,
    GoalOrientedGenerator,
    TemplateBasedGenerator,
)

# Import sample data loaders from backward chaining (or create a central loader)
from src.generators.backward_chaining import BackwardChainingGenerator as BCG


def main():
    print("Initializing Question Generation Demo...")

    # Load all defined rules
    all_rules = RULES_DB
    print(f"Loaded {len(all_rules)} rules.")

    # Instantiate generators
    fc_gen = ForwardChainingGenerator(all_rules)
    crw_gen = ConstrainedRandomWalkGenerator(all_rules)
    bc_gen = BackwardChainingGenerator(all_rules)
    template_gen = TemplateBasedGenerator(all_rules)
    # temp_bcg needed for loading data easily in this example
    temp_bcg = BCG(all_rules)

    # --- Example 1: Forward Chaining starting with a Person ---
    print("\n=== Example 1: Forward Chaining (Person Seed) ===")
    seed1 = State("Albert Einstein", InfoType.PERSON_NAME)
    result1 = fc_gen.generate(seed_state=seed1, max_hops=3)
    if result1:
        question1, _, config1 = result1
        print(f"Generated Question 1:\n{question1}")
        print(f"Final State Type: {config1[-1].info_type.name}")

    # --- Example 2: Constrained Random Walk starting with Location ---
    print("\n=== Example 2: Constrained Random Walk (Location Seed) ===")
    seed2 = State("Eiffel Tower", InfoType.LOCATION_NAME)
    result2 = crw_gen.generate(seed_state=seed2, max_hops=4, max_complexity=5)
    if result2:
        question2, _, config2 = result2
        print(f"Generated Question 2:\n{question2}")
        print(f"Final State Type: {config2[-1].info_type.name}")

    # --- Example 3: Backward Chaining aiming for a Numerical Value ---
    print("\n=== Example 3: Backward Chaining (Aim: Numerical from Table?) ===")
    result3 = bc_gen.generate(target_type=InfoType.NUMERICAL_VALUE, max_hops=3)
    if result3:
        question3, _, config3 = result3
        print(f"Generated Question 3:\n{question3}")
        print(f"Final State Type: {config3[-1].info_type.name}")
    else:
        print("Backward chaining failed to generate a 3-hop question for NUMERICAL_VALUE.")

    # --- Example 4: Forward Chaining starting with TABLE_DATA (Increased Hops) ---
    print("\n=== Example 4: Forward Chaining (Table Seed, More Hops) ===")
    planets_data = temp_bcg._find_seed_value_for_type(InfoType.TABLE_DATA)
    if planets_data:
        seed4 = State(planets_data, InfoType.TABLE_DATA)
        result4 = fc_gen.generate(seed_state=seed4, max_hops=4)
        if result4:
            question4, _, config4 = result4
            print(f"Generated Question 4:\n{question4}")
            print(f"Final State Type: {config4[-1].info_type.name}")
    else:
        print("Could not load planet data for Example 4.")

    # --- Example 5: Forward Chaining starting with TEXT_SNIPPET (Increased Hops) ---
    print("\n=== Example 5: Forward Chaining (Text Seed, More Hops) ===")
    curie_bio = temp_bcg._find_seed_value_for_type(InfoType.TEXT_SNIPPET)
    if curie_bio:
        seed5 = State(curie_bio, InfoType.TEXT_SNIPPET)
        result5 = fc_gen.generate(seed_state=seed5, max_hops=3)
        if result5:
            question5, _, config5 = result5
            print(f"Generated Question 5:\n{question5}")
            print(f"Final State Type: {config5[-1].info_type.name}")
    else:
        print("Could not load Curie bio data for Example 5.")

    # --- Example 6: Template-Based using Table Operations ---
    print("\n=== Example 6: Template-Based (Table Operations) ===")
    if planets_data:
        seed6 = State(planets_data, InfoType.TABLE_DATA)
        # Define template matching rule descriptions EXACTLY
        template6 = [
            # Note: The filter value 'Gas Giant' must be provided via input states normally.
            # Template generator cannot handle dynamic values like this well currently.
            # We need a rule like: Filter table {input0} where {input1} {input2} {input3}
            "Filter table {input0} to include only rows where column 'Type' equals 'Gas Giant'",  # This will likely fail unless a specific rule exists
            # Let's try a simpler template using AGGREGATE and LOOKUP
            # "Count the number of items in the primary list/table {input0}", # Removed - was CALCULATE
            "Calculate the sum of values in column 'Moons' of table {input0}",  # Requires explicit Aggregation rule for SUM
            "In table {input0}, find the value in column 'Type' for the row where column 'Name' matches 'Earth'.",  # Requires Lookup rule
        ]
        # --- Redefine Template 6 ---
        template6_new = [
            # Step 1: Aggregate - Calculate the sum of Moons
            # Requires the AGGREGATE_TABLE rule we defined
            "Calculate the sum of values in column 'Moons' of table {input0}.",
            # Step 2: Filter - Keep only planets with more than 10 moons
            # Requires the FILTER_TABLE rule
            "Filter table {input0} to include only rows where column 'Moons' greater than '10'.",
            # Step 3: Lookup - Find the Type of Saturn from the original table (or filtered?)
            # This requires careful state management by the template generator... let's lookup from original.
            # Requires TABLE_LOOKUP rule
            "In table {input0}, find the value in column 'Type' for the row where column 'Name' matches 'Saturn'.",
        ]

        print(f"Attempting Template 6: {template6_new}")
        result6 = template_gen.generate(seed_state=seed6, template=template6_new)
        if result6:
            question6, _, config6 = result6
            print(f"Generated Question 6:\n{question6}")
            print(f"Final State Type: {config6[-1].info_type.name}")
        else:
            print("Template-based generation failed for Example 6 (check rules, template steps, and generator logic).")
    else:
        print("Could not load planet data for Example 6.")

    # --- Example 7: Template-Based using Text Operations ---
    print("\n=== Example 7: Template-Based (Text Operations) ===")
    if curie_bio:
        seed7 = State(curie_bio, InfoType.TEXT_SNIPPET)
        template7 = [
            "From the text {input0}, extract the first date mentioned.",
            "Extract the year from the date {input0}",
        ]
        result7 = template_gen.generate(seed_state=seed7, template=template7)
        if result7:
            question7, _, config7 = result7
            print(f"Generated Question 7:\n{question7}")
            print(f"Final State Type: {config7[-1].info_type.name}")
        else:
            print("Template-based generation failed for Example 7 (check rules and template steps).")
    else:
        print("Could not load Curie bio data for Example 7.")


if __name__ == "__main__":
    main()
