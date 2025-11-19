#!/usr/bin/env python3

#from pprint import pprint
#import json
import openstack
from textwrap import dedent
from .to_hcl import to_hcl

def import_project(conn, args):
    os_project = conn.identity.find_project(args.project)
    if os_project:
        os_network_quota = conn.network.get_quota(os_project.id)
        os_compute_quota = conn.compute.get_quota_set(os_project.id)
        os_blockstorage_quota = conn.block_storage.get_quota_set(os_project.id)
        project = Project(os_project)
        project.quotas = [Quota(v, os_project.name) for v in (os_network_quota, os_compute_quota, os_blockstorage_quota)]
    
    print('# --- project import blocks ---')
    print(project.to_import_blocks())
    print()
    print('#--- project configuration ---')
    print(project.to_config())
    print()

class OpenStackResource:
    # this is used with str.format() so '{{' -> '{'
    IMPORT_BLOCK_TEMPLATE = """
        import {{
          to = module.{module_name}.{state_address}
          id = "{resource_id}"
        }}"""
    OS_DEFAULT_VALUES = (None, {}, -1)
    
    def to_import_blocks(self):
        out = dedent(self.IMPORT_BLOCK_TEMPLATE).format(
            module_name = 'openstack',
            state_address = self.state_address,
            resource_id = self.resource_id,
            )
        return out.strip()

class Quota(OpenStackResource):
    
    def __init__(self, os_quota, project_name):
        self.os_quota = os_quota
        self.project_name = project_name
        # module.openstack.openstack_compute_quotaset_v2.project["sb-test-1"]
        # module.openstack.openstack_networking_quota_v2.project["sb-test-1"]
        # module.openstack.openstack_blockstorage_quotaset_v3.project["sb-test-1"]
        state_type = {
            'openstack.network.v2.quota': 'openstack_networking_quota_v2',
            'openstack.compute.v2.quota_set': 'openstack_compute_quotaset_v2',
            'openstack.block_storage.v3.quota_set': 'openstack_blockstorage_quotaset_v3'
        }[self.os_quota.__module__]
        self.state_address = f'{state_type}.project["{self.project_name}"]'
        self.resource_id = f'{self.os_quota.id}/{self.os_quota.location.region_name}'
    
    def to_config(self):
        config = {}
        for k, v in self.os_quota.items():
            if v not in self.OS_DEFAULT_VALUES and k not in ('location', 'id', 'project_id'):
                config[k] = v
        return config
    
class Project(OpenStackResource):

    def __init__(self, os_project):
        self.os_project = os_project
        self.quotas = []
        self.state_address = f'openstack_identity_project_v3.project["{self.os_project.name}"]'
        self.resource_id = self.os_project.id
    
    def to_config(self):
        quota_config = {}
        for q in self.quotas:
            quota_config.update(q.to_config())
        config = dict(
            name=self.os_project.name,
            description = self.os_project.description,
            quotas = quota_config,
        )
        return to_hcl(dict(projects=config))

    def to_import_blocks(self):
        blocks = [super().to_import_blocks()] + [v.to_import_blocks() for v in self.quotas]
        return '\n'.join(blocks)

