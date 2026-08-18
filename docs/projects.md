## Projects

To create a project, add the config to `project-config.tf`.

Example Usage:

```console
projects = {
    "client" = {
      description = "client project"
      compute_quota = {
        key_pairs            = 100
        ram                  = -1
        cores                = -1
        instances            = 10
        server_groups        = 10
        server_group_members = 10
      }

      blockstorage_quota = {
        volumes              = 50
        snapshots            = 10
        gigabytes            = 100
        per_volume_gigabytes = 20
        backups              = 10
        backup_gigabytes     = 1000
        groups               = 10
      }

     network_quota = {
        floating_ips        = 50
        network             = 100
        port                = 500
        rbac_policy         = 10
        router              = 10
        subnet              = 100
        subnetpool          = -1
        security_group_rule = 100
        security_group      = 10
      }
    }
}
```

Argument reference:
- `description` (Optional) string
- `compute_quota` (Required), block supports:
    - `key_pairs` (Optional) number
    - `ram` (Optional) number
    - `cores` (Optional) number
    - `instances` (Optional) number
    - `server_groups` (Optional) number
    - `server_group_members` (Optional) number
- `blockstorage_quota` (Required), block supports:
    - `volumes` (Optional) number
    - `snapshots` (Optional) number
    - `gigabytes` (Optional) number
    - `per_volume_gigabytes` (Optional) number
    - `backups` (Optional) number
    - `backup_gigabytes` (Optional) number
    - `groups` (Optional)  number
    - `volume_type_quota` (Optional) map
- `network_quota` (Required), block supports:
    - `floatingip` (Optional) number
    - `network` (Optional) number
    - `port` (Optional) number
    - `rbac_policy` (Optional) number
    - `router` (Optional) number
    - `security_group` (Optional) number
    - `security_group_rule` (Optional) number
    - `subnet` (Optional) number
    - `subnetpool` (Optional) number
