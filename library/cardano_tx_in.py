from ansible.module_utils.basic import AnsibleModule

def create_utxo_query_command(cardano_node_socket, active_network, testnet_magic, cardano_bin_path, wallet_address):

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

def largest_first(raw_utxo_table, wanted_amount, max_tx, used_tx = 0):

    utxo_processed = sorted([row
                             for row
                             in raw_utxo_table.strip().splitlines()[2:]],
                            key=lambda x: int(x.split()[2]),
                            reverse=True)

    accumulated_amount = 0
    txs = []
    for row in utxo_processed:
        if accumulated_amount < wanted_amount:
            tx_details = row.split()
            accumulated_amount += int(tx_details[2])
            txs.append((tx_details[0], tx_details[1]))
        else:
            break

    if accumulated_amount < wanted_amount:
        return [], accumulated_amount

    return txs, accumulated_amount

def format_cli(txs):
    return " ".join(["--tx-in {}#{}".format(tx[0], tx[1]) for tx in txs])


def main():

    argument_spec = dict(
        cardano_node_socket=dict(type='str', required=True),
        cardano_bin_path=dict(type='path', default='~/bin'),
        lovelace=dict(type='int', required=True),
        address=dict(type='str', default=True),
        max_tx_count=dict(type='int', required=True),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str')
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_node_socket = module.params['cardano_node_socket']
    cardano_bin_path = module.params['cardano_bin_path']
    lovelace = module.params['lovelace']
    payment_address = module.params['address']
    max_tx_count = module.params['max_tx_count']
    active_network = module.params['active_network']
    testnet_magic = module.params['testnet_magic']

    utxo_query_command = create_utxo_query_command(cardano_node_socket,
                                                   active_network,
                                                   testnet_magic,
                                                   cardano_bin_path,
                                                   payment_address)

    code, utxo_response, stderr = module.run_command(utxo_query_command,
                                                     use_unsafe_shell=True)

    if code != 0 or stderr != "":
        module.fail_json(msg="Error querying utxo. Make sure the node is fully synced.",
                         code=code,
                         stderr=stderr,
                         command=utxo_query_command)
    assert code == 0
    assert stderr == ""

    txs, txs_lovelace = largest_first(utxo_response, lovelace, max_tx_count)

    if len(txs) == 0:
        module.fail_json(msg="Unable to collect enough Lovelace from the transactions.")

    module.exit_json(changed=False,
                     cli_formatted=format_cli(txs),
                     txs_lovelace=txs_lovelace,
                     txs_used=len(txs))

if __name__ == '__main__':
    main()
