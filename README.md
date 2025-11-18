# README

Proof of concept for an OpenTofu-based replacement for the Ansible [openstack-config](https://github.com/stackhpc/openstack-config/) for projects with federated users.

This contains:

- `modules/openstack`: An OpenTofu module to manage OpenStack projects and related
  configuration. A module instantiation may define multiple projects within a
  single domain.
- `main.tf`: An example of using that module to define two projects, with
  relevant groups and role assignments. An existing Keystone user is used to
  "fake" a federated user. The example also demonstrates how OpenTofu variables
  can be used similarly to indirection in Ansible to define the same quotas once
  for multiple projects.

This is not production-ready and does not contain any variable typing/checks or
docs.

## Usage

With a `clouds.yaml` and `OS_CLOUD`/`OS_CLIENT_CONFIG_FILE` set as necessary run

```shell
tofu init
tofu apply
```

The generated resources can be deleted using
```shell
tofu destroy
```

By default OpenTofu will process 10 operations concurrently as it walks the
resource graph. This can be increased using the `-parallelism=N` option.

## Comparison to stackhpc/openstack-config

This section provides an initial comparison of functionality vs:
- https://github.com/stackhpc/openstack-config/blob/main/etc/openstack-config/openstack-config.yml
- https://github.com/stackhpc/ansible-collection-openstack/tree/main/roles

Note this is not currentky complete either in breadth or depth!

- TODO: openstack_domains
  - Still don't entirely understand TF approach/resources for these.
  - Expecting domains to be pre-existing, but may want to support multiple domains.
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
- TODO: openstack_flavors
    - will provide flavor RBAC instead
- NO: openstack_host_aggregates
- NO: openstack_images
- OUT OF SCOPE: openstack_image_elements
- OUT OF SCOPE: openstack_image_git_elements
- OUT OF SCOPE: openstack_container_clusters_templates
- NO: openstack_ratings_hashmap_field_mappings
- NO: openstack_ratings_hashmap_service_mappings

## Current Issues
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
