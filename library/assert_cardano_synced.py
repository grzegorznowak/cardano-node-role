from ansible.module_utils.basic import AnsibleModule

import os
import json
import subprocess

from library.cardano_wallet import (
    collect_wallets,
    BrokenWalletsError,
)


def query_tip(active_network, testnet_magic, cardano_bin_path):

    raw_utxo_table = None
    if active_network == 'test':
        raw_response = subprocess.check_output(
            [cardano_bin_path, 'query', 'tip', '--testnet-magic', testnet_magic])
    elif active_network == 'main':
        raw_response = subprocess.check_output(
            [cardano_bin_path, 'query', 'utxo', '--mainnet'])

    return raw_response


def get_progress_from_response(raw_response):
    return float(json.loads(raw_response)['syncProgress'])



def main():

    argument_spec = dict(
        wanted_progress=dict(type='float', default='100'),
        cardano_bin_path=dict(type='path', default='~/bin'),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    active_network = module.params['active_network']
    wanted_progress = module.params['wanted_progress']
    testnet_magic = module.params['testnet_magic']
    cardano_bin_path = module.params['cardano_bin_path']

    sync_progress = get_progress_from_response(query_tip(
        active_network,
        testnet_magic,
        cardano_bin_path
    ))

    if sync_progress >= wanted_progress:
        module.fail_json(msg="Expected progress not achieved yet", progress=sync_progress)
    else:
        module.exit_json(changed=False, progress=sync_progress)

if __name__ == '__main__':
    main()