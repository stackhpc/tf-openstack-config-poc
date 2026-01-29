#!/usr/bin/env python3

import sys, subprocess, json, pprint, argparse
import to_tf

IMPORT_TEMPLATE="""
import {{
    to = {address}
    id = "{tofu_id}"
}}
"""
CONFIG_TEMPLATE="""
module "openstack" {{
  source = "TODO"

  projects = {{
  {project_tf}
  }}
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
            "compute_quotas": ComputeQuota(self.name, self.values['id'])
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

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.tf') # TODO: change to main.tf
    parser.add_argument('--imports', default='imports.tf')
    parser.add_argument('--projects', default=None)
    args = parser.parse_args()

    if args.projects is None:
        p = subprocess.run('openstack project list --format json'.split(), text=True, capture_output=True)
        project_names = [p['Name'] for p in json.loads(p.stdout)]
    else:
        project_names = args.projects.split(',')
    print('Importing projects:', project_names)

    # generate python datastructure with classes:
    projects = dict((project_name , Project(project_name)) for project_name in project_names)

    # TODO: not sure of best way to handle the fact the entire file isn't
    # maybe should let tofu fmt handle indentation??

    # convert that to literals only:
    project_config = dict((n, p.config()) for n, p in projects.items())

    # TODO: we could probably generate a single config object and then walk it?
    project_tf=to_tf.to_tf(project_config, indent=0) # indent depends on template :-(

    with open(args.config, 'w') as config_file:
        config_txt = CONFIG_TEMPLATE.format(project_tf=project_tf)
        #config_txt = to_tf.to_tf(config)
        config_file.write(config_txt)
    print(f'written {args.config}')

    with open(args.imports, 'w') as imports_file:
        for p in projects.values():
            imports_file.write('\n'.join(p.import_block()) + '\n')
    print(f'written {args.imports}')
