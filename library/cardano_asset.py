from ansible.module_utils.basic import AnsibleModule

import os

"""
testnet="testnet-magic 1097911063"
tokenname1="Testtoken"
tokenname2="SecondTesttoken"
tokenamount="10000000"
output="0"
fee="300000"
txhash="insert your txhash here"
txix="insert your TxIx here"
funds="insert Amount here"
policyid=$(cat policy/policyID)

cardano-cli transaction build-raw \
 --fee $fee \
 --tx-in $txhash#$txix \
 --tx-out $address+$output+"$tokenamount $policyid.$tokenname1 + $tokenamount $policyid.$tokenname2" \
 --mint="$tokenamount $policyid.$tokenname1 + $tokenamount $policyid.$tokenname2" \
 --minting-script-file policy/policy.script \
 --out-file matx.raw
"""

def build_raw_cmd(cardano_bin_path, name, tx_hash, txix, address,
                  quantity, policyid, policy_script):
    fee=300000
    cmd = """
    {bin_path}/cardano-cli transaction build-raw 
    --fee {fee} 
    --tx-in {tx_hash}#{txix} 
    --tx-out {address}+{output}+"{quantity} {policyid}.{name}" 
    --mint="{quantity} {policyid}.{name}" 
    --minting-script-file {policy_script} 
    --out-file {asset_path}
    """.format(bin_path=cardano_bin_path,
               tx_hash=tx_hash, txix=txix, fee=fee,
               address=address, output=0,
               quantity=quantity, policyid=policyid,
               name=name, policy_script=policy_script,
               asset_path=asset_path)

def main():

    argument_spec = dict(
        cardano_bin_path=dict(type='path', default='~/bin'),
        name=dict(type='str', required=True),
        quantity=dict(type='int', required=True),
        policies_path=dict(type='path', default='~/policies'),
        policy_name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present']))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    cardano_bin_path = module.params['cardano_bin_path']
    policies_path = module.params['policies_path']
    policy_name = module.params['name']
    asset_name = module.params['asset_name']
    quantity = module.params['quantity']
    state = module.params['state']


    # we don't really handle removal of policies
    if not module.params['name']:
        module.exit_json(changed=False, assets=[])

    if state == "present":
        if module.check_mode:
            module.exit_json(changed=bool(len(new_assets)))
        changed = False
        if len(new_assets):
            tx_hash, txix = get_
            raw_cmd = build_raw_cmd(cardano_bin_path, name, tx_hash, txix, address,
                                    quantity, policyid, policy_script):
            [create_policy_keys(cardano_bin_path,
                                policy, module)
             for policy in new_policies]

            [create_policy_id(cardano_bin_path,
                              policy, module)
             for policy in new_policies]

            changed = True
            # module.exit_json(wallets=wallets_cmds)

    module.exit_json(changed=changed, policies=policies_by_name)


if __name__ == '__main__':
    main()