#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible

from ansible.plugins.action import ActionBase
from itertools import takewhile
from time import sleep

# def exec_module_with_sleep():

def token_lookup(exec_fn, module_args, task_vars, tmp):
    token_result = exec_fn(
        module_name='cardano_token_lookup',
        module_args={
            'cardano_node_socket': module_args['cardano_node_socket'],
            'cardano_bin_path': module_args['cardano_bin_path'],
            'active_network': module_args['active_network'],
            'testnet_magic': module_args['testnet_magic'],
            'address': module_args['address']
        },
        task_vars=task_vars, tmp=tmp)
    return token_result


# delay return if we're not successfull
def is_token_found_with_sleep(lookup_result, token_name, quantity, sleep_time):
    res = 'tokens' in lookup_result \
    and token_name in lookup_result['tokens'] \
    and int(lookup_result['tokens'][token_name]) >= int(quantity)

    if res:
        return True
    else:
        sleep(sleep_time)
        return False


def submit_try(exec_fn, module_args, task_vars, tmp):

    submit_result = exec_fn(
        module_name='ansible.builtin.command',
        module_args={
            '_raw_params': "{0}/cardano-cli transaction submit "
                           "--tx-file {1} "
                           "--{2}".format(module_args['cardano_bin_path'],
                                          module_args['signed_tx'],
                                          module_args['network_param'])
        },
        task_vars=task_vars, tmp=tmp)

    return submit_result

def _run(exec_fn, module_args, task_vars, tmp, sleep_time, max_slot_check_retry):
    token_name = module_args['token_name']
    quantity = module_args['quantity']

    submit_result = submit_try(exec_fn,
                               module_args,
                               task_vars,
                               tmp)

    # wait for utxo to get updated
    list(takewhile(
        lambda _: not is_token_found_with_sleep(token_lookup(exec_fn,
                                                             module_args,
                                                             task_vars=task_vars,
                                                             tmp=tmp),
                                                token_name,
                                                quantity,
                                                sleep_time=sleep_time),
        range(max_slot_check_retry)))

    # get the latest utxo state
    lookup_result = token_lookup(exec_fn,
                                 module_args,
                                 task_vars=task_vars,
                                 tmp=tmp)

    return dict(submit_result=submit_result,
                lookup_result=lookup_result,)

class ActionModule(ActionBase):


    def run(self, tmp=None, task_vars=None):
        max_slot_check_retry = 6  # wait 1 minute for the new tx to be visible on the blockchain
        sleep_time=10
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        return _run(self._execute_module,
                    module_args,
                    task_vars,
                    tmp,
                    sleep_time,
                    max_slot_check_retry)

