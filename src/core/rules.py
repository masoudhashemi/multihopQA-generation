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
        InfoType.DURATION,  # Or NUMERICAL_VALUE if duration is just years
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
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.NUMERICAL_VALUE,
        1,
        "Calculate the difference between {input0} and {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.NUMERICAL_VALUE,
        1,
        "Calculate the product of {input0} and {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.NUMERICAL_VALUE,
        1,
        "Calculate the absolute difference between {input0} and {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.DATE, InfoType.DATE),
        InfoType.NUMERICAL_VALUE,
        2,
        "Calculate the number of days between {input0} and {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.DATE, InfoType.NUMERICAL_VALUE),
        InfoType.DATE,
        2,
        "Calculate the date that is {input1} days after {input0}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.DATE,),
        InfoType.NUMERICAL_VALUE,
        1,
        "Extract the year from the date {input0}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.NUMERICAL_VALUE,
        2,
        "Calculate what percentage {input0} is of {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.NUMERICAL_VALUE, InfoType.NUMERICAL_VALUE),
        InfoType.BOOLEAN,
        1,
        "Determine if {input0} is greater than {input1}",
    ),
    Rule(
        OperatorType.CALCULATE,
        (InfoType.DATE, InfoType.DATE),
        InfoType.BOOLEAN,
        1,
        "Determine if date {input0} is earlier than date {input1}",
    ),
    Rule( # Added for equality check
        OperatorType.CALCULATE,
        (InfoType.TEXT_SNIPPET, InfoType.TEXT_SNIPPET), # Example: Compare two extracted names
        InfoType.BOOLEAN,
        1,
        "Determine if {input0} and {input1} are equal.",
    ),
    # List/Table Aggregations (Using TABLE_DATA as input proxy for list)
    # These rules were ill-defined; use AGGREGATE_TABLE operator instead.
    # Rule(
    #     OperatorType.CALCULATE,
    #     (InfoType.TABLE_DATA,),
    #     InfoType.NUMERICAL_VALUE,
    #     2,
    #     "Calculate the sum of the primary numerical list in {input0}",
    # ),
    # Rule(
    #     OperatorType.CALCULATE,
    #     (InfoType.TABLE_DATA,),
    #     InfoType.NUMERICAL_VALUE,
    #     2,
    #     "Calculate the average of the primary numerical list in {input0}",
    # ),
    # Rule(
    #     OperatorType.CALCULATE,
    #     (InfoType.TABLE_DATA,),
    #     InfoType.NUMERICAL_VALUE,
    #     2,
    #     "Find the maximum value in the primary numerical list in {input0}",
    # ),
    # Rule(
    #     OperatorType.CALCULATE,
    #     (InfoType.TABLE_DATA,),
    #     InfoType.NUMERICAL_VALUE,
    #     1,
    #     "Count the number of items in the primary list/table {input0}",
    # ),
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
    # --- Table and Text Operations ---
    # Table Lookup (Example: Find population of a specific city in a table of cities)
    Rule(
        OperatorType.TABLE_LOOKUP,
        # Input: Table, Key Column Name, Key Value, Target Column Name
        (InfoType.TABLE_DATA, InfoType.TEXT_SNIPPET, InfoType.TEXT_SNIPPET, InfoType.TEXT_SNIPPET),
        InfoType.NUMERICAL_VALUE,  # Output type depends on the column
        2,
        "In table {input0}, find the value in column '{input3}' for the row where column '{input1}' matches '{input2}'.",
    ),
    # Table Filtering (Example: Filter planets table to show only gas giants)
    Rule(
        OperatorType.FILTER_TABLE,
        # Input: Table, Column Name, Comparison Type (str), Value to Compare
        (InfoType.TABLE_DATA, InfoType.TEXT_SNIPPET, InfoType.TEXT_SNIPPET, InfoType.TEXT_SNIPPET),
        InfoType.TABLE_DATA,
        3,
        "Filter table {input0} to include only rows where column '{input1}' {input2} '{input3}'.",
    ),
    # Table Aggregation (Example: Sum a 'Sales' column in a table)
    Rule(
        OperatorType.AGGREGATE_TABLE,
        # Input: Table, Aggregation Function (str), Column Name to Aggregate
        (InfoType.TABLE_DATA, InfoType.TEXT_SNIPPET, InfoType.TEXT_SNIPPET),
        InfoType.NUMERICAL_VALUE,
        2,
        "Calculate the {input1} of values in column '{input2}' of table {input0}.",
    ),
    # Text Extraction (Example: Extract birth date from a biography snippet)
    Rule(
        OperatorType.EXTRACT_INFO,
        (InfoType.TEXT_SNIPPET,),  # Input: Text Only
        InfoType.TEXT_SNIPPET,  # Output is generally text, might need conversion later
        3,  # Extraction can be complex
        "From the text {input0}, extract the first entity of type 'Person'.",  # Specify entity in description
    ),
    Rule(
        OperatorType.EXTRACT_INFO,
        (InfoType.TEXT_SNIPPET,),  # Input: Text Only
        InfoType.DATE,
        3,
        "From the text {input0}, extract the first date mentioned.",
    ),
    # Add more specific extraction rules as needed
    # Rule(OperatorType.EXTRACT_INFO, (InfoType.TEXT_SNIPPET,), InfoType.LOCATION_NAME, 3, "From the text {input0}, extract the first location."),
    # --- New Multi-Input Search Rules ---
    Rule(
        OperatorType.SEARCH_RELATIONSHIP,
        (InfoType.PERSON_NAME, InfoType.PERSON_NAME),
        InfoType.RELATIONSHIP_DESCRIPTION,
        3, # Higher complexity due to reasoning
        "What is the relationship between {input0} and {input1}?",
    ),
    Rule(
        OperatorType.SEARCH_CONTEXTUAL,
        (InfoType.CONCEPT, InfoType.LOCATION_NAME),
        InfoType.EVENT_DESCRIPTION,
        3,
        "Find events related to {input0} that occurred in {input1}",
    ),
]
