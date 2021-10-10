from ansible.module_utils.basic import AnsibleModule

import os

class BrokenWalletsError(Exception):
    pass

def sanitize_wallets(wallets_raw):
    sanitied_wallets = [wallet.strip() for wallet in wallets_raw]

def is_wallet_broken(wallet_files):
    return os.path.exists(wallet_files['addr']) and not \
        (os.path.exists(wallet_files['vkey']) and \
        os.path.exists(wallet_files['skey']))

def is_wallet_installed(wallet_files):
    return os.path.exists(wallet_files['addr']) and \
        os.path.exists(wallet_files['vkey']) and \
        os.path.exists(wallet_files['skey'])


def build_wallet_paths(wallets_path, wallet_name, vkey_file, skey_file, addr_file):
    return {'addr': "{}/{}/{}".format(wallets_path,
                                      wallet_name,
                                      addr_file),
            'vkey': "{}/{}/{}".format(wallets_path,
                                      wallet_name,
                                      vkey_file),
            'skey': "{}/{}/{}".format(wallets_path,
                                      wallet_name,
                                      skey_file),
            'name': wallet_name}
def collect_wallets(wallets_path, wallet_names, vkey_file, skey_file, addr_file):

    wallets_library = [build_wallet_paths(wallets_path,
                                          wallet_name,
                                          vkey_file,
                                          skey_file,
                                          addr_file)
                       for wallet_name
                       in wallet_names]

    broken_wallets = [wallet for wallet in wallets_library
                        if is_wallet_broken(wallet)]

    if len(broken_wallets):
        raise BrokenWalletsError("Broken wallet(s) found: \n {}".format(
            " | ".join([broken_wallet['name'] for broken_wallet in broken_wallets])))

    existing_wallets = [wallet for wallet in wallets_library
                        if is_wallet_installed(wallet)]
    new_wallets = [wallet for wallet in wallets_library
                        if not is_wallet_installed(wallet)]

    return {'existing': existing_wallets,
            'new': new_wallets}

"""
return commands needed to create a wallet
"""
def build_wallet_cmds(active_network, testnet_magic, cardano_bin_path, wallet):
    vkey_file = wallet['vkey']
    skey_file = wallet['skey']
    addr_file = wallet['addr']
    name = wallet['name']

    wallet_creation_cmds = []

    wallet_creation_cmds.append("mkdir -p {}".format(os.path.dirname(vkey_file)))

    wallet_creation_cmds.append("{0}/cardano-cli address key-gen " \
                     "--verification-key-file {1} " \
                     "--signing-key-file {2}".format(cardano_bin_path,
                                                         vkey_file,
                                                         skey_file))
    if active_network == "test":
        wallet_creation_cmds.append("{0}/cardano-cli address build "
                               "--payment-verification-key-file {1} "
                               "--out-file {2} "
                               "--testnet-magic {3}".format(cardano_bin_path,
                                                            vkey_file,
                                                            addr_file,
                                                            testnet_magic))
    elif active_network == "main":
        wallet_creation_cmds.append("{0}/cardano-cli address build "
                               "--payment-verification-key-file {1} "
                               "--out-file {2} "
                               "--mainnet".format(cardano_bin_path,
                                                  vkey_file,
                                                  addr_file))
    return wallet_creation_cmds


def main():

    argument_spec = dict(
        cardano_bin_path=dict(type='path',
                           default='~/bin'),
        wallets_path=dict(type='path',
                           default='~/wallets'),
        name=dict(type='list', required=True),
        vkey_file=dict(type='str', default='payment.vkey'),
        skey_file=dict(type='str', default='payment.skey'),
        addr_file=dict(type='str', default='payment.addr'),
        state=dict(type='str', default='present', choices=['present']),
        active_network=dict(type='str', default='test',
                            choices=['test', 'main']),
        testnet_magic=dict(type='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    state = module.params['state']

    active_network = module.params['active_network']
    testnet_magic = module.params['testnet_magic']
    wallets_path = module.params['wallets_path']
    wallet_names = module.params['name']
    vkey_file = module.params['vkey_file']
    skey_file = module.params['skey_file']
    addr_file = module.params['addr_file']
    cardano_bin_path = module.params['cardano_bin_path']

    try:
        wallets_info = collect_wallets(wallets_path=wallets_path,
                                       wallet_names=wallet_names,
                                       vkey_file=vkey_file,
                                       skey_file=skey_file,
                                       addr_file=addr_file)
    except BrokenWalletsError as wallets_error:
        module.fail_json(msg=wallets_error)

    existing_wallets = wallets_info['existing']
    new_wallets = wallets_info['new']

    # we don't really handle removal of wallets
    if not module.params['name']:
        module.exit_json(changed=False, wallets=existing_wallets)

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

    module.exit_json(changed=changed, wallets=wallet_names)

if __name__ == '__main__':
    main()