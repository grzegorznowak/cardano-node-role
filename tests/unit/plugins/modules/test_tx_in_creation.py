import pytest

from library.cardano_tx_in import (
    largest_first,
    format_cli
)


def test_tx_calcs():
    utxo1 = '''
                               TxHash                                 TxIx        Amount
    --------------------------------------------------------------------------------------
    a     0        2 lovelace + 11 x.SecondTesttoken + 101 y.Testtoken
    b     1        10 lovelace + 12 x.SecondTesttoken + 102 y.Testtoken
    c     0        100 lovelace + 13 x.SecondTesttoken + 103 y.Testtoken
        '''

    res, lovelace = largest_first(utxo1, 111, 3)
    assert len(res) == 3
    assert lovelace == 112
    assert res[0] == ('c','0')
    assert res[1] == ('b','1')
    assert res[2] == ('a','0')

    res2, lovelace = largest_first(utxo1, 1000, 3)
    assert res2 == []
    assert lovelace == 112

    res3, lovelace = largest_first(utxo1, 11, 3)
    assert len(res3) == 1
    assert lovelace == 100
    assert res3[0] == ('c','0')

def test_cli_formatting():
    txs = [('a', '0'), ('b', '2')]
    formatted = format_cli(txs)

    assert formatted == "--tx-in a#0 --tx-in b#2"