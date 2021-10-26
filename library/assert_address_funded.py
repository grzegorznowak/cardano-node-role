from ansible.module_utils.basic import AnsibleModule


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


def get_lovelace_from_utxo(raw_utxo_table, max_tx_count = 0):
    # Calculate total lovelace of the UTXO(s) inside the wallet address
    if max_tx_count == 0:
        return sum([int(row.split()[2]) for row in raw_utxo_table.strip().splitlines()[2:]])
    else:
        # with the tx limit we accumulate max no. of transactions
        # with the highest amount of ada only
        return sum(sorted([int(row.split()[2])
                           for row
                           in raw_utxo_table.strip().splitlines()[2:]],
                          reverse=True)[:max_tx_count])


def main():

    argument_spec = dict(
        cardano_node_socket=dict(type='str', required=True),
        cardano_bin_path=dict(type='path', default='~/bin'),
        expected_lovelace=dict(type='int', required=True),
        address=dict(type='str', required=True),
        max_tx=dict(type='int', default=0),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_node_socket = module.params['cardano_node_socket']
    max_tx = module.params['max_tx']
    active_network = module.params['active_network']
    testnet_magic = module.params['testnet_magic']
    payment_address = module.params['address']
    cardano_bin_path = module.params['cardano_bin_path']
    expected_lovelace = module.params['expected_lovelace']


    utxo_command = create_utxo_command(cardano_node_socket,
                                       active_network,
                                       testnet_magic,
                                       cardano_bin_path,
                                       payment_address)

    code, utxo_response, stderr = module.run_command(utxo_command,
                                                     use_unsafe_shell=True)

    if code != 0 or stderr != "":
        module.fail_json(msg="Error querying utxo. Make sure the node is fully synced.",
                         code=code,
                         stderr=stderr,
                         lovelace=0,
                         command=utxo_command)

    assert code == 0
    assert stderr == ""

    total_lovelace = get_lovelace_from_utxo(utxo_response, max_tx)

    if total_lovelace < expected_lovelace:
        module.fail_json(msg="Expected amount of lovelace not present", lovelace=total_lovelace)
    else:
        module.exit_json(changed=False, lovelace=total_lovelace)


if __name__ == '__main__':
    main()
