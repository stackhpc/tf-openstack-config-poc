#!/usr/bin/env python3


INDENT_STEP = 2

def to_tf(obj, indent=0):
    indent_start=indent
    queue = [(obj, indent_start, None)]  # (object, indent_level, key_name)
    lines = []
    
    while queue:
        current, indent, key = queue.pop(0)
        prefix = ' ' * indent
        
        if isinstance(current, dict):
            if key is not None:
                lines.append(f"{prefix}{key} = {{")
            # else:
            #     lines.append(f"{prefix}{{")
        
            # Add dict items to queue in reverse order so they process in correct order
            items = list(current.items())
            for k, v in reversed(items):
                queue.insert(0, (v, indent + INDENT_STEP, k))
            
            # Add closing brace (will be added after all nested items are processed)
            if key is not None:
                queue.insert(len(items), ('}', indent, None))
        
        elif isinstance(current, list):
            if key is not None:
                lines.append(f"{prefix}{key} = [")
            # else:
            #     lines.append(f"{prefix}[")
            
            # Add list items to queue in reverse order
            for item in reversed(current):
                queue.insert(0, (item, indent + INDENT_STEP, None))
            
            # Add closing bracket
            if key is not None:
                queue.insert(len(current), (']', indent, None))
        
        elif isinstance(current, str):
            if current in ['}', ']']:
                lines.append(f"{prefix}{current}")
            else:
                lines.append(f'{prefix}{key} = "{current}"')
        
        elif isinstance(current, int):
            lines.append(f'{prefix}{key} = {current}')
        
        elif current is None:
            lines.append(f'{prefix}{key} = null')
        
        else:
            raise NotImplementedError(f"Type {type(current)} not supported")
    
    return '\n'.join(lines)



if __name__ == '__main__':

    TEST1 = {
        "sb-test-1": {
            "description":"Project One",
            "quotas": [
                {'Limit': 20, 'Resource':"instances"},
                {'Limit': 200, 'Resource':"cores"},
            ]
        }
    }

    #print(to_tf(TEST1))
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
    print(to_tf(TEST2))

