## Users

To create a new user,

Example usage:

```console
users = {
    "<username>" = {
        name            = "bob"
        default_project = "client"
        email           = "bob@client.com"
        description     = "Bob from client"
        groups = [
            "admin:client",
            "member:client-other-project"
        ]
    }
}
```

Argument reference:
- `description` (Optional) string
- `email` (Optional) string
- `groups` (Optional) string
- `password` (Optional) string
- `default_project` (Optional) string. Project name.

For users to have access to projects - groups and role assignments need to be created. Users are then assigned the corresponding groups that match their `role:project` needs.

## Groups

To create a group, add config to `group-config.tf`.

Template:

```console
group-config = {
    "admin:client" = "Admins of client project"
    "member:client" = "Members of client project"
    ...
}
```

Argument reference:
- `description` (Optional) string

## Role assignment

To create a role,

Available roles can be seen by running `openstack role list`

Example usage:

```console
    role_assignments = [
        {
            role    = "admin"
            group   = "admin:client"
            project = "client"
        },
        {
            role    = "member"
            group   = "member:client-other-project"
            project = "client-other-project"
        },
        ...
    ]
```

Argument reference:
- `role` (Required) string. Role name, available roles found by running `openstack role list`.
- `group` (Required) string. Group name.
- `project` (Required) string. Project name.