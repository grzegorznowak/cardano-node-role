import pytest

from library.cardano_policy import (
    collect_policy,
    BrokenPolicyError
)

VKEY_FILE = "vkey"
SKEY_FILE = "skey"

def test_collecting_policies(tmp_path):
    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE)

    assert len(policy_info['existing']) == 0
    assert len(policy_info['new']) == 0

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE)

    assert len(policy_info['existing']) == 0
    assert len(policy_info['new']) == 1

    d = tmp_path / "policy1"
    d.mkdir()
    vkey = d / VKEY_FILE
    skey = d / SKEY_FILE
    vkey.touch()
    skey.touch()

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE)

    assert len(policy_info['existing']) == 1
    assert len(policy_info['new']) == 0

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy2",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE)

    assert len(policy_info['existing']) == 0
    assert len(policy_info['new']) == 1


def test_detecting_broken_policy(tmp_path):

    # Should raise error when skey is not present
    d = tmp_path / "policy1"
    d.mkdir()
    vkey = d / VKEY_FILE
    vkey.touch()

    with pytest.raises(BrokenPolicyError):
        _ = collect_policy(policies_path=tmp_path,
                           policy_name="policy1",
                           vkey_file=VKEY_FILE,
                           skey_file=SKEY_FILE)

    # Should raise error when vkey not present
    d = tmp_path / "policy2"
    d.mkdir()
    addr = d / SKEY_FILE
    addr.touch()

    with pytest.raises(BrokenWalletsError):
        _ = collect_policy(policies_path=tmp_path,
                           policy_name="policy2",
                           vkey_file=VKEY_FILE,
                           skey_file=SKEY_FILE)


def test_policy_creation_cmds(tmp_path):
    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE)
    new_policies = policy_info['new']

    policies_cmds = [build_policy_keys_cmds(cardano_bin_path="dummy_path",
                                            policy=policy)
                     for policy in new_policies]

    print(policies_cmds)
    assert len(policies_cmds) == 1
    assert len(policies_cmds[0]) == 2

    assert policies_cmds[0][0] == "mkdir -p {}/policy1".format(str(tmp_path))

    assert policies_cmds[0][1] == "dummy_path/cardano-cli address key-gen " \
                                "--verification-key-file {0}/policy1/vkey " \
                                "--signing-key-file {0}/policy1/skey".format(str(tmp_path))

    policy_id_cmds = build_policy_id_cmds()


def test_mainnet_wallet_cmds(tmp_path):
    wallets_info = collect_wallets(wallets_path=tmp_path,
                                  wallet_names=["wallet1"],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)
    new_wallets = wallets_info['new']

    wallet_cmds = [build_wallet_cmds(active_network="main",
                                     testnet_magic="",
                                     cardano_bin_path="dummy_path",
                                     wallet=wallet)
                   for wallet in new_wallets]

    assert len(wallet_cmds) == 1
    assert len(wallet_cmds[0]) == 3  # one for keys one for address
    assert wallet_cmds[0][2] == "dummy_path/cardano-cli address build " \
                                "--payment-verification-key-file {0}/wallet1/vkey " \
                                "--out-file {0}/wallet1/addr " \
                                "--mainnet".format(str(tmp_path))
