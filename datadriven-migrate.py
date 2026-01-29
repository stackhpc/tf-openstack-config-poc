#!/usr/bin/env python3

import sys, subprocess, json, pprint
import to_tf

IMPORT_TEMPLATE="""
import {{
    to = {address}
    id = {tofu_id}
}}
"""

def items_to_dict(lst, key='Resource', value='Limit'):
    d = {}
    for o in lst:
        d[o[key]] = o[value]
    return d

class OSResource:

    transform = None

    def eval(self, as_json=True, transform=None):
        p = subprocess.run(self.os_cmd.split(), text=True, capture_output=True)
        values = json.loads(p.stdout) if as_json else p.stdout.strip()
        if transform:
            values = transform(values)
        self.values = values

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

    config_values = ['description']

    def __init__(self, name):
        self.name = name
        self.os_cmd = f"openstack project show {self.name} --format json"
        self.eval()
        self.children = {
            "compute_quota": ComputeQuota(self.name, self.values['id'])
        }
        self.address = f'module.openstack.openstack_identity_project_v3.project["{self.name}"]'
        self.tofu_id = self.values['id']
    
class ComputeQuota(OSResource):

    children = {}
    
    def __init__(self, project_name, project_id):
        self.project_name = project_name
        self.project_id = project_id
        self.os_cmd = f"openstack quota show --compute -f json {self.project_id}"    
        self.eval(transform=items_to_dict)
        self.config_values = self.values.keys()
        self.address = f'module.openstack.openstack_compute_quotaset_v2.project["{self.project_name}"]'
        self.tofu_id = f"{self.project_id}/RegionOne"

if __name__ == "__main__":
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
