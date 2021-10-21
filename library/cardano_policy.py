from ansible.module_utils.basic import AnsibleModule

import os


class BrokenPolicyError(Exception):
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


def build_policy_paths(policies_path, policy_name, vkey_file, skey_file):
    return {'vkey': "{}/{}/{}".format(policies_path,
                                      policy_name,
                                      vkey_file),
            'skey': "{}/{}/{}".format(policies_path,
                                      policy_name,
                                      skey_file),
            'name': policy_name}


def collect_policy(policies_path, policy_name, vkey_file, skey_file):

    policy = build_policy_paths(policies_path,
                                policy_name,
                                vkey_file,
                                skey_file)

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


"""
return commands needed to create a wallet
"""
def build_policy_keys_cmds(cardano_bin_path, policy):

    vkey_file = policy['vkey']
    skey_file = policy['skey']
    policy_path = os.path.dirname(vkey_file)
    name = policy['name']

    cmds = []

    cmds.append("mkdir -p {}".format(policy_path))
    cmds.append("{0}/cardano-cli address key-gen " \
                                "--verification-key-file {1} " \
                                "--signing-key-file {2}".format(cardano_bin_path,
                                                                vkey_file,
                                                                skey_file))

    return cmds

def build_policy_id_cmds(cardano_bin_path, policy, key_hash):
    vkey_file = policy['vkey']
    policy_path = os.path.dirname(vkey_file)

    policy_data = {
        "keyHash": key_hash,
        "type": "sig"
    }

    "cardano-cli transaction policyid --script-file ./policy/policy.script >> policy/policyID"

def main():

    argument_spec = dict(
        cardano_bin_path=dict(type='path', default='~/bin'),
        policies_path=dict(type='path', default='~/policies'),
        name=dict(type='str', required=True),
        vkey_file=dict(type='str', default='policy.vkey'),
        skey_file=dict(type='str', default='policy.skey'),
        state=dict(type='str', default='present', choices=['present']))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_bin_path = module.params['cardano_bin_path']
    policies_path = module.params['policies_path']
    policy_name = module.params['name']
    vkey_file = module.params['vkey_file']
    skey_file = module.params['skey_file']
    state = module.params['state']

    try:
        policy_info = collect_policy(policies_path=policies_path,
                                     policy_name=policy_name,
                                     vkey_file=vkey_file,
                                     skey_file=skey_file)
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