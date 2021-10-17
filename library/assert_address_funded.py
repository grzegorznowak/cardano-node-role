from ansible.module_utils.basic import AnsibleModule

import os
import subprocess


def create_utxo_command(cardano_node_socket, active_network, testnet_magic, cardano_bin_path, wallet_address):

    command = ""
    if active_network == 'test':
        command = "CARDANO_NODE_SOCKET_PATH={0} " \
                  "{1}/cardano-cli query utxo " \
                  "--testnet-magic {2} --address {3}".format(cardano_node_socket,
                                                          cardano_bin_path,
                                                          testnet_magic,
                                                          wallet_address)
    elif active_network == 'main':
        command = "CARDANO_NODE_SOCKET_PATH={0} " \
                  "{1}/cardano-cli query utxo " \
                  "--mainnet --address {2}".format(cardano_node_socket,
                                               cardano_bin_path,
                                               wallet_address)

    return command


def get_lovelace_from_utxo(raw_utxo_table):
    # Calculate total lovelace of the UTXO(s) inside the wallet address
    return sum([int(row.split()[2]) for row in raw_utxo_table.strip().splitlines()[2:]])


def main():

    argument_spec = dict(
        cardano_node_socket=dict(type='str', required=True),
        cardano_bin_path=dict(type='path', default='~/bin'),
        expected_lovelace=dict(type='int', required=True),
        address_file=dict(type='str', required=True),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_node_socket = module.params['cardano_node_socket']
    active_network = module.params['active_network']
    testnet_magic = module.params['testnet_magic']
    address_file = module.params['address_file']
    cardano_bin_path = module.params['cardano_bin_path']
    expected_lovelace = module.params['expected_lovelace']

    with open(address_file, 'r') as file:
        payment_address = file.read()
        utxo_command = create_utxo_command(cardano_node_socket,
                                           active_network,
                                           testnet_magic,
                                           cardano_bin_path,
                                           payment_address)

        code, utxo_response, stderr = module.run_command(utxo_command,
                                                         use_unsafe_shell=True)

        if code != 0 or stderr != "":
            module.fail_json(msg="Error runnig utxo",
                             code=code,
                             stderr=stderr,
                             command=utxo_command)

        assert code == 0
        assert stderr == ""

        total_lovelace = get_lovelace_from_utxo(utxo_response)

        if total_lovelace < expected_lovelace:
            module.fail_json(msg="Expected amount of lovelace not present", lovelace=total_lovelace)
        else:
            module.exit_json(changed=False, lovelace=total_lovelace)

if __name__ == '__main__':
    main()