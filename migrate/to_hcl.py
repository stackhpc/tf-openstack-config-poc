"""
Module for converting Python data structures to HCL format suitable for tfvars files.
Supports int, str, dict, and list types without using recursion.
"""

def to_hcl(data, indent_size=2):
    """
    Convert a Python data structure to HCL format.
    
    Args:
        data: Python data structure (int, str, dict, list, bool, None)
        indent_size: Number of spaces per indentation level (default: 2)
    
    Returns:
        str: HCL formatted string
    """
    if not isinstance(data, dict):
        raise ValueError("Top-level data must be a dictionary")
    
    result = []
    # Stack contains tuples of (action, key, value, indent_level)
    # action can be 'open_dict', 'close_dict', 'open_list', 'close_list', 
    # 'dict_key', 'list_item', 'add_comma'
    stack = []
    
    # Build stack in reverse order so first items are processed first
    for key in reversed(list(data.keys())):
        stack.append(('dict_key', key, data[key], 0))
    
    while stack:
        action, key, value, indent_level = stack.pop()
        indent = ' ' * (indent_level * indent_size)
        
        if action == 'dict_key':
            # Handle a dictionary key-value pair
            if isinstance(value, dict):
                result.append(f'{indent}{key} = {{')
                stack.append(('close_dict', None, None, indent_level))
                # Add dict items in reverse order
                for k in reversed(list(value.keys())):
                    stack.append(('dict_key', k, value[k], indent_level + 1))
            elif isinstance(value, list):
                result.append(f'{indent}{key} = [')
                stack.append(('close_list', None, None, indent_level))
                # Add list items in reverse order
                for i in reversed(range(len(value))):
                    if i < len(value) - 1:
                        stack.append(('add_comma', None, None, indent_level + 1))
                    stack.append(('list_item', i, value[i], indent_level + 1))
            else:
                result.append(f'{indent}{key} = {_format_value(value)}')
        
        elif action == 'list_item':
            # Handle a list item
            if isinstance(value, dict):
                result.append(f'{indent}{{')
                stack.append(('close_dict', None, None, indent_level))
                # Add dict items in reverse order
                for k in reversed(list(value.keys())):
                    stack.append(('dict_key', k, value[k], indent_level + 1))
            elif isinstance(value, list):
                result.append(f'{indent}[')
                stack.append(('close_list', None, None, indent_level))
                # Add list items in reverse order
                for i in reversed(range(len(value))):
                    if i < len(value) - 1:
                        stack.append(('add_comma', None, None, indent_level + 1))
                    stack.append(('list_item', i, value[i], indent_level + 1))
            else:
                result.append(f'{indent}{_format_value(value)}')
        
        elif action == 'close_dict':
            result.append(f'{indent}}}')
        
        elif action == 'close_list':
            result.append(f'{indent}]')
        
        elif action == 'add_comma':
            # Add comma to the previous line
            if result:
                result[-1] = result[-1] + ','
    
    return '\n'.join(result)


def _format_value(value):
    """Format a primitive value for HCL."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, str):
        # Escape special characters
        escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{escaped}"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return 'null'
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")


# Example usage
if __name__ == "__main__":
    # Test case from user
    TEST2 = {
        "role_assignments": [
            {
                "role": "member",
                "group": "GroupA",
                "project": "sb-test-1",
            },
            {
                "role": "reader",
                "group": "GroupB",
                "project": "sb-test-2",
            }
        ]
    }
    
    print("TEST2 output:")
    print(to_hcl(TEST2))
    print("\n" + "="*50 + "\n")
    
    # More complex test
    test_data = {
        "environment": "production",
        "instance_count": 3,
        "enable_monitoring": True,
        "tags": {
            "Team": "DevOps",
            "Project": "Infrastructure"
        },
        "subnets": ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
        "instances": [
            {
                "name": "web-1",
                "type": "t3.medium",
                "ports": [80, 443]
            },
            {
                "name": "web-2",
                "type": "t3.large",
                "ports": [80, 443, 8080]
            }
        ],
        "price": 99.99,
        "description": None
    }
    
    print("Complex test output:")
    print(to_hcl(test_data))