#!/usr/bin/env python3

#from pprint import pprint
#import json

from .to_hcl import to_hcl

def import_project(conn, args):
    os_project = conn.identity.find_project(args.project)
    if os_project:
        os_network_quota = conn.network.get_quota(os_project.id)
        os_compute_quota = conn.compute.get_quota_set(os_project.id)
        os_blockstorage_quota = conn.block_storage.get_quota_set(os_project.id)
        project = Project(os_project)
        project.quotas = [Quota(v) for v in (os_network_quota, os_compute_quota, os_blockstorage_quota)]
    
    # project.to_import()
    # print('import_project:', args)

    print(project.to_config())
    
OS_DEFAULT_VALUES = (None, {}, -1)

IMPORT_BLOCK_TEMPLATE = """
import {{
  to = module.{module_name}.{instance_address}
  id = "{resource_id}"
}}
"""

class Quota:
    
    def __init__(self, os_quota):
        self.os_quota = os_quota
    
    def to_config(self):
        config = {}
        for k, v in self.os_quota.items():
            if v not in OS_DEFAULT_VALUES and k not in ('location', 'id', 'project_id'):
                config[k] = v
        return config
    
class Project:

    def __init__(self, os_project):
        self.os_project = os_project
        self.quota = None
    
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

    def to_import(self):
        print(
            IMPORT_BLOCK_TEMPLATE.format(
                module_name = 'openstack',
                instance_address = f'openstack_identity_project_v3.project["{self.os_project.name}"]',
                resource_id = self.os_project.id,
            )
        )


