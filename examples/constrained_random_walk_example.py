import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import RULES_DB, InfoType, State
from src.generators import ConstrainedRandomWalkGenerator


def run_examples():
    """Demonstrate the constrained random walk generator with various complexity limits."""
    generator = ConstrainedRandomWalkGenerator(RULES_DB)

    examples = [
        {
            "seed": State("Albert Einstein", InfoType.PERSON_NAME),
            "max_hops": 5,
            "max_complexity": 3,
            "description": "Einstein with tight complexity budget (3)",
        },
        {
            "seed": State("Albert Einstein", InfoType.PERSON_NAME),
            "max_hops": 5,
            "max_complexity": 6,
            "description": "Einstein with medium complexity budget (6)",
        },
        {
            "seed": State("Mona Lisa", InfoType.ARTWORK_NAME),
            "max_hops": 4,
            "max_complexity": 2,
            "description": "Mona Lisa with very tight complexity budget (2)",
        },
        {
            "seed": State("Mona Lisa", InfoType.ARTWORK_NAME),
            "max_hops": 4,
            "max_complexity": 5,
            "description": "Mona Lisa with medium complexity budget (5)",
        },
        {
            "seed": State("Eiffel Tower", InfoType.LOCATION_NAME),
            "max_hops": 4,
            "max_complexity": 4,
            "description": "Eiffel Tower with medium complexity budget (4)",
        },
        {
            "seed": State("France", InfoType.COUNTRY_NAME),
            "max_hops": 3,
            "max_complexity": 3,
            "description": "France with medium complexity budget (3)",
        },
    ]

    for example in examples:
        print(f"\n\n{'='*70}")
        print(f"Constrained Random Walk: {example['description']}")
        print(
            f"Seed: {example['seed'].value}, Max Hops: {example['max_hops']}, Max Complexity: {example['max_complexity']}"
        )
        print(f"{'='*70}")

        result = generator.generate(
            seed_state=example["seed"], max_hops=example["max_hops"], max_complexity=example["max_complexity"]
        )

        if result:
            question_text, applied_rules, _ = result
            total_complexity = sum(rule.complexity for rule in applied_rules)
            print(f"\nGenerated question with {len(applied_rules)} hops (total complexity: {total_complexity}):")
            print(f"QUESTION: {question_text}")

        print(f"\n{'-'*70}")


if __name__ == "__main__":
    run_examples()
