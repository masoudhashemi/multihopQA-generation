import os
import sys

# Import dotenv for environment variables
from dotenv import load_dotenv

from src.core import RULES_DB, InfoType, State
from src.generators import (
    BackwardChainingGenerator,
    ConstrainedRandomWalkGenerator,
    ForwardChainingGenerator,
    GoalOrientedGenerator,
    LLMQuestionGenerator,
    TemplateBasedGenerator,
)

# Load environment variables from .env file
load_dotenv()


def main():
    """Main function to demonstrate the question generators."""
    print("MultihopQA Question Generator Demonstration")
    print("=" * 50)

    # Define some seed states for examples
    seed_einstein = State("Albert Einstein", InfoType.PERSON_NAME)
    seed_eiffel = State("Eiffel Tower", InfoType.LOCATION_NAME)
    seed_mona_lisa = State("Mona Lisa", InfoType.ARTWORK_NAME)
    seed_france = State("France", InfoType.COUNTRY_NAME)
    seed_paris = State("Paris", InfoType.CITY_NAME)
    seed_ww2 = State("WW2", InfoType.EVENT_NAME)

    # Initialize all generators with the same rules
    forward_generator = ForwardChainingGenerator(RULES_DB)
    template_generator = TemplateBasedGenerator(RULES_DB)
    constrained_generator = ConstrainedRandomWalkGenerator(RULES_DB)
    goal_generator = GoalOrientedGenerator(RULES_DB)
    backward_generator = BackwardChainingGenerator(RULES_DB)

    # Example 1: Forward Chaining with Einstein
    print("\n\n" + "=" * 20 + " EXAMPLE 1: Forward Chaining (Einstein) " + "=" * 20)
    forward_generator.generate(seed_state=seed_einstein, max_hops=3)

    # Example 2: Template Based with Mona Lisa
    print("\n\n" + "=" * 20 + " EXAMPLE 2: Template Based " + "=" * 20)
    template_ml = [
        "Find the creator",  # Input: ArtworkName -> Output: PersonName
        "Find the birth date",  # Input: PersonName -> Output: Date
        "Find where {input0} is located",  # Input: ArtworkName -> Output: LocationName
    ]
    template_generator.generate(seed_state=seed_mona_lisa, template=template_ml)

    # Example 3: Constrained Random Walk with Eiffel Tower
    print("\n\n" + "=" * 20 + " EXAMPLE 3: Constrained Random Walk " + "=" * 20)
    constrained_generator.generate(seed_state=seed_eiffel, max_hops=4, max_complexity=4)

    # Example 4: Goal-Oriented Walk
    print("\n\n" + "=" * 20 + " EXAMPLE 4: Goal-Oriented Walk (Einstein -> DURATION) " + "=" * 20)
    goal_generator.generate(seed_state=seed_einstein, target_type=InfoType.DURATION, max_hops=5)

    # Example 5: Backward Chaining
    print("\n\n" + "=" * 20 + " EXAMPLE 5: Backward Chaining (Target: CITY_NAME) " + "=" * 20)
    backward_generator.generate(target_type=InfoType.CITY_NAME, max_hops=4)

    # Example 6: LLM Question Generator (if OPENROUTER_API_KEY is set)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print("\n\n" + "=" * 20 + " EXAMPLE 6: LLM Question Generation " + "=" * 20)
        # Initialize LLM generator with the forward chaining generator
        # Environment variables will be used automatically
        llm_generator = LLMQuestionGenerator(forward_generator)
        
        # Generate a question using the LLM
        llm_question = llm_generator.generate(seed_einstein, max_hops=3)
        
        if llm_question:
            print("\nLLM-generated question:")
            print(llm_question)
        else:
            print("Failed to generate LLM question.")
    else:
        print("\n\n" + "=" * 20 + " EXAMPLE 6: LLM Question Generation (Skipped) " + "=" * 20)
        print("Set OPENROUTER_API_KEY environment variable to use the LLM Question Generator.")
        print("You can create a .env file in the project root with your API key.")


if __name__ == "__main__":
    main()
