variable "projects" {
    type = any
}

module "projects" {
    source = "./../project"
    for_each = var.projects

    name = each.key
    description = each.value.description
    quotas = each.value.quotas
}

output "projects" {
    value = {for k, v in var.projects: k => module.projects[k].id}
}
