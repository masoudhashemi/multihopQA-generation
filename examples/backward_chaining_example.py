import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import RULES_DB, InfoType, State
from src.generators import BackwardChainingGenerator


def run_examples():
    """Demonstrate the backward chaining generator with various target types."""
    generator = BackwardChainingGenerator(RULES_DB)

    targets = [
        {"type": InfoType.CITY_NAME, "max_hops": 3, "description": "City (e.g., capital of country)"},
        {"type": InfoType.DATE, "max_hops": 3, "description": "Date (e.g., birth date of person)"},
        {"type": InfoType.NUMERICAL_VALUE, "max_hops": 3, "description": "Numerical Value (e.g., population, height)"},
        {"type": InfoType.DURATION, "max_hops": 5, "description": "Duration (requires dates & calculation)"},
        {"type": InfoType.PERSON_NAME, "max_hops": 3, "description": "Person (e.g., creator of artwork)"},
        {"type": InfoType.COUNTRY_NAME, "max_hops": 3, "description": "Country (e.g., country of city/location)"},
    ]

    for target in targets:
        print(f"\n\n{'='*70}")
        print(f"Backward Chaining: Target '{target['type'].name}' - {target['description']}")
        print(f"Max Hops: {target['max_hops']}")
        print(f"{'='*70}")

        result = generator.generate(target_type=target["type"], max_hops=target["max_hops"])

        if result:
            question_text, applied_rules, configuration = result
            seed = configuration[0]
            print(f"\nGenerated question with seed '{seed.value}' and {len(applied_rules)} hops:")
            print(f"QUESTION: {question_text}")
        else:
            print(f"\nFailed to generate question for target type {target['type'].name}")

        print(f"\n{'-'*70}")


if __name__ == "__main__":
    run_examples()
