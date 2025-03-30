import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import RULES_DB, InfoType, State
from src.generators import GoalOrientedGenerator


def run_examples():
    """Demonstrate the goal-oriented generator with various seeds and targets."""
    generator = GoalOrientedGenerator(RULES_DB)

    examples = [
        {
            "seed": State("Albert Einstein", InfoType.PERSON_NAME),
            "target": InfoType.DURATION,
            "max_hops": 5,
            "description": "Einstein to Duration (likely birth date -> event date -> duration)",
        },
        {
            "seed": State("Marie Curie", InfoType.PERSON_NAME),
            "target": InfoType.LOCATION_NAME,
            "max_hops": 3,
            "description": "Curie to Location (birth place or related location)",
        },
        {
            "seed": State("Mona Lisa", InfoType.ARTWORK_NAME),
            "target": InfoType.COUNTRY_NAME,
            "max_hops": 4,
            "description": "Mona Lisa to Country (location -> country)",
        },
        {
            "seed": State("WW2", InfoType.EVENT_NAME),
            "target": InfoType.NUMERICAL_VALUE,
            "max_hops": 4,
            "description": "WW2 to Numerical Value (dates -> calculations or locations -> population)",
        },
        {
            "seed": State("France", InfoType.COUNTRY_NAME),
            "target": InfoType.PERSON_NAME,
            "max_hops": 5,
            "description": "France to Person (capital -> artwork -> creator)",
        },
    ]

    for example in examples:
        print(f"\n\n{'='*70}")
        print(f"Goal-Oriented: {example['description']}")
        print(f"Seed: {example['seed'].value} -> Target: {example['target'].name}")
        print(f"Max Hops: {example['max_hops']}")
        print(f"{'='*70}")

        result = generator.generate(
            seed_state=example["seed"], target_type=example["target"], max_hops=example["max_hops"]
        )

        if result:
            question_text, applied_rules, _ = result
            print(f"\nGenerated question with {len(applied_rules)} hops:")
            print(f"QUESTION: {question_text}")

        print(f"\n{'-'*70}")


if __name__ == "__main__":
    run_examples()
