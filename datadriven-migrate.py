#!/usr/bin/env python3

import sys, subprocess, json, pprint

import to_tf

class OSCmd:
    def __init__(self, cmdstr, as_json=True, transform=None):
        self.cmdstr = cmdstr
        self.as_json = as_json
        self.transform = transform
    def __call__(self, **args):
        expanded_cmd = self.cmdstr.format(**args)
        cmd_list = ["openstack"] + expanded_cmd.split()
        cmd_list += ["-f", "json"] if self.as_json else ["-f", "value"]
        print('calling', cmd_list)
        p = subprocess.run(cmd_list, text=True, capture_output=True)
        # todo: error handling!
        value = json.loads(p.stdout) if self.as_json else p.stdout.strip()
        if self.transform:
            value = self.transform(value)
        return value
    
    # def __repr__(self):
    #     #return pprint.pformat(self.value)
    #     return pprint.pformat(self.to_tf)

def items_to_dict(lst, key='Resource', value='Limit'):
    d = {}
    for o in lst:
        d[o[key]] = o[value]
    return d

project = {
    "{project_name}": {
        "description": OSCmd("project show {project_name} -c description", as_json=False),
        "compute_quotas": OSCmd("quota show --compute {project_name}", transform=items_to_dict)
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
                    current[fmt_key] = value
                    del current[key]
                    key = fmt_key
                if isinstance(value, OSCmd):
                    current[key] = getattr(value, method)(**args)
                elif isinstance(value, (dict, list)):
                    queue.append(value)

        elif isinstance(current, list):
            print('processing list')
            for i, value in enumerate(current):
                if isinstance(value, OSCmd):
                    current[i] = getattr(value, method)(**args)
                elif isinstance(value, (dict, list)):
                    queue.append(value)
        else:
            print('should be an error?')
    return obj


if __name__ == "__main__":
    project_name = sys.argv[1]

    walk(project, {'project_name': project_name})
    #walk(project, {'project_name': project_name}, method='to_tf')
    pprint.pprint(project)

    print('--')
    tf = to_tf.to_tf(project)
    print(tf)
