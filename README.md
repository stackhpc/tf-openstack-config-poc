# README

Proof of concept for an OpenTofu-based replacement for the Ansible [openstack-config](https://github.com/stackhpc/openstack-config/) for projects with federated users.

This contains:

- `modules/openstack_config`: An OpenTofu module to manage OpenStack config.
  A single module instantiation may define multiple resources within a single
  domain.
- `examples/`: Examples of using the module. The `arcus/main.tf` example
  demonstrates two projects, with relevant groups and role assignments. An
  existing Keystone user is used to "fake" a federated user. The example also
  demonstrates how OpenTofu variables can be used similarly to indirection in
  Ansible to define the same quotas once for multiple projects.

This is not production-ready and does not contain any variable typing/checks or
docs.

## Usage

With a `clouds.yaml` and `OS_CLOUD`/`OS_CLIENT_CONFIG_FILE` set as necessary run

```shell
cd examples/EXAMPLE # select an example
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

Items marked `YES*` support "migration" - see section below. Items marked `NEW`
are additional functionality not supported in openstack-config

- TODO: openstack_domains
  - Still don't entirely understand TF approach/resources for these.
  - Expecting domains to be pre-existing, but may want to support multiple domains.
- YES*: openstack_projects:
  - YES*: name
  - YES*: description
  - TODO: project_domain
  - TODO: user_domain
  - NO: keypairs
  - YES*: quotas
- YES*: groups
- YES*: users - **WARNING: passwords will be stored in state!**
- NEW: role assignments
- NO: openstack_routers
- NO: openstack_security_groups
- YES: openstack_networks_rbac
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
 Error: Error unassigning openstack_identity_role_assignment_v3 ...: Successfully re-authenticated, but got error executing request: Expected HTTP response code [204] when accessing [DELETE ..., but got 401 instead: {"error":{"code":401,"message":"The request you have made requires authentication.","title":"Unauthorized"}}
 ```

worked on 3rd attempt :-(

I can't fix this with depends_on, I think this is a genuine bug?

## Migration
This repository contains some additional, experimental tooling to define inputs
for this repo based on existing OpenStack resources.

To set this up run:

```shell
python3 -m venv venv
. venv/bin/activate
pip install -U pip
pip install python-openstackclient==8.0.0 # NB won't work on later due to formatting errors
```

Then run

```shell
migrate.py
```

to query OpenStack and generate:
- `main.tf` - an example configuration using this module
- `imports.tf` - [import blocks](https://opentofu.org/docs/language/import/)
  linking the above configuration to the cloud resources

Run `migrate.py -h` to see options controlling this process.

The generated files should be reviewed and if necessary, modified. Note not all
features currently support migration.

To then actually import these resources into the OpenTofu state run:

```shell
tofu init # if necessary
tofu apply
```

noting where the plan indicates resources will be imported.

Note that the import blocks in the `imports.tf` file are idempotent; once
the configuration has been "applied" to import them, this file may be removed
or left/committed, it does not matter.

## TODO
- Fix user passwords ending up in state?
