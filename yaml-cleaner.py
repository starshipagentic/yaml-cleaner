from ruamel.yaml import YAML
from io import StringIO
import re
from typing import Tuple, Optional, Any, List, Dict, Union
from dataclasses import dataclass
from yaml_test_cases import get_test_cases

# YAML type constants
YAML_TYPE_SCALAR = 1
YAML_TYPE_LIST = 2
YAML_TYPE_DICT = 3

@dataclass
class YAMLResult:
    """Class to hold the result of YAML processing."""
    data: Optional[Any]
    cleaned_yaml: Optional[str]
    error_message: Optional[str]
    yaml_type: int
    
    def is_valid(self) -> bool:
        """Check if the YAML processing was successful."""
        return self.data is not None and self.cleaned_yaml is not None

    def get_type_name(self) -> str:
        """Return a human-readable name for the YAML type."""
        if self.yaml_type == YAML_TYPE_SCALAR:
            return "Scalar"
        elif self.yaml_type == YAML_TYPE_LIST:
            return "List"
        elif self.yaml_type == YAML_TYPE_DICT:
            return "Dictionary"
        else:
            return "Unknown"

class YAMLCleaner:
    def __init__(self, 
                 indent_mapping: int = 2,
                 indent_sequence: int = 4,
                 indent_offset: int = 2,
                 max_width: int = 80):
        """Initialize the YAML cleaner with formatting options."""
        self.yaml = YAML()
        self.yaml.indent(mapping=indent_mapping, 
                        sequence=indent_sequence, 
                        offset=indent_offset)
        self.yaml.allow_unicode = True
        self.yaml.default_flow_style = False
        self.yaml.width = max_width
        self.yaml.preserve_quotes = True

    def _add_missing_colons(self, lines: List[str]) -> List[str]:
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Check if the line starts with a quoted string or a single word
            match = re.match(r'^(\s*)(".*?"|\'.*?\'|\S+)(.*)$', line)
            if match:
                indent, key_part, rest = match.groups()
                rest = rest.lstrip()
                if not key_part.endswith(':'):
                    answer = f"{indent}{key_part}: {rest}"
                    fixed_lines.append(answer)
                else:
                    answer = line
                    fixed_lines.append(answer)
            elif ':' not in stripped and not stripped.startswith('-'):
                answer = f"{line}: "
                fixed_lines.append(answer)
            else:
                answer = line
                fixed_lines.append(answer)
        
        # DO NOT REMOVE THESE COMMENTS
        # remove the colons if we probably meant a scalar or just a list.
        # for instance if we wind up with:
        # item1:
        # item2:
        # item3:
        #
        # then we probably just have a list.
        #
        # and just:
        # new york:
        #
        # probably meant:
        # new york
        # Search for keys with no subvalues and remove colons
        cleaned_lines = []
        i = 0
        while i < len(fixed_lines):
            line = fixed_lines[i].rstrip()
            if line.endswith(':'):
                # Check if this is the last line or if the next line has the same or less indentation
                if i == len(fixed_lines) - 1 or len(fixed_lines[i+1]) - len(fixed_lines[i+1].lstrip()) <= len(line) - len(line.lstrip()):
                    # Check if it's not part of a list
                    if not any(l.strip().startswith('-') for l in fixed_lines):
                        # Remove the colon for scalar
                        cleaned_lines.append(line[:-1])
                    else:
                        # Keep the colon for list items
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
            i += 1

        return cleaned_lines

    def _fix_indentation(self, lines: List[str]) -> List[str]:
        fixed_lines = []
        indent_stack = [0]
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue

            current_indent = len(line) - len(line.lstrip())
            
            # Adjust indent stack based on current indentation
            while indent_stack and current_indent < indent_stack[-1]:
                indent_stack.pop()
            
            if ':' in stripped:
                key, value = [part.strip() for part in stripped.split(':', 1)]
                
                # Use the current indentation level
                proper_indent = indent_stack[-1] if indent_stack else 0
                answer = ' ' * proper_indent + stripped
                fixed_lines.append(answer)
                
                # If this is a new block (no value after colon), increase indentation for next line
                if not value:
                    indent_stack.append(current_indent + 2)
            else:
                # For lines without colon, use the last indentation level
                proper_indent = indent_stack[-1] if indent_stack else 0
                answer = ' ' * proper_indent + stripped
                fixed_lines.append(answer)

        return fixed_lines

    def _remove_leading_characters(self, lines: List[str]) -> List[str]:
        cleaned_lines = []
        for line in lines:
            # Strip leading whitespace
            stripped_line = line.lstrip()
            
            # Check if the line starts with a problematic character
            if stripped_line and stripped_line[0] in '-*':
                # Remove the first character
                cleaned_line = stripped_line[1:]
                # Preserve the original indentation
                cleaned_line = line[:len(line) - len(stripped_line)] + cleaned_line
            else:
                cleaned_line = line
            
            cleaned_lines.append(cleaned_line)
        return cleaned_lines

    def clean_yaml(self, yaml_string: str) -> YAMLResult:
        """Clean and format YAML string, handling common errors."""
        try:
            # Check if the input is a simple list
            lines = yaml_string.strip().split('\n')
            if all(line.strip().startswith('-') for line in lines):
                # It's a simple list, preserve its structure
                data = [line.strip()[1:].strip() for line in lines]
                formatted_yaml = '\n'.join(f'- {item}' for item in data)
                return YAMLResult(data, formatted_yaml, None, YAML_TYPE_LIST)

            # If it's not a simple list, proceed with the normal cleaning process
            lines = self._remove_leading_characters(lines)
            lines = self._add_missing_colons(lines)
            fixed_lines = self._fix_indentation(lines)
            
            simplified_yaml = '\n'.join(fixed_lines)
            
            # Parse the fixed YAML
            input_stream = StringIO(simplified_yaml)
            data = self.yaml.load(input_stream)
            
            # Determine YAML type
            yaml_type = self._determine_yaml_type(data)
            
            # Format the YAML properly
            output_stream = StringIO()
            self.yaml.dump(data, output_stream)
            formatted_yaml = output_stream.getvalue()
            
            return YAMLResult(data, formatted_yaml, None, yaml_type)
                
        except Exception as e:
            return YAMLResult(None, None, f"Unable to fix YAML: {str(e)}", 0)

    def _determine_yaml_type(self, data: Any) -> int:
        if isinstance(data, (str, int, float, bool)) or data is None:
            return YAML_TYPE_SCALAR
        elif isinstance(data, list):
            return YAML_TYPE_LIST
        elif isinstance(data, dict):
            return YAML_TYPE_DICT
        else:
            return 0  # Unknown type

