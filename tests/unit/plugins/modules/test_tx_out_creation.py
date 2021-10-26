import pytest

from library.cardano_tx_out import (
    tx_out,
    format_cli
)


def test_creating_tx_out():
    utxo1 = '''
                               TxHash                                 TxIx        Amount
    --------------------------------------------------------------------------------------
    a     0        2 lovelace + 11 x.SecondTesttoken + 101 y.Testtoken
    b     1        10 lovelace + 12 x.SecondTesttoken + 102 y.Testtoken
    c     0        100 lovelace + 13 x.SecondTesttoken + 103 y.Testtoken
        '''

    # test burning token fully
    res = tx_out(utxo1, 'x.SecondTesttoken', 0)
    assert len(res) == 2

    assert res[0] == ('')
    assert res[1] == ('b#1')
    assert res[2] == ('a#0')

    # see if we detect there isn't enough lovelace
    res2, lovelace = largest_first(utxo1, 'lovelace', 1000, 3)
    assert res2 == []
    assert lovelace == 112

    # see if we are ordering from having most lovelace, descending
    res3, lovelace = largest_first(utxo1, 'lovelace', 11, 3)
    assert len(res3) == 1
    assert lovelace == 100
    assert res3[0] == ('c#0')

    # see if we respect the max transaction count
    res4, lovelace = largest_first(utxo1, 'lovelace', 101, 1)
    assert len(res4) == 0
    assert lovelace == 100

    # see if we respect no tx limit
    res5, lovelace = largest_first(utxo1, 'lovelace', 111, 0)
    assert len(res) == 3
    assert lovelace == 112
    assert res[0] == ('c#0')
    assert res[1] == ('b#1')
    assert res[2] == ('a#0')

    # see if we respect no amount limit, aka take all transactions
    res6, lovelace = largest_first(utxo1, 'lovelace', 0, 0)
    assert len(res) == 3
    assert lovelace == 112
    assert res[0] == ('c#0')
    assert res[1] == ('b#1')
    assert res[2] == ('a#0')


def test_fetching_tx_using_custom_tokens():
    utxo1 = '''
                               TxHash                                 TxIx        Amount
    --------------------------------------------------------------------------------------
    a     0        2 lovelace + 11 x.SecondTesttoken + 101 y.Testtoken
    b     1        10 lovelace + 102 y.Testtoken
    c     0        100 lovelace + 211 x.SecondTesttoken + 103 y.Testtoken
        '''

    # a happy path
    res, amount = largest_first(utxo1, 'x.SecondTesttoken', 111, 3)
    assert len(res) == 1
    assert amount == 211
    assert res[0] == ('c#0')

    # multiple txs
    res, amount = largest_first(utxo1, 'x.SecondTesttoken', 222, 3)
    assert len(res) == 2
    assert amount == 222
    assert res[0] == ('c#0')
    assert res[1] == ('a#0')


def test_cli_formatting():
    txs = [('a#0'), ('b#2')]
    formatted = format_cli(txs)

    assert formatted == "--tx-in a#0 --tx-in b#2"