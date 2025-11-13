# README

## Issues
Hit this on apply:

```
│ Error: Provider produced inconsistent result after apply
│ 
│ When applying changes to module.roleB.openstack_identity_role_assignment_v3.A, provider "provider[\"registry.opentofu.org/hashicorp/openstack\"]" produced an unexpected new value: root object was present, but now absent.
│ 
│ This is a bug in the provider, which should be reported in the provider's own issue tracker.
```
But reapplying fixed it ...

Also not idempotent:

```
  # module.openstack.module.projects["sb-test-1"].openstack_blockstorage_quotaset_v3.project will be updated in-place
  ~ resource "openstack_blockstorage_quotaset_v3" "project" {
        id                   = "75dc3b8cb1324ea6a899c8281b9ff84b/RegionOne"
      ~ volume_type_quota    = {
          - "gigabytes___DEFAULT__"                          = "-1" -> null
          - "gigabytes_arcus-staging-ceph01-rbd"             = "-1" -> null
          - "gigabytes_arcus-staging-ceph01-rbd-multiattach" = "-1" -> null
          - "snapshots___DEFAULT__"                          = "-1" -> null
          - "snapshots_arcus-staging-ceph01-rbd"             = "-1" -> null
          - "snapshots_arcus-staging-ceph01-rbd-multiattach" = "-1" -> null
          - "volumes___DEFAULT__"                            = "-1" -> null
          - "volumes_arcus-staging-ceph01-rbd-multiattach"   = "-1" -> null
            # (1 unchanged element hidden)
        }
        # (9 unchanged attributes hidden)
    }
```

Hit this:
```
 Error: Error unassigning openstack_identity_role_assignment_v3 /ae96a9616a654075ba50a1e3daaef19f/7aef976453af48078d1740fa5542c974//0c7cb73501e740b995b660dc1b7d53fa: Successfully re-authenticated, but got error executing request: Expected HTTP response code [204] when accessing [DELETE https://arcus.staging.openstack.hpc.cam.ac.uk:5000/v3/projects/ae96a9616a654075ba50a1e3daaef19f/groups/7aef976453af48078d1740fa5542c974/roles/0c7cb73501e740b995b660dc1b7d53fa], but got 401 instead: {"error":{"code":401,"message":"The request you have made requires authentication.","title":"Unauthorized"}}
 ```

worked on 3rd attempt :-(

## TODO
- flavor permissions
- network RBAC
- work out if we want to abstract it further
- sort out defaults/typing etc


## Comparison to stackhpc/openstack-config

C.f.:
- https://github.com/stackhpc/openstack-config/blob/main/etc/openstack-config/openstack-config.yml
- https://github.com/stackhpc/ansible-collection-openstack/tree/main/roles

This is not complete either in breadth or depth!

- TODO: openstack_domains - do we create these?? Do we need to be able to create projects etc in existing domains?
- YES: openstack_projects:
  - YES: name
  - YES: description
  - TODO: project_domain
  - TODO: user_domain
  - NO: users
  - NO: keypairs
  - YES: quotas
- NO: openstack_routers
- NO: openstack_security_groups
- TODO: openstack_networks_rbac
- NO: openstack_flavors
- NO: openstack_host_aggregates
- NO: openstack_images
- OUT OF SCOPE: openstack_image_elements
- OUT OF SCOPE: openstack_image_git_elements
- OUT OF SCOPE?: openstack_container_clusters_templates
- NO: openstack_ratings_hashmap_field_mappings
- NO: openstack_ratings_hashmap_service_mappings