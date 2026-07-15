================================
Tofu OpenStack Config User Guide
================================

Tofu OpenStack Config allows you to manage your OpenStack config using Terraform.
This guide will provide you with example templates for available resources. A full
list of variables available for each resource can be found in `variables.tf`_,
with a description and type.

It is recommended for easy readibility to separate your resources in ``main.tf``
as follows:

.. code-block:: console

    module "openstack" {
        source =

        projects = local.project-config
        networks = local.network-config
        ...
    }

The config for each resource can then be written into separate files, suggested
format is ``<resource>-config.tf``, for example:

- project-config.tf
- network-config.tf
- router-config.tf

Projects
---------

To create a project, add config to ``project-config.tf``.

Template:

.. code-block:: console

    locals {
        project-config = {
             ## start of template
            "<your-project-name>" = {
                description =
                computa_quota = {
                    cores     =
                    instances =
                    ram       =
                    ....
                }
                network_quota = {
                    networks      =
                    ports         =
                    rbac_policies =
                    ....
                }
                blockstorage_quota = {
                    volumes   =
                    snapshots =
                    gigbytes  =
                    ....
                }
            }
            ## end of template
        }
    }

Flavors
-------

To create a flavor, add config to ``flavor-config.tf``.

Template:

.. code-block:: console

    locals {
        flavor-config = {
            ## start of template
            <your-flavor-name> = {
                ram      =
                vcpus    =
                disk     =
                ...
                projects = [ ... ]
            }
            ## end of template
        }
    }

Networks
--------

To create a network, add config to ``network-config.tf``.

Template:

.. code-block:: console

    locals {
        network-config = {
            ## start of template
            "<your-tofu-network-name>" = {
                name                  = "<your-openstack-network-name>"
                shared                =
                external              =
                admin_state_up        =
                project               = "<tofu-project-name>"
                tenant_id             = # does not need to be defined if project is defined
                mtu                   =
                port_security_enabled =

                segments = [{
                    physical_network =
                    network_type     =
                    segmentation_id  =
                }]

                subnets = {
                    # first subnet config
                    "<your-tofu-subnet-name>" = {
                        name        = "<your-openstack-subnet-name>"
                        cidr        = "<cidr>"
                        ip_version  =
                        gateway_ip  = "<gateway_ip>"
                        enable_dhcp =

                        allocation_pool = [{
                            start = "<start-of-allocation-pool>"
                            end   = "<end-of-allocation-pool>"
                        }]
                    } , # subnets need to be separated by a comma (,)
                    # second subnet config
                    "<your-second-tofu-subnet-name" = {
                        name          = "<your-second-openstack-subnet-name>"
                        ip_version    =
                        no_gateway    = true

                        subnetpool_id = # found using openstack subnet pool list
                        prefix_length =
                    }
                }
            }
            ## end of template
        }
    }


Routers
-------

To create a router, add config to ``router-config.tf`` .

Template:

.. code-block:: console

    locals {
        router-config = {
            ## start of template
            "<your-tofu-router-name>" = {
                name                = "<your-openstack-router-name>"
                region              =
                external_network    = "<your-tofu-network-name>"
                # or
                external_network_id =
                project             = "<your-tofu-project-name>"
                # or
                tenant_id           =
                ...

                external_fixed_ips  = [
                { subnet    = "<your-tofu-subnet-name>" }, # external_fixed_ips need to be separated by a comma (,)
                { subnet_id = }
                ...
                ]

                interfaces = [
                { subnet = "<your-tofu-subnet-name>" }, # interfaces need to be separated by a comma (,)
                { subnet_id = }
                ...
                ]
            }
            ## end of template
        }
    }

Users
-----

To create a new user, add config to ``user-config.tf``.

Template:

.. code-block:: console

    locals {
        user-config = {
            ## start of template
            "<username>" = {
                name            = "<username>"
                default_project = "<openstack-project-name>"
                groups = [
                    "<member-project-group>",
                    "<admin-project-group>"
                    ...
                ]
            }
            ## end of template
        }
    }

For users to have access to projects - groups and roles need to be created then
users are assigned the corresponding groups that match their project:role needs.

Groups
------

To create a group, add config to ``group-config.tf``.

Template:

.. code-block:: console

    locals {
        group-config = {
        admins = ""
        ## start of template
        <your-project-group> = "<group description>"
        ## end of template
        }
    }


Roles
-----

To create a role, add config to ``role-config.tf``.

Available roles can be seen by running ``openstack role list``

Template:

.. code-block:: console

    locals {
        role-config = [
            ## start of template
            {
                role    = "member"
                group   = "<member-project-group>"
                project = "<your-project-name>"
            },
            {
                role    = "admin"
                group   = "<admin-project-group>"
                project = "<your-project-name>"
            },
            ...
            ## end of template
        ]
    }

Images
------

To create an image, add config to ``image-config.tf``.

Template:

.. code-block:: console

    locals {
        image-config = {
            ## start of template
            <your-image-name> = {
                container_format =
                disk_format      =
                image_source_url =
                ...
            }
            ## end of template
        }

Sharetypes
----------

To create a sharetype, add config to ``sharetype-config.tf``.

Template:

.. code-block:: console

    locals {
        sharetype-config = {
            ## start of template
            <tofu-sharetype-name> = {
                name        = <openstack-sharetype-name>
                description =
                is_public   =

                extra_specs = {
                    driver_handles_share_servers =
                    snapshot_support             =
                    share_backend_name           =
                    vippoolname                  = # see opentofu manila integration
                }
            }
            ## end of template
        }
    }


Sharetypes Access
-----------------

For projects to have access to the correct sharetypes,  the ``sharetypes_access``
resource is used.

To create a sharetype access, add config to ``sharetype-access.tf``.

Template:

.. code-block:: console

    locals {
        sharetype-access-config = {
            ## start of templace
            <sharetype-access-name> = {
                share_type_id =
                project       =
                # or
                project_id    =
            }
            ## end of template
        }
    }

=================================
OpenTofu Vast Manila Integration
=================================

To access the ``vippools`` resource from the `OpenTofu Vast Manila`_ module,
you need to provide the ``openstack`` module with the ``vast`` resources.
This can be done by including the following in your ``main.tf``:

.. code-block:: console

    ##main.tf
    module "openstack" {
        source = "github.com/stackhpc/tofu-openstack-config?ref=main"
        # this lines takes the vippools resources from the module "vast" into the openstack module
        vippools = module.vast.vippools
        ...
    }

    module "vast" {
        source = "github.com/stackhpc/opentofu-vast-manila?ref=main"

        vippools =
        ...
    }

.. _OpenTofu Vast Manila: https://github.com/stackhpc/opentofu-vast-manila/
.. _variables.tf: https://github.com/stackhpc/tofu-openstack-config/blob/main/variables.tf
