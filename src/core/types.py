import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class InfoType(Enum):
    """Defines the possible types of information a State can hold."""

    PERSON_NAME = auto()
    DATE = auto()
    LOCATION_NAME = auto()
    CITY_NAME = auto()
    COUNTRY_NAME = auto()
    NUMERICAL_VALUE = auto()
    EVENT_NAME = auto()
    ARTWORK_NAME = auto()
    ORGANIZATION_NAME = auto()
    CONCEPT = auto()
    TEXT_SNIPPET = auto()
    URL = auto()
    TABLE_DATA = auto()  # Represents structured data, e.g., list of dicts
    CODE_OUTPUT = auto()  # Output from simulated code execution
    DURATION = auto()  # Represents a time duration, e.g., in years
    CURRENCY_VALUE = auto()
    BOOLEAN = auto()
    OTHER = auto()  # Generic fallback type


class OperatorType(Enum):
    """Defines the types of tools/operations available."""

    SEARCH = auto()  # Simulate web search
    CALCULATE = auto()  # Simulate mathematical calculation
    RUN_CODE = auto()  # Simulate running a code snippet
    TABLE_LOOKUP = auto()  # Simulate looking up data in a table
    EXTRACT_INFO = auto()  # Simulate extracting specific info from text
    FILTER_TABLE = auto()  # Simulate filtering rows from a table
    AGGREGATE_TABLE = auto()  # Simulate calculating aggregates (sum, avg) over table columns


class State:
    """Represents a piece of information (value and type) at a specific hop."""

    def __init__(
        self,
        value: Any,
        info_type: InfoType,
        source_rule: Optional["Rule"] = None,
        source_inputs: Optional[List["State"]] = None,
    ):
        """
        Initializes a State.

        Args:
            value: The actual data value (e.g., "Paris", 1984, 3.14).
            info_type: The type of information (from InfoType enum).
            source_rule: The Rule that generated this state (for provenance).
            source_inputs: The list of State objects used as input to the source_rule.
        """
        self.value = value
        self.info_type = info_type
        # Provenance: helps in formatting the final question
        self.source_rule = source_rule
        self.source_inputs = source_inputs if source_inputs else []

    def __repr__(self) -> str:
        """Provides a concise string representation of the State."""
        # Truncate long values for readability in logs/debug output
        val_repr = repr(self.value)
        if len(val_repr) > 50:
            val_repr = val_repr[:47] + "..."
        return f"State(value={val_repr}, type={self.info_type.name})"


class Rule:
    """Defines a transition rule for generating a new State."""

    def __init__(
        self,
        operator: OperatorType,
        input_types: Tuple[InfoType, ...],
        output_type: InfoType,
        complexity: int,
        description_template: str,
    ):
        """
        Initializes a Rule.

        Args:
            operator: The type of tool/operation this rule uses.
            input_types: A tuple of InfoType enums specifying the required input state types.
            output_type: The InfoType of the state generated by this rule.
            complexity: An integer representing the estimated difficulty/cost.
            description_template: A string template used for formatting this step
                                  into a natural language question. Placeholders like
                                  {input0}, {input1}, {output} can be used.
        """
        self.operator = operator
        self.input_types = input_types
        self.output_type = output_type
        self.complexity = complexity
        self.description_template = description_template

    def __repr__(self) -> str:
        """Provides a concise string representation of the Rule."""
        inputs = ", ".join(it.name for it in self.input_types)
        return f"Rule({self.operator.name}: ({inputs}) -> " f"{self.output_type.name}, complexity={self.complexity})"
