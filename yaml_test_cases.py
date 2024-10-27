"""Test cases for YAML cleaning functionality"""

TEST_CASES = [
        # Test Case 0 - Nested structure with mixed issues and - and * at the beginning of lists
    {
        "name": "Nested Structure with Mixed Issues and * and - on lists",
        "yaml": """
top1:
    - linesandstart: value1  # dash
    -  extra_nestedandline: value2  # Wrong indent and -
top2:
  *  nested2star value3  # Missing colon and *
  wrong_indent: value4  # Wrong indent
        """,
        "expected_success": True,
        "note": ""
    },

    # Test Case 1 - Server configuration with indentation errors
    {
        "name": "Server Config with Indentation Error",
        "yaml": """
server:
  host: localhost
    port: 8181  # Indentation error
database:
  url: www.myurl.com
        """,
        "expected_success": False,
        "note": ""
    },
    
    # Test Case 2 - Missing colons and wrong indentation
    {
        "name": "Missing Colons and Wrong Indentation",
        "yaml": """
server:
  host: localhost
    port: 8080
database:
  url postgresql://localhost:5432/mydb  # Missing colon
logging:
  level debug  # Missing colon
    handlers:  # Wrong indent
      file: /var/log/app.log
        """,
        "expected_success": False,
        "note": ""
    },
    
    # Test Case 3 - Nested structure with mixed issues
    {
        "name": "Nested Structure with Mixed Issues",
        "yaml": """
top1:
    nested1: value1
      extra_nested: value2  # Wrong indent
top2:
    nested2 value3  # Missing colon
  wrong_indent: value4  # Wrong indent
        """,
        "expected_success": True,
        "note": ""
    }
    
]

def get_test_cases():
    """Return the test cases for YAML cleaning tests."""
    return TEST_CASES