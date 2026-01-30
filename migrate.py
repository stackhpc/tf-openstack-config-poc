#!/usr/bin/env python3

import subprocess, json, pprint, argparse, os, itertools
import hcl

IMPORT_TEMPLATE="""
import {{
    to = {address}
    id = "{tofu_id}"
}}
"""
MODULE_SOURCE="../../modules/openstack_config"
DEBUG=os.getenv('DEBUG', default=False)

def flatten(lst):
    return list(itertools.chain.from_iterable(lst))

def items_to_dict(lst, key='Resource', value='Limit'):
    if not isinstance(lst, list):
        raise TypeError(f'not a list: {lst}')
    d = {}
    for o in lst:
        if not isinstance(o, dict):
            raise TypeError(f'List item is not a dict: {o}')
        if key not in o:
            raise ValueError(f'Key {key} not found in dict: {o}')
        if value not in o:
            raise ValueError(f'Key {value} not found in dict: {o}')
        d[o[key]] = o[value]
    return d

class OSResource:

    children = {}
    config_values = {} # TODO: change to config_keys
    address = None
    tofu_id = None

    def eval(self, as_json=True, transform=None):
        if DEBUG: print('DEBUG os_cmd:', self.os_cmd)
        p = subprocess.run(self.os_cmd.split(), text=True, capture_output=True)
        if p.returncode > 0:
            raise ValueError(p.stderr)
        values = json.loads(p.stdout) if as_json else p.stdout.strip()
        if DEBUG: print('DEBUG values:', self)
        print(values)
        if transform:
            values = transform(values)
        self.values = values

    def config(self):
        # TODO: explaijn this is the common case where
        # each object returns a dict, with keys from self.config_values
        # and values from returned values, descending into child items
        d = dict((k, self.values[k]) for k in self.config_values)
        for k, v in self.children.items():
            d[k] = v.config()
        return d
    
    def import_block(self):
        if self.address is None:
            raise ValueError(f'address property not set on {self}')
        if self.tofu_id is None:
            raise ValueError(f'tofu_id property not set on {self}')
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
            "compute_quota": ComputeQuota(self.name, self.values['id']),
            "blockstorage_quota": BlockStorageQuota(self.name, self.values['id']),
            "network_quota": NetworkQuota(self.name, self.values['id']),
        }
        self.address = f'module.openstack.openstack_identity_project_v3.project["{self.name}"]'
        self.tofu_id = self.values['id']
    
class ComputeQuota(OSResource):
    
    def __init__(self, project_name, project_id):
        self.project_name = project_name
        self.project_id = project_id
        self.os_cmd = f"openstack quota show --compute -f json {self.project_id}"    
        self.eval(transform=items_to_dict)
        self.config_values = self.values.keys()
        self.address = f'module.openstack.openstack_compute_quotaset_v2.project["{self.project_name}"]'
        self.tofu_id = f"{self.project_id}/RegionOne" # TODO: FIX REGION?

class BlockStorageQuota(OSResource):
    
    def __init__(self, project_name, project_id):
        self.project_name = project_name
        self.project_id = project_id
        self.os_cmd = f"openstack quota show --volume -f json {self.project_id}"    
        self.eval(transform=items_to_dict)
        self.config_values = self.values.keys()
        self.address = f'module.openstack.openstack_blockstorage_quotaset_v3.project["{self.project_name}"]'
        self.tofu_id = f"{self.project_id}/RegionOne"  # TODO: FIX REGION?

class NetworkQuota(OSResource):
    
    def __init__(self, project_name, project_id):
        self.project_name = project_name
        self.project_id = project_id
        self.os_cmd = f"openstack quota show --network -f json {self.project_id}"    
        self.eval(transform=items_to_dict)
        self.config_values = self.values.keys()
        self.address = f'module.openstack.openstack_networking_quota_v2.project["{self.project_name}"]'
        self.tofu_id = f"{self.project_id}/RegionOne"  # TODO: FIX REGION?

class Group(OSResource):
    def __init__(self, group_name):
        self.group_name = group_name
        self.os_cmd = f"openstack group show -f json {self.group_name}"
        self.eval()
        self.address = f'module.openstack.openstack_identity_group_v3.group["{self.group_name}"]'
        self.tofu_id = self.values['id']

    def config(self):
        return self.values['description']

class User(OSResource):
    def __init__(self, user_name):
        self.user_name = user_name
        self.os_cmd = f"openstack user show -f json {self.user_name}"
        self.eval()
        self.config_values = ['description', 'email'] # TODO: groups
        self.address = f'module.openstack.openstack_identity_user_v3.user["{self.user_name}"]'
        self.tofu_id = self.values['id']
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='main.tf', help="path for created file containing OpenTofu configuration (default: main.tf)")
    parser.add_argument('--imports', default='imports.tf', help="path for created file containing import blocks (default: imports.tf)")
    parser.add_argument('--projects', default=None, help="comma-separated list of projects to import (default: all)")
    parser.add_argument('--groups', default=None, help="comma-separated list of groups to import (default: all)")
    parser.add_argument('--users', default=None, help="comma-separated list of users to import (default: all)")
    args = parser.parse_args()

    # TODO: could tidy this up!
    if args.projects is None:
        p = subprocess.run('openstack project list --format json'.split(), text=True, capture_output=True)
        project_names = [p['Name'] for p in json.loads(p.stdout)]
    else:
        project_names = args.projects.split(',')
    
    if args.groups is None:
        g = subprocess.run('openstack group list --format json'.split(), text=True, capture_output=True)
        group_names = [g['Name'] for g in json.loads(g.stdout)]
    else:
        group_names = args.groups.split(',')

    if args.users is None:
        u = subprocess.run('openstack user list --format json'.split(), text=True, capture_output=True)
        user_names = [u['Name'] for u in json.loads(u.stdout)]
    else:
        user_names = args.users.split(',')
    
    # run API queries:
    project_objs = dict((project_name , Project(project_name)) for project_name in project_names)
    group_objs = dict((group_name, Group(group_name)) for group_name in group_names)
    user_objs = dict((user_name, User(user_name)) for user_name in user_names)
    
    # create a datastructure with the config in Python form:
    config_py = {
        ("module", "openstack"):{
            "source":f"{MODULE_SOURCE}",
            # TODO: could tidy this into a function?
            "projects":dict((n, p.config()) for n, p in project_objs.items()),
            "groups":dict((n, g.config()) for n, g in group_objs.items()),
            "users":dict((n, u.config()) for n, u in user_objs.items()),
        }
    }

    # convert to hcl config:
    config_hcl=hcl.to_hcl(config_py)
    with open(args.config, 'w') as config_file:
        config_file.write(config_hcl)
    print(f'written {args.config}')

    # convert to hcl import blocks:
    objs = flatten((project_objs.values(), group_objs.values(), user_objs.values()))
    with open(args.imports, 'w') as imports_file:
        for o in objs:
            imports_file.write('\n'.join(o.import_block()) + '\n')
    print(f'written {args.imports}')
