import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import RULES_DB, InfoType, State
from src.generators import TemplateBasedGenerator


def run_examples():
    """Demonstrate the template-based generator with various templates."""
    generator = TemplateBasedGenerator(RULES_DB)

    examples = [
        {
            "seed": State("Mona Lisa", InfoType.ARTWORK_NAME),
            "template": [
                "Find the creator",
                "Find the birth date",
                "Find where {input0} is located",
            ],
            "description": "Artwork -> Creator -> Birth Date + Location",
        },
        {
            "seed": State("Paris", InfoType.CITY_NAME),
            "template": [
                "Find the country of {input0}",
                "Find the capital city of {input0}",
            ],
            "description": "City -> Country -> Capital City (cycle)",
        },
        {
            "seed": State("France", InfoType.COUNTRY_NAME),
            "template": [
                "Find the capital city of {input0}",
                "Find the population of {input0}",
            ],
            "description": "Country -> Capital -> Population",
        },
        {
            "seed": State("Eiffel Tower", InfoType.LOCATION_NAME),
            "template": [
                "Find the height or elevation of {input0}",
                "Find the city for the location {input0}",
                "Find the country of {input0}",
            ],
            "description": "Location -> Height + City -> Country",
        },
    ]

    for example in examples:
        print(f"\n\n{'='*70}")
        print(f"Template Based: {example['description']}")
        print(f"Seed: {example['seed'].value}")
        print(f"Template: {example['template']}")
        print(f"{'='*70}")

        result = generator.generate(seed_state=example["seed"], template=example["template"])

        if result:
            question_text, applied_rules, _ = result
            print(f"\nGenerated question with {len(applied_rules)} hops:")
            print(f"QUESTION: {question_text}")

        print(f"\n{'-'*70}")


if __name__ == "__main__":
    run_examples()
