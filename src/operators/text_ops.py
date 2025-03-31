import datetime
import re
from typing import Any, List, Optional

from ..core import InfoType, State

# Basic date patterns (add more as needed)
DATE_PATTERNS = [
    r"\b(\d{4}-\d{2}-\d{2})\b",  # YYYY-MM-DD
    r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",  # D Month YYYY
    r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4})\b",  # Month D, YYYY
]
DATE_FORMATS = ["%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"]


def _try_parse_date(text: str) -> Optional[datetime.date]:
    """Attempt to parse a string using known date formats."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def simulate_extract_info(rule_description: str, args: List[Any], expected_output_type: InfoType) -> Optional[State]:
    """Simulates extracting information from a text snippet. Uses basic regex."""
    if len(args) != 1:
        print("  -> Error: EXTRACT_INFO expects 1 argument (text_snippet).")
        return None

    text = args[0]
    # Infer entity type from description or expected output
    entity_type_str = "unknown"
    desc_lower = rule_description.lower()
    if "date mentioned" in desc_lower or expected_output_type == InfoType.DATE:
        entity_type_str = "date"
    elif "person" in desc_lower or expected_output_type == InfoType.PERSON_NAME:
        entity_type_str = "person"
    elif "location" in desc_lower or expected_output_type == InfoType.LOCATION_NAME:
        entity_type_str = "location"
    # Add other inferences...

    print(f"  Simulating EXTRACT_INFO: Find first '{entity_type_str}' in text: '{text[:50]}...'")

    if not isinstance(text, str):
        print(f"  -> Error: Input text must be a string, got {type(text)}.")
        return None
    # No longer need to check entity_type_str input
    # if not isinstance(entity_type_str, str): ...

    found_value = None  # Changed from found_value_str
    extracted_type = InfoType.TEXT_SNIPPET
    entity_type_lower = entity_type_str.lower()  # Use inferred type

    # --- Basic Extraction Logic ---
    if "date" in entity_type_lower:
        found_value_str = None  # Reset for this block
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found_value_str = match.group(1)
                parsed_date = _try_parse_date(found_value_str)
                if parsed_date:
                    found_value = parsed_date
                    extracted_type = InfoType.DATE
                    print(f"  -> Found and parsed date: {found_value}")
                    break
                else:
                    found_value = found_value_str
                    extracted_type = InfoType.TEXT_SNIPPET
                    print(f"  -> Found date string: {found_value}")
                    break
        # No explicit 'pass' needed here if found_value holds the result

    elif "person" in entity_type_lower:
        # Basic pattern for multi-word capitalized names, optionally preceded by titles
        match = re.search(r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)?\s?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text)
        if match:
            found_value = match.group(1)
            extracted_type = InfoType.PERSON_NAME
            print(f"  -> Found person: {found_value}")

    elif "location" in entity_type_lower or "place" in entity_type_lower:
        # Basic pattern for multi-word capitalized names, optionally after prepositions
        match = re.search(r"\b(?:in|at|near|from)\s+((?:[A-Z][a-zA-Z]+\s*)+)\b", text)
        if match:
            found_value = match.group(1).strip()
            extracted_type = InfoType.LOCATION_NAME
            print(f"  -> Found location: {found_value}")

    # Add more basic extraction patterns here...

    # --- Post-processing and Type Handling ---
    if found_value is None:
        print(f"  -> Extraction failed for type '{entity_type_str}'.")
        return None

    print(f"  -> Extracted value: {found_value} (as type {extracted_type.name})")

    final_value = found_value
    final_type = extracted_type

    if extracted_type == InfoType.TEXT_SNIPPET and expected_output_type != InfoType.TEXT_SNIPPET:
        print(f"  -> Extracted text, but rule expects {expected_output_type.name}. Attempting conversion...")
        if expected_output_type == InfoType.DATE:
            parsed = _try_parse_date(str(found_value))
            if parsed:
                final_value = parsed
                final_type = InfoType.DATE
                print("  -> Conversion to DATE successful.")
            else:
                print("  -> Conversion to DATE failed.")
                pass
        elif expected_output_type == InfoType.NUMERICAL_VALUE:
            try:
                cleaned_str = re.sub(r"[,\s]", "", str(found_value))
                final_value = float(cleaned_str) if "." in cleaned_str else int(cleaned_str)
                final_type = InfoType.NUMERICAL_VALUE
                print("  -> Conversion to NUMERICAL_VALUE successful.")
            except ValueError:
                print("  -> Conversion to NUMERICAL_VALUE failed.")
                pass

    elif extracted_type != expected_output_type and expected_output_type == InfoType.TEXT_SNIPPET:
        print(
            f"  -> Extracted specific type {extracted_type.name}, but rule expects TEXT_SNIPPET. Converting value to string."
        )
        final_value = str(final_value)
        final_type = InfoType.TEXT_SNIPPET

    elif final_type != expected_output_type and expected_output_type != InfoType.TEXT_SNIPPET:
        print(
            f"  -> Warning: Final extracted type {final_type.name} does not match expected rule output type {expected_output_type.name}. Returning extracted type anyway."
        )

    return State(final_value, final_type)
