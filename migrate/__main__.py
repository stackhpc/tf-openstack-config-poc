import argparse
import openstack

from . import lib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()
    parser_project = subparsers.add_parser('project', help='Import OpenStack project')
    parser_project.add_argument('project')#, help='action to take')
    parser_project.set_defaults(func=lib.import_project)
    args = parser.parse_args()

    conn = openstack.connection.from_config()

    args.func(conn, args)
    #print(args)

