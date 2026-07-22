## Flavors

To create a flavor,

Example usage:

```console
flavors = {
        "test-flavour" = {
            ram          = 4096
            vcpus        = 1
            disk         = 50
            ephemeral    = 0
            swap         = 0
            rx_tx_factor = 1.0
            is_public    = true
            extra_specs = {
            }
            projects = [
                "client", "client-other-project"
            ]
        }
}
```

Argument reference:
- `ram` (Required) number. Value in megabytes. Changing this creates a new flavor.
- `vcpus` (Required) number. Changing this creates a new flavor.
- `disk` (Required) number. Value in GiB. Changing this creates a new flavor.
- `ephemral` (Optional) number. Changing this creates a new flavor.
- `swap` (Optional) number. The amount of disk space in megabytes to use. Changing this creates a new flavor.
- `rx_tx_factor` (Optional) number. Changing this creates a new flavor.
- `is_public` (Optional) bool, default true. If "projects" is non-empty this is ignored and set false. Changing this creates a new flavor.
- `flavor_id` (Optional) string. Changing this creates a new flavor access
- `extra_specs` (Optional) map of strings
- `projects` (Optional) list of strings. Project names to have access to the flavor. Changing this creates a new flavor access.
