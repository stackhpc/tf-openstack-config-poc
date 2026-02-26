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


import subprocess, json, pprint, argparse, os, itertools, functools
from pathlib import Path
from dataclasses import dataclass
from . import hcl, _version

IMPORT_TEMPLATE="""
import {{
    to = {address}
    id = "{tofu_id}"
}}
"""
MODULE_SOURCE = "github.com/stackhpc/tofu-openstack-config"
DEBUG = os.getenv('DEBUG', default=False)

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

@functools.cache
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

def as_dict(obj, keys=[]):
    return {k: getattr(obj, k) for k in keys}

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
        return as_dict(self, self.config_keys)
    
    def to_import(self):
        
        blocks = [
            fmt_import(f'module.openstack.openstack_identity_project_v3.project["{self.name}"]', self.id),
            fmt_import(f'module.openstack.openstack_compute_quotaset_v2.project["{self.name}"]', f"{self.id}/RegionOne"), # TODO: FIX REGION?
            fmt_import(f'module.openstack.openstack_networking_quota_v2.project["{self.name}"]', f"{self.id}/RegionOne"), # TODO: FIX REGION?
            fmt_import(f'module.openstack.openstack_blockstorage_quotaset_v3.project["{self.name}"]', f"{self.id}/RegionOne"), # TODO: FIX REGION?
        ]
        return blocks
    
def load_projects(names=None) -> dict[str, Project]:
    if names is None:
        names = [n['Name'] for n in run_os_cmd("openstack project list --format json")]
    projects = {}
    for name in sorted(names):
        proj = run_os_cmd(f"openstack project show {name} --format json")
        compute_quota = run_os_cmd(f"openstack quota show --compute --format json {proj['id']}")
        network_quota = run_os_cmd(f"openstack quota show --network --format json {proj['id']}")
        blockstorage_quota = run_os_cmd(f"openstack quota show --volume --format json {proj['id']}")
        projects[name] = Project(
            name=proj['name'],
            description=proj['description'],
            id=proj['id'],
            compute_quota=items_to_dict(compute_quota),
            network_quota=items_to_dict(network_quota),
            blockstorage_quota=items_to_dict(blockstorage_quota),
        )
    return projects

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
    
def load_groups(names=None) -> list[str, Group]:
    if names is None:
        names = [n["Name"] for n in run_os_cmd("openstack group list --format json")]
    groups = {}
    for name in sorted(names):
        group = run_os_cmd(f'openstack group show --format json  {name}')
        groups[name] = Group(
            name=name,
            description=group['description'],
            id=group['id']
        )
    return groups

@dataclass
class User:
    name: str
    description: str
    id: str
    email: str
    groups: list[str]

    def to_data(self):
        # should return a python datastructure
        data = as_dict(self, ["name", "description", "email"])
        data["groups"] = [g['Name'] for g in self.groups]
        return data

    def to_import(self):
        blocks = [
            fmt_import(f'module.openstack.openstack_identity_user_v3.user["{self.name}"]', self.id)
        ]
        for group in self.groups:
            group_name = group['Name']
            group_id = group['ID']
            address = f'module.openstack.openstack_identity_user_membership_v3.user_membership["{self.name}:{group_name}"]'
            tofu_id = f'{self.id}/{group_id}'
            blocks.append(fmt_import(address, tofu_id))
        return blocks
    
def load_users(names=None) -> list[User]:
    if names is None:
        names = [n["Name"] for n in run_os_cmd("openstack user list --format json --domain default")]
    users = {}
    for name in sorted(names):
        user = run_os_cmd(f"openstack user show --format json {name}")
        groups = run_os_cmd(f"openstack group list --format json --user {user['id']}")
        users[name] = User(name=name,
                        description=user['description'],
                        id=user['id'],
                        email=user['email'],
                        groups=groups,
                        )
    return users

@dataclass
class Flavor:
    name: str
    id: str
    ram: int
    vcpus: int
    disk: int
    ephemeral: int
    swap: int
    rx_tx_factor: float
    is_public: bool
    extra_specs: dict
    projects: list[dict]

    def to_data(self):
        data = as_dict(self, ['ram', 'vcpus', 'disk', 'ephemeral', 'swap', 'rx_tx_factor', 'is_public', 'extra_specs'])
        data["projects"] = [p["Name"] for p in self.projects]
        return data
    
    def to_import(self):
        blocks = [
            fmt_import(f'module.openstack.openstack_compute_flavor_v2.flavor["{self.name}"]', self.id)
        ]
        for project in self.projects:
            project_name = project["Name"]
            project_id = project["ID"]
            tofu_address = f'module.openstack.openstack_compute_flavor_access_v2.flavor_access["{self.name}:{project_name}"]'
            tofu_id = f'{self.id}/{project_id}'
            block = fmt_import(tofu_address, tofu_id)
            blocks.append(block)
        return blocks

