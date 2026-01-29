#!/usr/bin/env python3

import sys, subprocess, json, pprint

class OSCmd:
    def __init__(self, cmdstr):
        self.cmdstr = cmdstr
    def __call__(self, **args):

        expanded_cmd = self.cmdstr.format(**args)
        cmd_list = ["openstack"] + expanded_cmd.split() + ["-f", "json"]
        print('calling', cmd_list)
        p = subprocess.run(cmd_list, text=True, capture_output=True)
        # todo: error handling!
        return json.loads(p.stdout)

project = {
    "description": OSCmd("project show {project_name} -c description"),
    "quotas": {
        "compute": OSCmd("quota show --compute {project_name}")
        }
}



def call(cmd):
    cmd_list = ["openstack"] + cmd.split() + ["-f", "json"]
    print(cmd_list)
    p = subprocess.run(cmd_list, text=True, capture_output=True)
    # todo: error handling!
    return json.loads(p.stdout)

if __name__ == "__main__":
    project_name = sys.argv[1]

    for tmpl in [project['description'], project['quotas']['compute']]:
    
        data = tmpl(project_name=project_name)
        pprint.pprint(data)
