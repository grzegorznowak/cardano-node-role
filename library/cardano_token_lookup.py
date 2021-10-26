from ansible.module_utils.basic import AnsibleModule
from functools import reduce
from collections import Counter
import operator

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


def tokens_from_utxo(raw_utxo_table):

    rows_tokens = [zip(row.split()[2:][1::3], row.split()[2:][0::3])
                   for row
                   in raw_utxo_table.strip().splitlines()[2:]]

    all_tokens = [{tokens[0]: int(tokens[1])}
           for row_tokens in rows_tokens
           for tokens in row_tokens]

    return dict(reduce(operator.add,
                       map(Counter, all_tokens)))


def main():

    argument_spec = dict(
        cardano_node_socket=dict(type='str', required=True),
        cardano_bin_path=dict(type='path', default='~/bin'),
        address=dict(type='str', default=True),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str')
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_node_socket = module.params['cardano_node_socket']
    cardano_bin_path = module.params['cardano_bin_path']
    payment_address = module.params['address']
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

    tokens = tokens_from_utxo(utxo_response)

    module.exit_json(changed=False,
                     tokens=tokens,
                     code=code)


if __name__ == '__main__':
    main()
