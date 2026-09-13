import optparse
import json
from typing import TypedDict

from ascenderkit.utils import random_title


class InventoryGroup(TypedDict):
    """One group of the Ansible dynamic inventory format.

    The `_meta` key of the inventory carries host variables rather than a group,
    so it is built separately and joined on at the end. Keeping the two apart is
    what lets `hosts` and `children` be known lists here.
    """

    hosts: list[str]
    children: list[str]
    vars: dict[str, str]


def upload_inventory(ansible_runner, nhosts=10, ini=False):
    """Helper to upload inventory script to target host"""
    # Create an inventory script
    if ini:
        copy_mode = '0644'
        copy_dest = f'/tmp/inventory{random_title()}.ini'
        copy_content = ini_inventory(nhosts)
    else:
        copy_mode = '0755'
        copy_dest = f'/tmp/inventory{random_title()}.sh'
        copy_content = '''#!/bin/bash
cat <<EOF
{json_inventory(nhosts)}
EOF'''

    # Copy script to test system
    contacted = ansible_runner.copy(dest=copy_dest, force=True, mode=copy_mode, content=copy_content)
    for result in contacted.values():
        assert not result.get('failed', False), f"Failed to create inventory file: {result}"
    return copy_dest


def generate_inventory(nhosts=100):
    """Generate a somewhat complex inventory with a configurable number of hosts"""
    groups: dict[str, InventoryGroup] = {}
    hostvars: dict[str, dict[str, str | int]] = {}

    for n in range(nhosts):
        hostname = f'host-{n:08d}.example.com'
        group_evens_odds = 'evens.example.com' if n % 2 == 0 else 'odds.example.com'
        group_threes = 'threes.example.com' if n % 3 == 0 else ''
        group_fours = 'fours.example.com' if n % 4 == 0 else ''
        group_fives = 'fives.example.com' if n % 5 == 0 else ''
        group_sixes = 'sixes.example.com' if n % 6 == 0 else ''
        group_sevens = 'sevens.example.com' if n % 7 == 0 else ''
        group_eights = 'eights.example.com' if n % 8 == 0 else ''
        group_nines = 'nines.example.com' if n % 9 == 0 else ''
        group_tens = 'tens.example.com' if n % 10 == 0 else ''
        # Integer division: these were true division, which made the argument a
        # float that %d truncated. The result is the same for the non-negative n
        # range() produces, and the value is now the integer the format says.
        group_by_10s = f'group-{n // 10:07d}X.example.com'
        group_by_100s = f'group-{n // 100:06d}XX.example.com'
        group_by_1000s = f'group-{n // 1000:05d}XXX.example.com'
        for group in [group_evens_odds, group_threes, group_fours, group_fives, group_sixes, group_sevens, group_eights, group_nines, group_tens, group_by_10s]:
            if not group:
                continue
            if group in groups:
                groups[group]['hosts'].append(hostname)
            else:
                groups[group] = {'hosts': [hostname], 'children': [], 'vars': {'group_prefix': group.split('.')[0]}}
        if group_by_1000s not in groups:
            groups[group_by_1000s] = {'hosts': [], 'children': [], 'vars': {'group_prefix': group_by_1000s.split('.')[0]}}
        if group_by_100s not in groups:
            groups[group_by_100s] = {'hosts': [], 'children': [], 'vars': {'group_prefix': group_by_100s.split('.')[0]}}
        if group_by_100s not in groups[group_by_1000s]['children']:
            groups[group_by_1000s]['children'].append(group_by_100s)
        if group_by_10s not in groups[group_by_100s]['children']:
            groups[group_by_100s]['children'].append(group_by_10s)
        hostvars[hostname] = {
            'ansible_user': 'example',
            'ansible_connection': 'local',
            'host_prefix': hostname.split('.')[0],
            'host_id': n,
        }

    # `_meta` first, then the groups in the order they were met, which is the
    # order the single dict produced before.
    return {'_meta': {'hostvars': hostvars}, **groups}


def json_inventory(nhosts=10):
    """Return a JSON representation of inventory"""
    return json.dumps(generate_inventory(nhosts), indent=4)


def ini_inventory(nhosts=10):
    """Return a .INI representation of inventory"""
    output = list()
    inv_list = generate_inventory(nhosts)

    for group in inv_list.keys():
        if group == '_meta':
            continue

        # output host groups
        output.append(f'[{group}]')
        for host in inv_list[group].get('hosts', []):
            output.append(host)
        output.append('')  # newline

        # output child groups
        output.append(f'[{group}:children]')
        for child in inv_list[group].get('children', []):
            output.append(child)
        output.append('')  # newline

        # output group vars
        output.append(f'[{group}:vars]')
        for k, v in inv_list[group].get('vars', {}).items():
            output.append(f'{k}={v}')
        output.append('')  # newline

    return '\n'.join(output)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--json', action='store_true', dest='json')
    parser.add_option('--ini', action='store_true', dest='ini')
    parser.add_option('--host', dest='hostname', default='')
    parser.add_option('--nhosts', dest='nhosts', action='store', type='int', default=10)
    options, args = parser.parse_args()
    if options.json:
        print(json_inventory(nhosts=options.nhosts))
    elif options.ini:
        print(ini_inventory(nhosts=options.nhosts))
    elif options.hostname:
        print(json_inventory(nhosts=options.nhosts)['_meta']['hostvars'][options.hostname])
    else:
        print(json.dumps({}, indent=4))
