import pytest

from library.cardano_wallet import (
    collet_wallets,
    BrokenWalletsError,
    build_wallet_cmds
)

VKEY_FILE = "vkey"
SKEY_FILE = "skey"
ADDR_FILE = "addr"
def test_new_wallets(tmp_path):
    wallets_info = collet_wallets(wallets_path=tmp_path,
                                  wallet_names=[],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)

    assert len(wallets_info['existing']) == 0
    assert len(wallets_info['new']) == 0


    wallets_info = collet_wallets(wallets_path=tmp_path,
                                  wallet_names=["wallet1"],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)

    assert len(wallets_info['existing']) == 0
    assert len(wallets_info['new']) == 1

    wallets_info = collet_wallets(wallets_path=tmp_path,
                                  wallet_names=["wallet1", "wallet2"],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)

    assert len(wallets_info['existing']) == 0
    assert len(wallets_info['new']) == 2

def test_existing_wallets(tmp_path):

    d = tmp_path / "wallet1"
    d.mkdir()
    vkey = d / VKEY_FILE
    skey = d / SKEY_FILE
    addr = d / ADDR_FILE
    vkey.touch()
    skey.touch()
    addr.touch()

    wallets_info = collet_wallets(wallets_path=tmp_path,
                                  wallet_names=["wallet1"],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)

    assert len(wallets_info['existing']) == 1
    assert len(wallets_info['new']) == 0

    wallets_info = collet_wallets(wallets_path=tmp_path,
                                  wallet_names=["wallet1", "wallet2"],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)

    assert len(wallets_info['existing']) == 1
    assert len(wallets_info['new']) == 1


def test_broken_wallet(tmp_path):

    # Should raise error when skey is not present
    d = tmp_path / "wallet1"
    d.mkdir()
    vkey = d / VKEY_FILE
    addr = d / ADDR_FILE
    vkey.touch()
    addr.touch()

    with pytest.raises(BrokenWalletsError):
        wallets_info = collet_wallets(wallets_path=tmp_path,
                                      wallet_names=["wallet1"],
                                      vkey_file=VKEY_FILE,
                                      skey_file=SKEY_FILE,
                                      addr_file=ADDR_FILE)

    # Should raise error when vkey and skey are not present
    d = tmp_path / "wallet2"
    d.mkdir()
    addr = d / ADDR_FILE
    addr.touch()

    with pytest.raises(BrokenWalletsError):
        wallets_info = collet_wallets(wallets_path=tmp_path,
                                      wallet_names=["wallet2"],
                                      vkey_file=VKEY_FILE,
                                      skey_file=SKEY_FILE,
                                      addr_file=ADDR_FILE)

    # Should raise error when vkey is not present
    d = tmp_path / "wallet3"
    d.mkdir()
    vkey = d / SKEY_FILE
    addr = d / ADDR_FILE
    vkey.touch()
    addr.touch()

    with pytest.raises(BrokenWalletsError):
        wallets_info = collet_wallets(wallets_path=tmp_path,
                                      wallet_names=["wallet3"],
                                      vkey_file=VKEY_FILE,
                                      skey_file=SKEY_FILE,
                                      addr_file=ADDR_FILE)


def test_testnet_wallet_cmds(tmp_path):
    wallets_info = collet_wallets(wallets_path=tmp_path,
                                  wallet_names=["wallet1"],
                                  vkey_file=VKEY_FILE,
                                  skey_file=SKEY_FILE,
                                  addr_file=ADDR_FILE)
    new_wallets = wallets_info['new']

    wallet_cmds = [build_wallet_cmds(active_network="test",
                                     testnet_magic="123",
                                     cardano_bin_path="dummy_path",
                                     wallet=wallet)
                   for wallet in new_wallets]

    assert len(wallet_cmds) == 1
    assert len(wallet_cmds[0]) == 3  # one for keys one for address

    assert wallet_cmds[0][0] == "mkdir {}/wallet1".format(str(tmp_path))

    assert wallet_cmds[0][1] == "dummy_path/cardano-cli address key-gen " \
                                "--verification-key-file {0}/wallet1/vkey " \
                                "--signing-key-file {0}/wallet1/skey".format(str(tmp_path))

    assert wallet_cmds[0][2] == "dummy_path/cardano-cli address build " \
                                "--payment-verification-key-file {0}/wallet1/vkey " \
                                "--out-file {0}/wallet1/addr " \
                                "--testnet-magic 123".format(str(tmp_path))


def test_mainnet_wallet_cmds(tmp_path):
    wallets_info = collet_wallets(wallets_path=tmp_path,
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


#
# def test_wallet_creation(tmp_path):
#     wallets_info = collet_wallets(wallets_path=tmp_path,
#                                   wallet_names=["wallet1"],
#                                   vkey_file=VKEY_FILE,
#                                   skey_file=SKEY_FILE,
#                                   addr_file=ADDR_FILE)
#     new_wallets = wallets_info['new']
#
#     (wallet_create(new_wallet) for new_wallet in new_wallets)
#
#     d = tmp_path / "wallet1"
#     vkey = d / VKEY_FILE
#     skey = d / SKEY_FILE
#     addr = d / ADDR_FILE
#     assert d.is_dir()
#     assert vkey.is_file()
#     assert vkey.stat().st_size > 0
#
#     assert skey.is_file()
#     assert skey.stat().st_size > 0
#
#     assert addr.is_file()
#     assert addr.stat().st_size > 0
