# MultihopQA Question Generator

A modular Python framework for generating multi-hop questions using various strategies, intended for testing question-answering systems.

## Generation Strategies

This project provides multiple strategies for generating multi-hop questions:

1. **Forward Chaining**: Randomly selects applicable rules at each step, starting from a seed entity.
2. **Template-Based**: Follows a predefined template of operations to generate a structured question.
3. **Constrained Random Walk**: Similar to forward chaining but with a complexity budget limit.
4. **Goal-Oriented**: Prioritizes rules that lead toward a specific target information type.
5. **Backward Chaining**: Plans backward from a target type, then executes forward.

## Running Examples

To run specific strategy examples:

```bash
python examples/forward_chaining_example.py
python examples/template_based_example.py
python examples/constrained_random_walk_example.py
python examples/goal_oriented_example.py
python examples/backward_chaining_example.py
```

## Core Concepts

- **State**: Represents information at a particular step (e.g., "Paris" as a CITY_NAME)
- **Rule**: Defines a transition between states using operators
- **InfoType**: Categorizes the type of information (PERSON_NAME, DATE, etc.)
- **OperatorType**: Categorizes the tool/operation used (SEARCH, CALCULATE, etc.)

## Customizing

- Add new rules in `src/core/rules.py`
- Enhance operator implementations in the `src/operators/` directory
- Create new generation strategies by subclassing `QuestionGenerator`

## Example Output

Questions are formatted as a sequence of operations:

Consider the starting entity: 'Albert Einstein'. Please perform the following sequence of operations:

1. Find the birth date of the initial entity ('Albert Einstein')
2. Find the start date of the event the initial entity ('WW2')
3. Calculate the time duration in years between the result from step 1 and the result from step 2
