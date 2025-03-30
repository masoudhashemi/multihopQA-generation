import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import RULES_DB, InfoType, State
from src.generators import ForwardChainingGenerator


def run_examples():
    """Demonstrate the forward chaining generator with various seeds."""
    generator = ForwardChainingGenerator(RULES_DB)

    seeds = [
        State("Albert Einstein", InfoType.PERSON_NAME),
        State("Marie Curie", InfoType.PERSON_NAME),
        State("Eiffel Tower", InfoType.LOCATION_NAME),
        State("Mona Lisa", InfoType.ARTWORK_NAME),
        State("France", InfoType.COUNTRY_NAME),
        State("Paris", InfoType.CITY_NAME),
        State("WW2", InfoType.EVENT_NAME),
    ]

    hop_counts = [2, 3, 4]

    for seed in seeds:
        for hops in hop_counts:
            print(f"\n\n{'='*70}")
            print(f"Forward Chaining: Seed '{seed.value}' with {hops} hops")
            print(f"{'='*70}")

            result = generator.generate(seed_state=seed, max_hops=hops)

            if result:
                question_text, applied_rules, _ = result
                print(f"\nGenerated question with {len(applied_rules)} hops:")
                print(f"QUESTION: {question_text}")

            print(f"\n{'-'*70}")


if __name__ == "__main__":
    run_examples()
