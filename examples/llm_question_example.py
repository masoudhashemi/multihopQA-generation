import os
import sys
from typing import List, Optional, Tuple

sys.path.append("..")  # Add the parent directory to the path to import from src

# Import dotenv for environment variables
from dotenv import load_dotenv
from src.core import RULES_DB, InfoType, Rule, State
from src.generators import (
    BackwardChainingGenerator,
    ForwardChainingGenerator,
    GoalOrientedGenerator,
    LLMQuestionGenerator,
)
from src.utils import format_question

# Load environment variables from .env file
load_dotenv()

# Check if OpenRouter API key is set
if not os.getenv("OPENROUTER_API_KEY"):
    print("Please set the OPENROUTER_API_KEY environment variable or provide it as an argument.")
    print("Example 1: Create a .env file in the project root with your API key.")
    print("Example 2: OPENROUTER_API_KEY=your_key python examples/llm_question_example.py")
    sys.exit(1)


def main():
    print("LLM Question Generator Example")
    print("=" * 50)

    # Define example seed states
    seed_einstein = State("Albert Einstein", InfoType.PERSON_NAME)
    seed_mona_lisa = State("Mona Lisa", InfoType.ARTWORK_NAME)

    # Initialize base generators
    forward_generator = ForwardChainingGenerator(RULES_DB)
    goal_generator = GoalOrientedGenerator(RULES_DB)
    backward_generator = BackwardChainingGenerator(RULES_DB)

    # Get site information from environment variables
    site_url = os.getenv("SITE_URL")
    site_name = os.getenv("SITE_NAME")

    # Example 1: Using ForwardChainingGenerator as base
    print("\n\n" + "=" * 20 + " EXAMPLE 1: LLM with Forward Chaining (Einstein) " + "=" * 20)

    # Generate a trajectory using the forward chaining generator
    trajectory_result = forward_generator.generate(seed_einstein, max_hops=3)

    if trajectory_result:
        # Extract components from trajectory result
        original_question, applied_rules, configuration = trajectory_result

        # Initialize LLM generator with the forward chaining generator
        # Environment variables will be used automatically
        llm_forward_generator = LLMQuestionGenerator(forward_generator)

        # Generate the question using the LLM
        llm_question = llm_forward_generator.generate_from_trajectory(seed_einstein, applied_rules, configuration)

        # Print the original formatted question and the LLM-generated question
        print("\nOriginal formatted question:")
        print(original_question)
        print("\nLLM-generated question:")
        print(llm_question)
    else:
        print("Failed to generate trajectory with forward chaining.")

    # Example 2: Using GoalOrientedGenerator as base
    print("\n\n" + "=" * 20 + " EXAMPLE 2: LLM with Goal-Oriented (Mona Lisa) " + "=" * 20)

    # Generate a trajectory using the goal-oriented generator
    trajectory_result = goal_generator.generate(seed_mona_lisa, target_type=InfoType.PERSON_NAME, max_hops=3)

    if trajectory_result:
        # Extract components from trajectory result
        original_question, applied_rules, configuration = trajectory_result

        # Initialize LLM generator with the goal-oriented generator
        # Environment variables will be used automatically
        llm_goal_generator = LLMQuestionGenerator(goal_generator)

        # Generate the question using the LLM
        llm_question = llm_goal_generator.generate_from_trajectory(seed_mona_lisa, applied_rules, configuration)

        # Print the original formatted question and the LLM-generated question
        print("\nOriginal formatted question:")
        print(original_question)
        print("\nLLM-generated question:")
        print(llm_question)
    else:
        print("Failed to generate trajectory with goal-oriented generator.")

    # Example 3: Using BackwardChainingGenerator as base
    print("\n\n" + "=" * 20 + " EXAMPLE 3: LLM with Backward Chaining " + "=" * 20)

    # Generate a trajectory using the backward chaining generator
    trajectory_result = backward_generator.generate(target_type=InfoType.CITY_NAME, max_hops=3)

    if trajectory_result:
        # Extract components from trajectory result
        original_question, applied_rules, configuration = trajectory_result

        # Get the seed state (first state in configuration)
        seed_state = configuration[0] if configuration else None

        if seed_state:
            # Initialize LLM generator with the backward chaining generator
            # Environment variables will be used automatically
            llm_backward_generator = LLMQuestionGenerator(backward_generator)

            # Generate the question using the LLM
            llm_question = llm_backward_generator.generate_from_trajectory(seed_state, applied_rules, configuration)

            # Print the original formatted question and the LLM-generated question
            print("\nOriginal formatted question:")
            print(original_question)
            print("\nLLM-generated question:")
            print(llm_question)
        else:
            print("No seed state found in configuration.")
    else:
        print("Failed to generate trajectory with backward chaining generator.")

    # Example 4: Direct use of LLMQuestionGenerator with custom model
    print("\n\n" + "=" * 20 + " EXAMPLE 4: Direct use of LLMQuestionGenerator " + "=" * 20)

    # Get custom model from environment variable if available
    custom_model = os.getenv("LLM_MODEL")
    if custom_model:
        print(f"Using model from environment: {custom_model}")
    else:
        custom_model = "openai/gpt-4o"
        print(f"Using default model: {custom_model}")

    # Initialize LLM generator with custom model
    llm_direct_generator = LLMQuestionGenerator(forward_generator, model=custom_model)

    # Generate the question
    llm_question = llm_direct_generator.generate(seed_einstein, max_hops=3)

    if llm_question:
        print("\nLLM-generated question:")
        print(llm_question)
    else:
        print("Failed to generate question.")


if __name__ == "__main__":
    main()
