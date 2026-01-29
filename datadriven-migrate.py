#!/usr/bin/env python3

import sys, subprocess, json, pprint

class OSCmd:
    def __init__(self, cmdstr, as_json=True):
        self.cmdstr = cmdstr
        self.as_json = as_json
        self.value = None
    def __call__(self, **args):
        expanded_cmd = self.cmdstr.format(**args)
        cmd_list = ["openstack"] + expanded_cmd.split()
        cmd_list += ["-f", "json"] if self.as_json else ["-f", "value"]
        print('calling', cmd_list)
        p = subprocess.run(cmd_list, text=True, capture_output=True)
        # todo: error handling!
        self.value = json.loads(p.stdout) if self.as_json else p.stdout.strip()

    def __repr__(self):
        return pprint.pformat(self.value)

project = {
    "{project_name}": {
        "description": OSCmd("project show {project_name} -c description", as_json=False),
        "compute_quotas": OSCmd("quota show --compute {project_name}")
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
        #print('current', current)

        if id(current) in visited:
            continue
        visited.add(id(current))

        if isinstance(current, dict):
            for key, value in list(current.items()):
                fmt_key = key.format(**args)
                if fmt_key != key:
                    del current[key]
                    current[fmt_key] = value
                if isinstance(value, OSCmd):
                    getattr(value, method)(**args)
                elif isinstance(value, (dict, list)):
                    queue.append(value)

        elif isinstance(current, list):
            print('processing list')
            for i, value in enumerate(current):
                if isinstance(value, OSCmd):
                    getattr(value, method)(**args)
                elif isinstance(value, (dict, list)):
                    queue.append(value)
        else:
            print('should be an error?')
    return obj


if __name__ == "__main__":
    project_name = sys.argv[1]

    walk(project, {'project_name': project_name})
    pprint.pprint(project)
