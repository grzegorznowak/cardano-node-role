import pytest
from itertools import takewhile
from time import sleep


from action_plugins.tx_submit_until_success import (
    _run
)

def stub_failing_exec(module_name, module_args, task_vars, tmp):
    return {}


def stub_success_exec(module_name, module_args, task_vars, tmp):
    return {'tokens': {'token_name': 100}}


def stub_failing_exec_with_sleep(module_name, module_args, task_vars, tmp):
    sleep(0.01)
    return stub_failing_exec(module_name, module_args, task_vars, tmp)

def stub_success_exec_with_sleep(module_name, module_args, task_vars, tmp):
    sleep(0.01)
    return stub_success_exec(module_name, module_args, task_vars, tmp)

def test_retrying_submit():
    max_retries = 3

    module_args = {}
    module_args['cardano_bin_path'] = 'bin'
    module_args['signed_tx'] = 'signed.txt'
    module_args['network_param'] = 'network 123'
    module_args['cardano_node_socket'] = 'node.socket'
    module_args['active_network'] = 'network'
    module_args['testnet_magic'] = 'magic'
    module_args['address'] = 'address'
    module_args['quantity'] = '100'
    module_args['token_name'] = 'token_name'

    res1 = _run(stub_failing_exec_with_sleep,
                module_args,
                task_vars=None,
                tmp=None,
                sleep_time=0.01,
                max_slot_check_retry=3)

    res2 = _run(stub_success_exec_with_sleep,
                module_args,
                task_vars=None,
                tmp=None,
                sleep_time=0.01,
                max_slot_check_retry=3)
