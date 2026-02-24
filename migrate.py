#!/usr/bin/env python3
""""
This needs to produce:
a) An HCL fragment defining the config, i.e. a module block with arguments
   which are valid module input variables - this is a nested HCL datastructure
b) A series of import blocks

For a), the way this works is to actually produce a *python* (nested) datastructure
first, then convert that to HCL. Noting that the module input variables are actually
*containers*, e.g. a map of projects etc:
- There is a dataclass representing each entry in an input variable (e.g. a project, a user etc)
- There is a load_ function which constructs that dataclass
The load_ function simply:
- Uses a helper function to make an openstack CLI call [1] and return a python
  data structure.
- Uses the returne data to create the dataclass

The dataclass:
- Has an attribute for each attribute on the HCL container
- Has methods:
    to_data(): Return a python datastructure
    to_import(): Return a list of import blocks

Then at the "top-level" in the code we construct a python datastructure
which represents the HCL, then convert it.

[1]: These are more regularly structured than using the sdk functions!

"""


import subprocess, json, pprint, argparse, os, itertools
from pathlib import Path
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
        print('DEBUG os_cmd:', os_cmd)
        print('DEBUG stderr', p.stderr)
        exit(1)
    values = json.loads(p.stdout) if as_json else p.stdout
    if DEBUG: print('DEBUG values:', values)
    return values

def fmt_import(address, tofu_id):
    return IMPORT_TEMPLATE.format(address=address, tofu_id=tofu_id).strip()

def os_resource_list(resource_type, extra_os_args=None):
    """ Return a list of OpenStack resource names for the given resource type """
    cmd = f'openstack {resource_type} list --format json'.split() + (extra_os_args or [])
    p = subprocess.run(cmd, text=True, capture_output=True)
    try:
        names = [p['Name'] for p in json.loads(p.stdout)]
    except Exception:
        print('DEBUG:', p.stdout)
        raise
    return names

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
    groups: list[str]
    config_keys = ['description', 'email', 'groups']

    def to_data(self):
        # should return a python datastructure
        return {k: getattr(self, k) for k in self.config_keys}

    def to_import(self):
        blocks = [
            fmt_import(f'module.openstack.openstack_identity_user_v3.user["{self.name}"]', self.id)
        ]
        return blocks
    
def load_user(name):
    user = run_os_cmd(f"openstack user show --format json {name}")
    groups = run_os_cmd(f"openstack group list --format json --user {user['id']}")
    return User(name=name,
                description=user['description'],
                id=user['id'],
                email=user['email'],
                groups=[g['Name'] for g in groups]
                )        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='main.tf', help="name for created file containing OpenTofu configuration (default: main.tf)")
    parser.add_argument('--imports', default='imports.tf', help="name for created file containing import blocks (default: imports.tf)")
    parser.add_argument('--output', default='.', help="path to directory containing created files (default: cwd)")
    parser.add_argument('--projects', default=None, help="comma-separated list of projects to import (default: all)")
    parser.add_argument('--groups', default=None, help="comma-separated list of groups to import (default: all)")
    parser.add_argument('--users', default=None, help="comma-separated list of users to import (default: all in 'default' domain)")
    parser.add_argument('--flavors', default=None, help="comma-separated list of flavors to import (default: all)")
    args = parser.parse_args()

    # load resource names to import:
    project_names = args.projects.split(',') if args.projects else os_resource_list("project")
    group_names = args.groups.split(',') if args.groups else os_resource_list("group")
    user_names = args.users.split(',') if args.users else os_resource_list("user", ["--domain", "default"])
    
    # run API queries:
    project_objs = {p: load_project(p) for p in sorted(project_names)}
    group_objs = {g: load_group(g) for g in sorted(group_names)}
    user_objs = {u: load_user(u) for u in sorted(user_names)}

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
    config_path = Path(args.output).joinpath(args.config)
    with open(config_path, 'w') as config_file:
        config_file.write(config_hcl)
    print(f'written {config_path}')

    # convert to hcl import blocks:
    objs = flatten((project_objs.values(), group_objs.values(), user_objs.values()))
    import_path = Path(args.output).joinpath(args.imports)
    with open(import_path, 'w') as imports_file:
        for o in objs:
            imports_file.write('\n'.join(o.to_import()) + '\n')
    print(f'written {import_path}')
