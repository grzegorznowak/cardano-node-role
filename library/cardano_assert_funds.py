from ansible.module_utils.basic import AnsibleModule

import os
import subprocess

from library.cardano_wallet import (
    collect_wallets,
    BrokenWalletsError,
)


def query_utxo(active_network, testnet_magic, cardano_bin_path, wallet_address):

    raw_utxo_table = None
    if active_network == 'test':
        raw_utxo_table = subprocess.check_output(
            [cardano_bin_path, 'query', 'utxo', '--testnet-magic', testnet_magic, '--address',
             wallet_address])
    elif active_network == 'main':
        raw_utxo_table = subprocess.check_output(
            [cardano_bin_path, 'query', 'utxo', '--mainnet', '--address',
             wallet_address])

    return raw_utxo_table


def get_lovelace_from_utxo(raw_utxo_table):
    # Calculate total lovelace of the UTXO(s) inside the wallet address
    return sum([int(row.split()[2]) for row in raw_utxo_table.strip().splitlines()[2:]])


def main():

    argument_spec = dict(
        cardano_bin_path=dict(type='path', default='~/bin'),
        wallets_path=dict(type='path', default='~/wallets'),
        wallet_name=dict(type='str', required=True),
        expected_lovelace=dict(type='int', required=True),
        vkey_file=dict(type='str', default='payment.vkey'),
        skey_file=dict(type='str', default='payment.skey'),
        addr_file=dict(type='str', default='payment.addr'),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    active_network = module.params['active_network']
    testnet_magic = module.params['testnet_magic']
    wallets_path = module.params['wallets_path']
    wallet_name = module.params['wallet_name']
    vkey_file = module.params['vkey_file']
    skey_file = module.params['skey_file']
    addr_file = module.params['addr_file']
    cardano_bin_path = module.params['cardano_bin_path']
    expected_lovelace = module.params['expected_lovelace']

    # make sure we're checking against a non-broken wallet
    try:
        wallets_info = collect_wallets(wallets_path=wallets_path,
                                       wallet_names=[wallet_name],
                                       vkey_file=vkey_file,
                                       skey_file=skey_file,
                                       addr_file=addr_file)
    except BrokenWalletsError as wallets_error:
        module.fail_json(msg=wallets_error)

    # double check if we returned with one and only one wallet
    assert len(wallets_info) == 1

    payment_addr_path = "{}/wallet1/skey"/format
    # Read wallet address value from payment.addr file
    with open(wallets_info[0]['addr'], 'r') as file:
        wallet_address = file.read()

        total_lovelace = get_lovelace_from_utxo(query_utxo(active_network, testnet_magic, cardano_bin_path, wallet_address))

    if total_lovelace < expected_lovelace:
        module.fail_json(msg="Expected amount of lovelace not present", lovelace=total_lovelace)
    else:
        module.exit_json(changed=False, lovelace=total_lovelace)

if __name__ == '__main__':
    main()