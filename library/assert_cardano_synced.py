from ansible.module_utils.basic import AnsibleModule

import os
import json


def query_tip_cmd(cardano_node_socket, active_network, testnet_magic, cardano_bin_path):

    raw_utxo_table = None
    command = ""
    if active_network == 'test':
        command = "CARDANO_NODE_SOCKET_PATH={0} " \
                  "{1}/cardano-cli query tip " \
                  "--testnet-magic {2} ".format(cardano_node_socket,
                                                cardano_bin_path,
                                                testnet_magic)
    elif active_network == 'main':
        command = "CARDANO_NODE_SOCKET_PATH={0} " \
                  "{1}/cardano-cli query tip --mainnet".format(cardano_node_socket,
                                                               cardano_bin_path)

    return command


def get_progress_from_response(raw_response):
    return float(json.loads(raw_response)['syncProgress'])


def main():

    argument_spec = dict(
        cardano_node_socket=dict(type='str', required=True),
        wanted_progress=dict(type='float', default='100'),
        cardano_bin_path=dict(type='path', default='~/bin'),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_node_socket = module.params['cardano_node_socket']
    active_network = module.params['active_network']
    wanted_progress = module.params['wanted_progress']
    testnet_magic = module.params['testnet_magic']
    cardano_bin_path = module.params['cardano_bin_path']

    tip_cmd = query_tip_cmd(cardano_node_socket,
                            active_network,
                            testnet_magic,
                            cardano_bin_path)

    code, tip_responce, stderr = module.run_command(tip_cmd,
                                                    use_unsafe_shell=True)

    if code != 0 or stderr != "":
        module.fail_json(msg="Error querying the tip",
                         code=code,
                         stderr=stderr,
                         rc=code,
                         progress=0,
                         command=tip_cmd)

    sync_progress = float(get_progress_from_response(tip_responce))

    if sync_progress >= wanted_progress:
        module.exit_json(changed=False,
                         progress=sync_progress,
                         rc=code)
    else:
        module.fail_json(msg="Expected progress not achieved yet",
                         progress=sync_progress,
                         rc=code)


if __name__ == '__main__':
    main()