def load_flavors(names=None) -> dict[str, Flavor]:
    if names is None:
        names = [n["Name"] for n in run_os_cmd("openstack flavor list --format json")]
    flavors = {}
    projects_by_id = {p["ID"]: p for p in run_os_cmd(f"openstack project list --format json")}
    for name in sorted(names):
        flavor = run_os_cmd(f"openstack flavor show --format json {name}")
        flavors[name] = Flavor(
            name = name,
            id = flavor['id'],
            ram = flavor['ram'],
            vcpus = flavor['vcpus'],
            disk = flavor['disk'],
            ephemeral = flavor.get('OS-FLV-EXT-DATA:ephemeral', 0),
            swap = flavor['swap'],
            rx_tx_factor = flavor['rxtx_factor'],
            is_public = flavor['os-flavor-access:is_public'],
            extra_specs = flavor['properties'],
            projects = [] if flavor['access_project_ids'] is None else [projects_by_id[pid] for pid in flavor['access_project_ids']],
        )
    return flavors

@dataclass
class RoleAssignment:
    role: dict
    group: dict
    project: dict

    def to_data(self):
        return {
            "role": self.role["Name"],
            "group": self.group["Name"],
            "project": self.project["Name"],
        }

    def to_import(self):
        role_name = self.role["Name"]
        role_id = self.role['ID']
        group_name = self.group["Name"]
        group_id = self.group['ID']
        project_name = self.project["Name"]
        project_id = self.project["ID"]
        domain_id = user_id = ''
        tofu_address = f'module.openstack.openstack_identity_role_assignment_v3.role_assign["{project_name}:{group_name}:{role_name}"]'
        tofu_id = f'{domain_id}/{project_id}/{group_id}/{user_id}/{role_id}'
        return [fmt_import(tofu_address, tofu_id)]

def load_role_assigments(project_names, group_names):

    # create dicts keyed by ID so can lookup names:
    roles = {e['ID']: e for e in run_os_cmd(f"openstack role list --format json")}
    projects = {e['ID']: e for e in run_os_cmd(f"openstack project list --format json")}
    groups = {e['ID']: e for e in run_os_cmd(f"openstack group list --format json")}

    role_assignments = []
    for ra in run_os_cmd(f"openstack role assignment list --format json"):
        # will always have a Role (id), but Group or Project fields may be ''
        role_id, project_id, group_id = ra['Role'], ra['Project'], ra['Group']
        project_name = projects[project_id]['Name'] if project_id else None
        group_name = groups[group_id]['Name'] if group_id else None
        if project_name in project_names and group_name in group_names:
            role_assignment = RoleAssignment(
                role=roles[role_id],
                group = groups[group_id],
                project = projects[project_id]
            )
            role_assignments.append(role_assignment)
    return role_assignments

def get_git_ref():
    # Exact tag: tuple is only integers
    if all(isinstance(x, int) for x in _version.__version_tuple__):
        return f"v{_version.__version__}"

    # Otherwise not on a tag: use commit
    commit = _version.__commit_id__
    if commit.startswith("g"):
        commit = commit[1:]
    return commit

def main():

    default_module = f"{MODULE_SOURCE}?ref={get_git_ref()}"

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='main.tf', help="name for created file containing OpenTofu configuration (default: main.tf)")
    parser.add_argument('--imports', default='imports.tf', help="name for created file containing import blocks (default: imports.tf)")
    parser.add_argument('--output', default='.', help="path to directory containing created files (default: cwd)")
    parser.add_argument('--projects', nargs="+", help="space-separated list of projects to import (default: all)")
    parser.add_argument('--groups', nargs="+", help="space-separated list of groups to import (default: all)")
    parser.add_argument('--users', nargs="+", help="space-separated list of users to import (default: all in 'default' domain)")
    parser.add_argument('--flavors', nargs="+", help="space-separated list of flavors to import (default: all)")
    parser.add_argument('--module', default=default_module, help=f"path to provide for opentof module, default {default_module}")
    # for role assignments, only those covered by project AND group should match
    args = parser.parse_args()

    # run API queries:
    project_objs = load_projects(args.projects)
    group_objs = load_groups(args.groups)
    role_assign_objs = load_role_assigments(project_objs, group_objs)
    user_objs = load_users(args.users)
    flavor_objs = load_flavors(args.flavors)

    # create a datastructure with the config in Python form:
    config_py = {
        ("module", "openstack"):{
            "source":f"{args.module}",
            "projects":{n: p.to_data() for n, p in project_objs.items()},
            "groups":{g.name: g.description for g in group_objs.values()},
            "role_assignments": [r.to_data() for r in role_assign_objs],
            "users":{n: u.to_data() for n, u in user_objs.items()},
            "flavors": {n: f.to_data() for n, f in flavor_objs.items()},
        }
    }

    # convert to hcl config:
    config_hcl=hcl.to_hcl(config_py)
    config_path = Path(args.output).joinpath(args.config)
    with open(config_path, 'w') as config_file:
        config_file.write(config_hcl)
    print(f'written {config_path}')

    # convert to hcl import blocks:
    objs = flatten(
        (
            project_objs.values(),
            group_objs.values(),
            role_assign_objs,
            user_objs.values(),
            flavor_objs.values(),
        )
    )
    import_path = Path(args.output).joinpath(args.imports)
    with open(import_path, 'w') as imports_file:
        for o in objs:
            imports_file.write('\n'.join(o.to_import()) + '\n')
    print(f'written {import_path}')

if __name__ == "__main__":
    main()
