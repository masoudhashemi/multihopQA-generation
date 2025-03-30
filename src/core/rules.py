from typing import List

from .types import InfoType, OperatorType, Rule

# Rule(OperatorType, InputTypesTuple, OutputType, Complexity, DescriptionTemplate)
# Description templates use {input0}, {input1}, ..., {output}

RULES_DB: List[Rule] = [
    # Search Rules
    Rule(OperatorType.SEARCH, (InfoType.PERSON_NAME,), InfoType.DATE, 1, "Find the birth date of {input0}"),
    Rule(OperatorType.SEARCH, (InfoType.PERSON_NAME,), InfoType.LOCATION_NAME, 1, "Find the birth place of {input0}"),
    Rule(
        OperatorType.SEARCH,
        (InfoType.PERSON_NAME,),
        InfoType.CONCEPT,
        2,
        "Find a notable concept or achievement associated with {input0}",
    ),
    Rule(OperatorType.SEARCH, (InfoType.EVENT_NAME,), InfoType.DATE, 1, "Find the start date of the event {input0}"),
    Rule(
        OperatorType.SEARCH,
        (InfoType.EVENT_NAME,),
        InfoType.LOCATION_NAME,
        1,
        "Find the primary location of the event {input0}",
    ),
    Rule(
        OperatorType.SEARCH,
        (InfoType.LOCATION_NAME,),
        InfoType.CITY_NAME,
        1,
        "Identify the city for the location {input0}",
    ),
    Rule(
        OperatorType.SEARCH,
        (InfoType.LOCATION_NAME,),
        InfoType.COUNTRY_NAME,
        1,
        "Identify the country for the location {input0}",
    ),
    Rule(
        OperatorType.SEARCH,
        (InfoType.LOCATION_NAME,),
        InfoType.NUMERICAL_VALUE,
        1,
        "Find the height or elevation of {input0}",
    ),
    Rule(OperatorType.SEARCH, (InfoType.CITY_NAME,), InfoType.NUMERICAL_VALUE, 1, "Find the population of {input0}"),
    Rule(OperatorType.SEARCH, (InfoType.COUNTRY_NAME,), InfoType.CITY_NAME, 1, "Find the capital city of {input0}"),
    Rule(OperatorType.SEARCH, (InfoType.ARTWORK_NAME,), InfoType.LOCATION_NAME, 1, "Find where {input0} is located"),
    Rule(OperatorType.SEARCH, (InfoType.ARTWORK_NAME,), InfoType.PERSON_NAME, 1, "Find the creator of {input0}"),
    Rule(
        OperatorType.SEARCH, (InfoType.COUNTRY_NAME,), InfoType.TEXT_SNIPPET, 1, "Find the currency used in {input0}"
    ),  # Example where output might not be specific type
    Rule(
        OperatorType.SEARCH, (InfoType.CITY_NAME,), InfoType.COUNTRY_NAME, 1, "Find the country of {input0}"
    ),  # Added Rule
    # Calculation Rules
    Rule(
        OperatorType.CALCULATE,
        (InfoType.DATE, InfoType.DATE),
        InfoType.DURATION,
        2,
        "Calculate the time duration in years between {input0} and {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.NUMERICAL_VALUE,
        1,
        "Calculate the sum of {input0} and {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.NUMERICAL_VALUE,
        1,
        "Calculate the result of dividing {input0} by {input1}",
    ),
    # Code Rules (Example - requires specific input handling in _execute_rule)
    Rule(
        OperatorType.RUN_CODE,
        (InfoType.TABLE_DATA,),
        InfoType.NUMERICAL_VALUE,
        3,
        "Using code, find the maximum value in the list {input0}",
    ),
    Rule(
        OperatorType.RUN_CODE,
        (InfoType.TABLE_DATA,),
        InfoType.TABLE_DATA,
        3,
        "Using code, filter the list {input0} based on criteria X",
    ),  # Criteria X needs definition
]
