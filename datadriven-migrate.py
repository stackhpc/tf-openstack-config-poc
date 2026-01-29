#!/usr/bin/env python3

import sys, subprocess, json, pprint

class OSCmd:
    def __init__(self, cmdstr):
        self.cmdstr = cmdstr
    def __call__(self, **args):

        expanded_cmd = self.cmdstr.format(**args)
        cmd_list = ["openstack"] + expanded_cmd.split() + ["-f", "json"]
        print('calling', cmd_list)
        p = subprocess.run(cmd_list, text=True, capture_output=True)
        # todo: error handling!
        return json.loads(p.stdout)

project = {
    "description": OSCmd("project show {project_name} -c description"),
    "quotas": {
        "compute": OSCmd("quota show --compute {project_name}")
        }
}

def walk(obj, args=None, method='__call__'):
    """
    Walk obj (non-recursively, calling the specified method passing args on each OSCmd objects.
    Results replace OSCmd objects.

    Note: This modifies the original structure!

    Args:
        obj: The data structure to walk
        args: Dict of arguments to the method, splatted in
        method: name of OSCmd method to call.
    """
    queue = [obj]
    visited = set()
    args = {} if args is None else args
    
    while queue:
        current = queue.pop(0)

        if id(current) in visited:
            continue
        visited.add(id(current))

        if isinstance(current, dict):
            for key, value in list(current.items()):
                if isinstance(value, OSCmd):
                    current[key] = getattr(value, method)(**args)
                elif isinstance(value, (dict, list)):
                    queue.append(value)

        elif isinstance(current, list):
            for i, value in enumerate(current):
                if isinstance(value, OSCmd):
                    current[i] = getattr(value, method)(**args)
                elif isinstance(value, (dict, list)):
                    queue.append(value)
    
    return obj


if __name__ == "__main__":
    project_name = sys.argv[1]

    walk(project, {'project_name': project_name})
    pprint.pprint(project)
