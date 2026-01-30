#!/usr/bin/env python3


INDENT_STEP = 2

class Newline:
    pass
NEWLINE = Newline()

def to_hcl(obj):
    queue = [(obj, 0, None)]  # (current object, indent, key)
    # key is either:
    # - a string (dict value)
    # - None (everything else: top-level, list items, and structural markers)
    lines = []
    is_top = True
    
    while queue:
        current, indent, key = queue.pop(0)
        prefix = ' ' * indent
        
        if isinstance(current, dict):
            if key is not None:
                if isinstance(key, tuple): # block
                    block_type = key[0]
                    block_labels = [f'"{k}"' for k in key[1:]]
                    lines.append(f"{prefix}{block_type} {' '.join(block_labels)} {{")
                else:
                    lines.append(f"{prefix}{key} = {{")
            elif not is_top:
                lines.append(f"{prefix}{{")

            # Add dict items to queue in reverse order so they process in correct order
            items = list(current.items())
            for k, v in reversed(items):
                queue.insert(0, (v, indent + INDENT_STEP if not is_top else indent, k))
            
            # Add closing brace (will be added after all nested items are processed)
            if not is_top:
                if key is None: # # Add comma if this dict is a list item
                    closing = ['},'] #queue.insert(len(items), ('},', indent, None))
                elif isinstance(key, tuple) and indent == 0: # Add newline between top-level blocks
                    closing = ['}', NEWLINE]
                    #queue.insert(len(items) + 1, (NEWLINE, indent, None))    
                else:
                    closing = ['}']
                for idx, c in enumerate(closing):
                    queue.insert(len(items) + idx, (c, indent, None))
                    
        elif isinstance(current, list):
            if key is not None:
                lines.append(f"{prefix}{key} = [")
            elif not is_top:
               lines.append(f"{prefix}[")
            
            # Add list items to queue in reverse order
            for item in reversed(current):
                queue.insert(0, (item, indent + INDENT_STEP if not is_top else indent, None))
            
            # Add closing bracket
            if not is_top:
                closing = '],' if key is None else ']'  # Add comma if this list is a list item
                queue.insert(len(current), (closing, indent, None))
        
        elif isinstance(current, str):
            if current in ['}', '],', '},', ']']:
                lines.append(f"{prefix}{current}")
            elif key is None:  # List item
                lines.append(f'{prefix}"{current}",')
            else:  # Dict value
                lines.append(f'{prefix}{key} = "{current}"')
        
        elif isinstance(current, int):
            if key is None:  # List item
                lines.append(f'{prefix}{current},')
            else:  # Dict value
                lines.append(f'{prefix}{key} = {current}')
        
        # TODO: maybe get rid of this so we don't define null values for brevity?
        elif current is None:
            if key is None:  # List item
                lines.append(f'{prefix}null,')
            else:  # Dict value
                lines.append(f'{prefix}{key} = null')
        
        elif current == NEWLINE:
            lines.append('')
        
        else:
            raise NotImplementedError(f"Type {type(current)} not supported")

        is_top = False  # After first iteration, we're never at top level again
    
    return '\n'.join(lines)



if __name__ == '__main__':

    import sys
    TEST1 = {
        "sb-test-1": {
            "description":"Project One",
            "quotas": [
                {'Limit': 20, 'Resource':"instances"},
                {'Limit': 200, 'Resource':"cores"},
            ]
        }
    }

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

    TEST3 = [
        "a", "b","c"
    ]
    TEST4 = {
        "foo": ["a", "b", "c"]
    }

    TEST5 = {
        ("resource", "aws_instance", "foo"):{
            "ami": "abc123",
            ("network_interface",): {
                "id":"uuid_1"
            }
        },
        ("resource", "aws_instance", "bar"):{
            "ami": "abc123",
            ("network_interface",): {
                "id":"uuid_2"
            }
        }
    }

    TEST6 = {
        "x":[
            {"foo":"0"},
            {"bar":"1"},
        ]
    }

    TEST7 = {
        "foo": [
            "a",
            [0, 1, 2], 
            "b",
            "c"
        ]
    }

    test = sys.argv[1]
    print(to_tf(locals()[test]))

