## Sharetypes

To create a sharetype,

Example usage:

```console
sharetypes = {
    client_sharetype = {
      name = "client-vast"
      description = "client - data"
      is_public = false

      extra_specs = {
        driver_handles_share_servers = false
        snapshot_support = true
        share_backend_name = "VAST"
        vippoolname = "client_manila"
      }
    }
}
```

Argument reference:
- `description` (Optional) string
- `is_public` (Optional) bool, default true
- `extra_specs` (Required), block supports:
    - `driver_handles_share_servers` (Required) bool
    - `snapshot_support` (Optional) bool
    - `share_backend_name` (Required) string
    - `vippoolname` (Required) string

## Sharetypes Access

For projects to have access to the correct sharetypes,  the `sharetypes_access`
resource is used.

To create a sharetype access,

Example usage:

```console
sharetypes-access = {
    "client4_sharetype_access" = {
      sharetype_name = "client4_sharetype"
      project = "client"
    }
}
```

Argument reference:
One is required:
- `sharetype_name` string
or
- `share_type_id` string
One is required:
- `project` string
or
- `project_id` string

## Shares ?

To create a share,

Example usage:

```console
shares = {

}
```


Argument reference:
- `share_proto` (Required) string
- `size` (Required) number
- `region` (Optional) string
- `description` (Optional) string
- `share_type` (Optional) string