def main():
    """Main function for testing YAML cleaning functionality."""
    cleaner = YAMLCleaner()
    test_cases = get_test_cases()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i} - {test_case['name']}:")
        print("=" * 50)
        print("Original YAML:")
        print(test_case['yaml'])
        
        result = cleaner.clean_yaml(test_case['yaml'])
        
        if result.is_valid():
            print("\nCleaned YAML:")
            print(result.cleaned_yaml)
            print("\nParsed data:")
            print(result.data)
            print(f"\nYAML Type: {result.get_type_name()} (Type {result.yaml_type})")
            if result.error_message:
                print("\nNote:", result.error_message)
        else:
            print("\nError:", result.error_message)
            print("Expected success:", test_case['expected_success'])
            print("Note:", test_case['note'])

    # Additional examples to demonstrate YAML types
    print("\nAdditional YAML Type Examples:")
    print("=" * 50)
    
    scalar_yaml = "42"
    list_yaml = "- item1\n- item2\n- item3"
    dict_yaml = "key1: value1\nkey2: value2"
    
    for yaml_str in [scalar_yaml, list_yaml, dict_yaml]:
        result = cleaner.clean_yaml(yaml_str)
        print(f"\nOriginal YAML:\n{yaml_str}")
        print(f"YAML Type: {result.get_type_name()} (Type {result.yaml_type})")
        print(f"Cleaned YAML:\n{result.cleaned_yaml}")

if __name__ == "__main__":
    main()
