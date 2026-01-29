#!/usr/bin/env python3

import sys, subprocess, json, pprint
import to_tf

IMPORT_TEMPLATE="""
import {{
    to = {address}
    id = {tofu_id}
}}
"""

class OSResource:

    def eval(self):
        p = subprocess.run(self.os_cmd.split(), text=True, capture_output=True)
        self.values = json.loads(p.stdout) if self.as_json else p.stdout.strip()
        if self.transform:
            self.values = self.transform(self.values)

    def config(self):
        d = dict((k, self.values[k]) for k in self.config_values)
        for k, v in self.children.items():
            d[k] = v.config()
        return d
    
    def import_block(self):
        blocks = [IMPORT_TEMPLATE.format(address=self.address, tofu_id=self.tofu_id).strip()]
        for v in self.children.values():
            blocks.extend(v.import_block())
        return blocks

class Project(OSResource):
    def __init__(self, name):
        self.name = name
        self.os_cmd = f"openstack project show {self.name} --format json"
        self.as_json = True
        
        self.transform = None
        self.eval()
        self.config_values = ['description']
        
        self.children = {
            "compute_quota": ComputeQuota(self.name, self.values['id'])
        }

        self.address = f'module.openstack.openstack_identity_project_v3.project["{self.name}"]'
        self.tofu_id = self.values['id']
    
class ComputeQuota(OSResource):
    def __init__(self, project_name, project_id):
        self.project_name = project_name
        self.project_id = project_id
        self.os_cmd = f"openstack quota show --compute -f json {self.project_id}"
        self.as_json = True
        
        self.transform = items_to_dict
        self.eval()
        self.children = {}
        
        self.config_values = self.values.keys()

        self.address = f'module.openstack.openstack_compute_quotaset_v2.project["{self.project_name}"]'
        self.tofu_id = f"{self.project_id}/RegionOne"
        

def items_to_dict(lst, key='Resource', value='Limit'):
    d = {}
    for o in lst:
        d[o[key]] = o[value]
    return d

projects = dict((project_name , Project(project_name)) for project_name in sys.argv[1:])
project_data = {
    "projects": dict((n, p.config()) for n, p in projects.items())
}
print('data:')
pprint.pprint(project_data)
print('---')
config = to_tf.to_tf(project_data)
print(config)
print('---')
print('imports:')
for p in projects.values():
    print('\n'.join(p.import_block()))

# TODO: this can't handle multiple projects ...
# project={
#     'projects': {
#         "{project_name}": {
#             "description": OSCmd("project show {project_name} -c description", as_json=False),
#             "compute_quotas": OSCmd("quota show --compute {project_name}", transform=items_to_dict),
#             "id": OSCmd("project show {project_name} -c ID", as_json=False)
#         }
#     }
# }

# def walk(obj, args=None, method='__call__'):
#     """
#     Walk obj (non-recursively, calling the specified method passing args on each OSCmd objects.
#     Results replace OSCmd objects.

#     Note: This modifies the original structure!

#     Args:
#         obj: The data structure to walk
#         args: Dict of arguments to the method, splatted in
#         method: name of OSCmd method to call.
#     """
#     queue = [obj]
#     visited = set()
#     args = {} if args is None else args
    
#     while queue:
#         current = queue.pop(0)
#         #print('current', current)

#         if id(current) in visited:
#             continue
#         visited.add(id(current))

#         if isinstance(current, dict):
#             for key, value in list(current.items()):
#                 fmt_key = key.format(**args)
#                 if fmt_key != key:
#                     current[fmt_key] = value
#                     del current[key]
#                     key = fmt_key
#                 if isinstance(value, OSCmd):
#                     current[key] = getattr(value, method)(**args)
#                 elif isinstance(value, (dict, list)):
#                     queue.append(value)

#         elif isinstance(current, list):
#             print('processing list')
#             for i, value in enumerate(current):
#                 if isinstance(value, OSCmd):
#                     current[i] = getattr(value, method)(**args)
#                 elif isinstance(value, (dict, list)):
#                     queue.append(value)
#         else:
#             print('should be an error?')
#     return obj


# if __name__ == "__main__":
#     project_name = sys.argv[1]

#     walk(project, {'project_name': project_name})
#     #walk(project, {'project_name': project_name}, method='to_tf')
#     print('data:')
#     pprint.pprint(project)
#     print('--')
#     print('config:')
#     tf = to_tf.to_tf(project)
#     print(tf)
#     print('---')
#     print('import blocks:')
#     print('TODO')