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


def create_utxo_struct(raw_utxo_table, token):
    rows_tokens = [{'tx': "#".join(row.split()[0:2]),
                    'tokens': dict(zip(row.split()[3:][0::3], row.split()[2:][0::3]))}
                   for row
                   in raw_utxo_table.strip().splitlines()[2:]
                   if token in row.split()[3:][0::3]]
    rows_by_tx = {"#".join(row.split()[0:2]): {'tx': "#".join(row.split()[0:2]),
                                               'tokens': dict(zip(row.split()[3:][0::3], row.split()[2:][0::3]))}
                  for row
                  in raw_utxo_table.strip().splitlines()[2:]
                  if token in row.split()[3:][0::3]}
    return sorted(rows_tokens, key=lambda x: int(x['tokens'][token]), reverse=True), rows_by_tx

def tx_in(raw_utxo_table, token, wanted_amount, max_tx):
    sorted_token_txs, rows_by_tx = create_utxo_struct(raw_utxo_table, token)

    accumulated_amount = 0
    accumulated_lovelace = 0
    txs = []
    for row in sorted_token_txs:
        if (accumulated_amount < wanted_amount or wanted_amount == 0) \
                and (len(txs) < max_tx or not max_tx):

            accumulated_amount += int(row['tokens'][token])
            accumulated_lovelace += int(row['tokens']['lovelace'])  # some lovelace will always be there
            txs.append(row['tx'])
        else:
            break

    if accumulated_amount < wanted_amount:
        return [], accumulated_amount, accumulated_lovelace

    return txs, accumulated_amount, accumulated_lovelace

def tx_out(raw_utxo_table, custom_token, token_new_amount, txs_in):

    # not very elegant, but let's just dumbly skip lovelace to solve an immediate problem
    skip_token = 'lovelace'

    sorted_token_txs, rows_by_tx = create_utxo_struct(raw_utxo_table, custom_token)

    tx_out = {}
    for row in txs_in:
        tokens = rows_by_tx[row]['tokens']
        for token in tokens:
            if token != skip_token:
                if not token in tx_out:
                    tx_out[token] = 0
                tx_out[token] += int(tokens[token])

    # set the correct amount for the selected token
    if custom_token != skip_token:
        tx_out[custom_token] = token_new_amount

    return tx_out

def format_cli_in(txs):
    return " ".join(["--tx-in {}".format(tx) for tx in txs])

def format_cli_out(txs_out):
    return " + ".join(["{} {}".format(txs_out[tx], tx)
                       for tx in txs_out
                       if txs_out[tx] > 0])

def main():

    argument_spec = dict(
        cardano_node_socket=dict(type='str', required=True),
        cardano_bin_path=dict(type='path', default='~/bin'),
        lovelace_amount=dict(type='int', required=True),
        token_amount=dict(type='int', required=True),
        out_amount=dict(type='int', required=True),
        token=dict(type='str', default='lovelace'),
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
    lovelace_amount = module.params['lovelace_amount']
    token_amount = module.params['token_amount']
    out_amount = module.params['out_amount']
    token = module.params['token']
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

    txs_in, txs_amount, lovelace_available = tx_in(utxo_response, token, token_amount, max_tx_count)

    if lovelace_available < lovelace_amount:
        module.fail_json(msg="Unable to collect enough amount of lovelace from transactions.")

    txs_out = tx_out(utxo_response, token, out_amount, txs_in)

    if len(txs_in) == 0:
        module.fail_json(msg="Unable to collect enough amount of tokens from transactions.")

    module.exit_json(changed=False,
                     tx_in_formatted=format_cli_in(txs_in),
                     tx_out_formatted=format_cli_out(txs_out),
                     lovelace_available=lovelace_available,
                     txs_token_available=txs_amount,
                     txs_in_used=len(txs_in),
                     txs_in=txs_in,
                     txs_out=txs_out)


if __name__ == '__main__':
    main()
