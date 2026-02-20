#!/usr/bin/env python3

import subprocess, json, pprint, argparse, os, itertools
from dataclasses import dataclass
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

def run_os_cmd(os_cmd, as_json=True):
    """" Returns a dict of key/values from command stdout """
    if DEBUG: print('DEBUG os_cmd:', os_cmd)
    p = subprocess.run(os_cmd.split(), text=True, capture_output=True)
    if p.returncode > 0:
        raise ValueError(p.stderr)
    values = json.loads(p.stdout) if as_json else p.stdout
    if DEBUG: print('DEBUG values:', values)
    return values

def fmt_import(address, tofu_id):
    return IMPORT_TEMPLATE.format(address=address, tofu_id=tofu_id).strip()

@dataclass
class Project:
    name: str
    description: str
    id: str
    compute_quota: dict
    network_quota: dict
    blockstorage_quota: dict
    config_keys = ['description', 'compute_quota', 'network_quota', 'blockstorage_quota']
    
    def to_data(self):
        # should return a python datastructure
        return {k: getattr(self, k) for k in self.config_keys}
    
    def to_import(self):
        
        blocks = [
            fmt_import(f'module.openstack.openstack_identity_project_v3.project["{self.name}"]', self.id),
            fmt_import(f'module.openstack.openstack_compute_quotaset_v2.project["{self.name}"]', f"{self.id}/RegionOne"), # TODO: FIX REGION?
            fmt_import(f'module.openstack.openstack_networking_quota_v2.project["{self.name}"]', f"{self.id}/RegionOne"), # TODO: FIX REGION?
            fmt_import(f'module.openstack.openstack_blockstorage_quotaset_v3.project["{self.name}"]', f"{self.id}/RegionOne"), # TODO: FIX REGION?
        ]
        return blocks
    
def load_project(name) -> Project:
    proj = run_os_cmd(f"openstack project show {name} --format json")
    compute_quota = run_os_cmd(f"openstack quota show --compute --format json {proj['id']}")
    network_quota = run_os_cmd(f"openstack quota show --network --format json {proj['id']}")
    blockstorage_quota = run_os_cmd(f"openstack quota show --volume --format json {proj['id']}")
    return Project(
        name=proj['name'],
        description=proj['description'],
        id=proj['id'],
        compute_quota=items_to_dict(compute_quota),
        network_quota=items_to_dict(network_quota),
        blockstorage_quota=items_to_dict(blockstorage_quota),
    )


@dataclass
class Group:
    name: str
    description: str
    id: str
        
    def to_import(self):
        blocks = [
            fmt_import(f'module.openstack.openstack_identity_group_v3.group["{self.name}"]', self.id)
        ]
        return blocks
    
def load_group(name) -> Group:
    group = run_os_cmd(f'openstack group show --format json  {name}')
    return Group(
        name=name,
        description=group['description'],
        id=group['id']
    )

@dataclass
class User:
    name: str
    description: str
    id: str
    email: str
    config_keys = ['description', 'email'] # TODO: groups

    def to_data(self):
        # should return a python datastructure
        return {k: getattr(self, k) for k in self.config_keys}
    
def load_user(name):
    user = run_os_cmd(f"openstack user show --format json {name}")
    return User(name=name,
                description=user['description'],
                id=user['id'],
                email=user['email'],
                )
    
        

if __name__ == "__main__":

    # TODO: really need to handle domain to add users!

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='main.tf', help="path for created file containing OpenTofu configuration (default: main.tf)")
    parser.add_argument('--imports', default='imports.tf', help="path for created file containing import blocks (default: imports.tf)")
    parser.add_argument('--projects', default=None, help="comma-separated list of projects to import (default: all)")
    parser.add_argument('--groups', default=None, help="comma-separated list of groups to import (default: all)")
    parser.add_argument('--users', default=None, help="comma-separated list of users to import (default: all in 'default' domain)")
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
    if args.users is None: # TODO: handle non-default domain!
        u = subprocess.run('openstack user list --domain default --format json'.split(), text=True, capture_output=True)
        user_names = [u['Name'] for u in json.loads(u.stdout)]
    else:
        user_names = args.users.split(',')
    
    # run API queries:
    project_objs = {p: load_project(p) for p in sorted(project_names)}
    group_objs = {g: load_group(g) for g in sorted(group_names)}
    user_objs = {u: load_user(u) for u in sorted(user_names)}

    # for k, v in project_objs.items():
    #     print(k)
    #     print(type(v))
    
    # create a datastructure with the config in Python form:
    config_py = {
        ("module", "openstack"):{
            "source":f"{MODULE_SOURCE}",
            "projects":dict((n, p.to_data()) for n, p in project_objs.items()),
            "groups":{g.name: g.description for g in group_objs.values()},
            "users":{n: u.to_data() for n, u in user_objs.items()},
        }
    }

    # convert to hcl config:
    config_hcl=hcl.to_hcl(config_py)
    with open(args.config, 'w') as config_file:
        config_file.write(config_hcl)
    print(f'written {args.config}')

    # # convert to hcl import blocks:
    # #objs = flatten((project_objs.values(), group_objs.values(), user_objs.values()))
    objs = flatten((project_objs.values(), group_objs.values()))
    with open(args.imports, 'w') as imports_file:
        for o in objs:
            imports_file.write('\n'.join(o.to_import()) + '\n')
    print(f'written {args.imports}')
