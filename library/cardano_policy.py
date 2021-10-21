from ansible.module_utils.basic import AnsibleModule

import os
import json


class PolicyException(Exception):
    pass

class BrokenPolicyError(PolicyException):
    pass

class IncorrectPolicyNameError(PolicyException):
    pass

def sanitize_wallets(wallets_raw):
    sanitied_wallets = [wallet.strip() for wallet in wallets_raw]


def is_policy_broken(policy_files):
    return (os.path.exists(policy_files['vkey']) and \
        not os.path.exists(policy_files['skey'])) or \
        (not os.path.exists(policy_files['vkey']) and \
        os.path.exists(policy_files['skey']))


def is_policy_installed(wallet_files):
    return os.path.exists(wallet_files['vkey']) and \
        os.path.exists(wallet_files['skey'])


def build_policy_paths(policies_path, policy_name, vkey_file,
                       skey_file, script_file, id_file):
    policy_name = str(policy_name).strip()

    if policy_name == "":
        raise IncorrectPolicyNameError(
            "The wallet name is incorrect: '{}'".format(policy_name))

    policy_basepath = "{}/{}".format(policies_path, policy_name)

    return {'basepath': policy_basepath,
            'vkey': "{}/{}".format(policy_basepath,
                                   vkey_file),
            'skey': "{}/{}".format(policy_basepath,
                                   skey_file),
            'script': "{}/{}".format(policy_basepath,
                                     script_file),
            'id': "{}/{}".format(policy_basepath,
                                 id_file),
            'name': policy_name}


def collect_policy(policies_path, policy_name, vkey_file,
                   skey_file, script_file, id_file):

    policy = build_policy_paths(policies_path,
                                policy_name,
                                vkey_file,
                                skey_file,
                                script_file,
                                id_file)

    if is_policy_broken(policy):
        raise BrokenPolicyError("Broken policy found: {}".format(policy['name']))

    # makes it cleaner if we go full LISP here
    existing_policies = [policy for policy in [policy]
                        if is_policy_installed(policy)]
    new_policies = [policy for policy in [policy]
                        if not is_policy_installed(policy)]

    return {'existing': existing_policies,
            'new': new_policies,
            'all': [policy]}


def build_policy_keys_cmds(cardano_bin_path, policy):

    vkey_file = policy['vkey']
    skey_file = policy['skey']
    policy_path = policy['basepath']

    return ["mkdir -p {}".format(policy_path),
            "{0}/cardano-cli address key-gen " 
            "--verification-key-file {1} " 
            "--signing-key-file {2}".format(cardano_bin_path,
                                            vkey_file,
                                            skey_file)]


def build_policy_id_cmds(cardano_bin_path, policy, key_hash):
    script_file = policy['script']
    id_file = policy['id']
    policy_path = policy['basepath']

    policy_data = {
        "keyHash": key_hash,
        "type": "sig"
    }
    policy_data_json = json.dumps(policy_data)

    return ["echo {} > {}".format(policy_data_json, script_file),
            "{0}/cardano-cli transaction policyid "
            "--script-file {1} >> {2}".format(cardano_bin_path,
                                               script_file,
                                               id_file)]

def main():

    argument_spec = dict(
        cardano_bin_path=dict(type='path', default='~/bin'),
        policies_path=dict(type='path', default='~/policies'),
        name=dict(type='str', required=True),
        vkey_file=dict(type='str', default='policy.vkey'),
        skey_file=dict(type='str', default='policy.skey'),
        script_file=dict(type='str', default='policy.script'),
        id_file=dict(type='str', default='policyID'),
        state=dict(type='str', default='present', choices=['present']))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_bin_path = module.params['cardano_bin_path']
    policies_path = module.params['policies_path']
    policy_name = module.params['name']
    vkey_file = module.params['vkey_file']
    skey_file = module.params['skey_file']
    script_file = module.params['script_file'],
    id_file = module.params['id_file'],
    state = module.params['state']

    try:
        policy_info = collect_policy(policies_path=policies_path,
                                     policy_name=policy_name,
                                     vkey_file=vkey_file,
                                     skey_file=skey_file,
                                     script_file=script_file,
                                     id_file=id_file)
    except BrokenWalletsError as wallets_error:
        module.fail_json(msg=wallets_error)

    existing_wallets = wallets_info['existing']
    new_wallets = wallets_info['new']
    all_wallets = wallets_info['all']
    wallets_by_name = {wallet['name']: wallet for wallet in all_wallets}

    # we don't really handle removal of wallets
    if not module.params['name']:
        module.exit_json(changed=False, wallets=wallets_by_name)

    if state == "present":
        if module.check_mode:
            module.exit_json(changed=bool(len(new_wallets)))
        changed = False
        if len(new_wallets):
            wallets_cmds = [build_wallet_cmds(active_network,
                                             testnet_magic,
                                             cardano_bin_path,
                                             wallet)
                            for wallet in new_wallets]

            [module.run_command(cmd, check_rc=True)
             for wallet_cmds in wallets_cmds
             for cmd in wallet_cmds]
            changed = True
            # module.exit_json(wallets=wallets_cmds)

    module.exit_json(changed=changed, wallets=wallets_by_name)


if __name__ == '__main__':
    main()