#!/usr/bin/env python3


INDENT_STEP = 2

def to_tf(obj):
    queue = [obj]
    head = ['']
    tail = []
    indent = 0
    while queue:
        current = queue.pop(0)
        print('DEBUG:', current)
        if isinstance(current, dict):
            head[-1] += '{'
            indent += INDENT_STEP
            tail.append(f"{' ' * (indent - INDENT_STEP)}}}")
            for k, v in current.items():
                if isinstance(v, dict):
                    head.append(f"{' ' * indent}{k} = ")
                    queue.append(v)
                elif isinstance(v, str):
                    head.append(' ' * indent + f'{k} = "{v}"')
                elif isinstance(v, int):
                    head.append(' ' * indent + f'{k} = {v}')
                elif isinstance(v, list):
                    queue.append(v)
                elif v is None:
                    head.append(' ' * indent + f'{k} = null')
                else:
                    raise NotImplementedError(v)
        elif isinstance(current, list):
            head.append(f"{' ' * indent}[")
            indent += INDENT_STEP
            tail.append(f"{' ' * (indent - INDENT_STEP)}]")
            for e in current:
                queue.append(e)
    return '\n'.join(head + list(reversed(tail)))



if __name__ == '__main__':

    TEST1 = {
        "sb-test-1": {
            "description":"Project One",
            "quotas": {
                "instances": 20,
                "cores": 200,
                "ram": 512000,
                "floating_ips": 3,
                "routers": 3,
                "ports": 500,
            }
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
    print(to_tf(TEST1))

