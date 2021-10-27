import pytest

from library.cardano_policy import (
    collect_policy,
    build_policy_id_cmds,
    build_policy_keys_cmds,
    BrokenPolicyError,
    IncorrectPolicyNameError
)

VKEY_FILE = "vkey"
SKEY_FILE = "skey"
SCRIPT_FILE = "script"
ID_FILE = "policyID"


def test_policy_keys_creation_cmds(tmp_path):
    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE,
                                 script_file=SCRIPT_FILE,
                                 id_file=ID_FILE)
    new_policies = policy_info['new']

    policy_keys_cmds = [build_policy_keys_cmds(cardano_bin_path="dummy_path",
                                               policy=policy)
                        for policy in new_policies]

    assert len(policy_keys_cmds) == 1
    assert len(policy_keys_cmds[0]) == 2
    assert policy_keys_cmds[0][1] == "dummy_path/cardano-cli address key-gen " \
                                     "--verification-key-file {0}/policy1/vkey " \
                                     "--signing-key-file {0}/policy1/skey".format(str(tmp_path))


def test_tokens_policy_id_creation_cmds(tmp_path):
    key_hash = "key_hash"

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE,
                                 script_file=SCRIPT_FILE,
                                 id_file=ID_FILE)
    new_policies = policy_info['new']

    policy_id_cmds = [build_policy_id_cmds(cardano_bin_path="dummy_path",
                                           policy=policy,
                                           key_hash=key_hash,
                                           type='token')
                      for policy in new_policies]

    assert len(policy_id_cmds) == 1
    assert len(policy_id_cmds[0]) == 2

    assert policy_id_cmds[0][0] == "echo '{{\"keyHash\": \"{0}\", \"type\": \"sig\"}}' > " \
                                   "{1}/policy1/script".format(key_hash, str(tmp_path))


def test_nfts_policy_id_creation_cmds(tmp_path):
    key_hash = "key_hash"

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE,
                                 script_file=SCRIPT_FILE,
                                 id_file=ID_FILE)
    new_policies = policy_info['new']

    policy_id_cmds = [build_policy_id_cmds(cardano_bin_path="dummy_path",
                                           policy=policy,
                                           key_hash=key_hash,
                                           type='nft')
                      for policy in new_policies]

    assert len(policy_id_cmds) == 1
    assert len(policy_id_cmds[0]) == 2
    assert policy_id_cmds[0][0] == "echo '{{\"type\": \"all\", \"scripts\": [{{\"slot\": 0, " \
"\"type\": \"before\"}}, {{\"keyHash\": \"{0}\", \"type\": \"sig\"}}]}}\' " \
"> {1}/policy1/script".format(key_hash, str(tmp_path))


def test_collecting_policies(tmp_path):

    with pytest.raises(IncorrectPolicyNameError):
        _ = collect_policy(policies_path=tmp_path,
                                     policy_name=" ",
                                     vkey_file=VKEY_FILE,
                                     skey_file=SKEY_FILE,
                                     script_file=SCRIPT_FILE,
                                     id_file=ID_FILE)

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy1",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE,
                                 script_file=SCRIPT_FILE,
                                 id_file=ID_FILE)

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
                                 skey_file=SKEY_FILE,
                                 script_file=SCRIPT_FILE,
                                 id_file=ID_FILE)

    assert len(policy_info['existing']) == 1
    assert len(policy_info['new']) == 0

    policy_info = collect_policy(policies_path=tmp_path,
                                 policy_name="policy2",
                                 vkey_file=VKEY_FILE,
                                 skey_file=SKEY_FILE,
                                 script_file=SCRIPT_FILE,
                                 id_file=ID_FILE)

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
                           skey_file=SKEY_FILE,
                           script_file=SCRIPT_FILE,
                           id_file=ID_FILE)

    # Should raise error when vkey not present
    d = tmp_path / "policy2"
    d.mkdir()
    addr = d / SKEY_FILE
    addr.touch()

    with pytest.raises(BrokenPolicyError):
        _ = collect_policy(policies_path=tmp_path,
                           policy_name="policy2",
                           vkey_file=VKEY_FILE,
                           skey_file=SKEY_FILE,
                           script_file=SCRIPT_FILE,
                           id_file=ID_FILE)
