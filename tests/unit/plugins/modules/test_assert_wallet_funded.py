import pytest

from library.assert_address_funded import (
    get_lovelace_from_utxo,
    create_utxo_command
)


def test_creating_utxo_command():
    cmd = create_utxo_command("cardano_node_socket",
                              "test",
                              "testnet_magic",
                              "bin_path",
                              "addr")
    print(cmd)
    assert cmd == "CARDANO_NODE_SOCKET_PATH=cardano_node_socket bin_path/cardano-cli query utxo " \
                  "--testnet-magic testnet_magic --address addr"


def test_calculating_funds_from_utxo():

    lovelace = 1234567

    sample_response = '''
                               TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
21a4641241ff937c8bbb14bc4493089c9a9fe1b759195e07d66e506106b76adf     0        %d lovelace + TxOutDatumNone
    ''' % lovelace

    address_lovelace = get_lovelace_from_utxo(sample_response)

    assert address_lovelace == lovelace

    sample_response2 = ''''''

    address_lovelace2 = get_lovelace_from_utxo(sample_response2)

    assert address_lovelace2 == 0

    sample_response3 = '''
                               TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
    '''

    address_lovelace3 = get_lovelace_from_utxo(sample_response3)

    assert address_lovelace3 == 0

    sample_response4 = '''
                           TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
21a4641241ff937c8bbb14bc4493089c9a9fe1b759195e07d66e506106b76adf     0        1000000000 lovelace + TxOutDatumNone
da7bcb251f3a90e74d8d661a55d2e8951f92932d9cdea0172ed70e8f2be47a5e     0        1000000000 lovelace + TxOutDatumNone

    '''

    address_lovelace4 = get_lovelace_from_utxo(sample_response4)

    assert address_lovelace4 == 2000000000
