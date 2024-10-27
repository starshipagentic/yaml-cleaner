# YAML Heuristics and Processing Rules

## Existing Code Rules

1. The YAML cleaner uses `ruamel.yaml` library for parsing and dumping YAML.
2. The cleaner preserves quotes, unicode characters, and maintains a maximum line width.
3. It adds missing colons to keys without values.
4. It fixes indentation issues in the YAML structure.
5. It removes leading characters that are not whitespace or word characters.

## Detailed Cleaning Rules

1. Initialization:
   - Uses `ruamel.yaml` library for YAML processing.
   - Sets indentation for mapping, sequence, and offset.
   - Allows unicode characters.
   - Disables default flow style.
   - Sets maximum line width.
   - Preserves quotes in the YAML.

2. Adding Missing Colons:
   - Checks each line for missing colons after keys.
   - Handles quoted strings and single words as keys.
   - Adds colons to any first word or quoted words without a colon
   - Preserves existing colons and list item markers.

3. Fixing Indentation:
   - Maintains an indentation stack to track nested structures.
   - Adjusts indentation based on the presence of keys.
   - Increases indentation for new blocks (lines ending with a colon) or even a single value without a colon, unless its just a single scalar in the whole yaml file
   - Uses consistent indentation for lines within the same block.

4. Removing Leading Characters:
   - preserves leading whitespace from each line.
   - Removes problematic leading characters like '-' or '*'.
   - Preserves original indentation after removing characters.

5. Main Cleaning Process:
   - Applies the above rules in sequence of Remove Leading Chars, Add colons, Fix Indentation.
   - Parses the fixed YAML using `ruamel.yaml`.
   - Formats the parsed data back into a properly structured YAML.

6. Error Handling:
   - Catches and reports any exceptions during the cleaning process.
   - Returns a `YAMLResult` object containing the cleaned YAML, parsed data, and any error messages.

## Handling Scalar, List, and Dict Types

We're returning a tuple of (datatype, dataobject), where datatype is:  

Proposed structure:

YAML_TYPE_SCALAR = 1
YAML_TYPE_LIST = 2
YAML_TYPE_DICT = 3

This approach allows us to distinguish between scalars, lists, and dictionaries while preserving the original data structure.

Considerations:
- This method handles the top-level structure. For nested structures, we might need a recursive approach.
- handle empty lists or dictionaries as dataobject is None
- For more complex YAML structures (like sets or ordered dicts), we might need to expand our type constants.

Next steps:
1. Implement this approach in the YAML processing code.
2. Test with various YAML structures to ensure correct type identification.
3. Update any code that consumes the processed YAML to handle the new tuple structure.
