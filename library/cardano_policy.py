from ansible.module_utils.basic import AnsibleModule

import os
import json


class PolicyException(Exception):
    pass


class BrokenPolicyError(PolicyException):
    pass


class IncorrectPolicyNameError(PolicyException):
    pass


def is_policy_broken(policy):
    return (os.path.exists(policy['vkey']) and
            not os.path.exists(policy['skey'])) or \
           (not os.path.exists(policy['vkey']) and
            os.path.exists(policy['skey']))


def is_policy_installed(policy):
    return os.path.exists(policy['vkey']) and \
        os.path.exists(policy['skey'])


def build_policy_paths(policies_path, policy_name, vkey_file,
                       skey_file, script_file, id_file):
    policy_name = str(policy_name).strip()

    if policy_name == "":
        raise IncorrectPolicyNameError(
            "The policy name is incorrect: '{}'".format(policy_name))

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

    policy_data = {
        "keyHash": key_hash,
        "type": "sig"
    }
    policy_data_json = json.dumps(policy_data)

    return ["echo '{}' > {}".format(policy_data_json, script_file),
            "{0}/cardano-cli transaction policyid "
            "--script-file {1} >> {2}".format(cardano_bin_path,
                                              script_file,
                                              id_file)]


def build_policy_key_hash_cmds(cardano_bin_path, policy):
    vkey_file = policy['vkey']

    return "{}/cardano-cli address key-hash " \
           "--payment-verification-key-file {} | tr -d '\n'".format(cardano_bin_path,
                                                                    vkey_file)


def create_policy_keys(cardano_bin_path, policy, module):
    policy_keys_cmds = build_policy_keys_cmds(cardano_bin_path,
                                              policy)

    results = [module.run_command(cmd, check_rc=True, use_unsafe_shell=True)
               for cmd in policy_keys_cmds]

    def assert_result_ok(result):
        (rc, stdout, stderr) = result
        assert rc == 0
        assert stderr == ""

    [assert_result_ok(result) for result in results]


def create_policy_key_hash(cardano_bin_path, policy, module):

    policy_key_hash_cmds = build_policy_key_hash_cmds(cardano_bin_path, policy)

    rc, policy_key_hash, stderr = module.run_command(policy_key_hash_cmds, check_rc=True, use_unsafe_shell=True)
    assert rc == 0
    assert stderr == ""

    return policy_key_hash


def create_policy_id(cardano_bin_path, policy, module):
    policy_key_hash = create_policy_key_hash(cardano_bin_path, policy, module)

    policy_id_cmds = build_policy_id_cmds(cardano_bin_path,
                                          policy,
                                          policy_key_hash)

    results = [module.run_command(cmd, check_rc=True, use_unsafe_shell=True)
               for cmd in policy_id_cmds]

    def assert_result_ok(result):
        (rc, stdout, stderr) = result
        assert rc == 0
        assert stderr == ""

    [assert_result_ok(result) for result in results]

def materialize_id(policy):
    with open(policy['id'], 'r') as file:
        return file.read().strip()

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
    script_file = module.params['script_file']
    id_file = module.params['id_file']
    state = module.params['state']

    try:
        policy_info = collect_policy(policies_path=policies_path,
                                     policy_name=policy_name,
                                     vkey_file=vkey_file,
                                     skey_file=skey_file,
                                     script_file=script_file,
                                     id_file=id_file)
    except BrokenPolicyError as policy_error:
        module.fail_json(msg=policy_error)

    existing_policies = policy_info['existing']
    new_policies = policy_info['new']
    all_policies = policy_info['all']
    policies_by_name = {policy['name']: policy for policy in all_policies}
    policies_id_by_name = {policy['name']: materialize_id(policy) for policy in existing_policies}
    # we don't really handle removal of policies
    if not module.params['name']:
        module.exit_json(changed=False, policies=policies_by_name)

    if state == "present":
        if module.check_mode:
            module.exit_json(changed=bool(len(new_policies)))
        changed = False
        if len(new_policies):
            [create_policy_keys(cardano_bin_path,
                                policy, module)
             for policy in new_policies]

            [create_policy_id(cardano_bin_path,
                              policy, module)
             for policy in new_policies]

            changed = True

    policies_id_by_name = {policy['name']: materialize_id(policy) for policy in all_policies}

    module.exit_json(changed=changed,
                     policies=policies_by_name,
                     policies_ids=policies_id_by_name)


if __name__ == '__main__':
    main()