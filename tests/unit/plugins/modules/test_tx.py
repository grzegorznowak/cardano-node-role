from library.cardano_tx import (
    tx_in,
    tx_out,
    format_cli_in,
    format_cli_out
)


def test_creating_tx_out():
    utxo1 = '''
                                   TxHash                                 TxIx        Amount
        --------------------------------------------------------------------------------------
        a     0        2 lovelace + 101 y.Testtoken
        b     1        10 lovelace + 12 x.SecondTesttoken
        c     0        100 lovelace + 13 x.SecondTesttoken + 103 y.Testtoken
            '''

    txs, _, _ = tx_in(utxo1, 'y.Testtoken', wanted_amount=0, max_tx=0)
    res = tx_out(utxo1, 'y.Testtoken', 0, txs)
    assert res == {'x.SecondTesttoken': 13, 'y.Testtoken': 0}

    res2 = tx_out(utxo1, 'y.Testtoken', 10, txs)
    assert res2 == {'x.SecondTesttoken': 13, 'y.Testtoken': 10}

    txs2, _, _ = tx_in(utxo1, 'x.SecondTesttoken', wanted_amount=12, max_tx=2)
    res3 = tx_out(utxo1, 'x.SecondTesttoken', 0, txs2)
    assert res3 == {'x.SecondTesttoken': 0, 'y.Testtoken': 103}

    txs3, _, _ = tx_in(utxo1, 'lovelace', wanted_amount=101, max_tx=2)
    res4 = tx_out(utxo1, 'lovelace', 101, txs3)
    assert res4 == {'x.SecondTesttoken': 25, 'y.Testtoken': 103}

def test_creating_tx_in_using_native_token():
    utxo1 = '''
                               TxHash                                 TxIx        Amount
    --------------------------------------------------------------------------------------
    a     0        2 lovelace + 11 x.SecondTesttoken + 101 y.Testtoken
    b     1        10 lovelace + 12 x.SecondTesttoken + 102 y.Testtoken
    c     0        100 lovelace + 13 x.SecondTesttoken + 103 y.Testtoken
        '''

    # a happy path
    res, lovelace, amount_lovelace = tx_in(utxo1, 'lovelace', 111, 3)
    assert len(res) == 3
    assert lovelace == 112
    assert amount_lovelace == lovelace
    assert res[0] == ('c#0')
    assert res[1] == ('b#1')
    assert res[2] == ('a#0')

    # see if we detect there isn't enough lovelace
    res2, lovelace, amount_lovelace = tx_in(utxo1, 'lovelace', 1000, 3)
    assert res2 == []
    assert lovelace == 112
    assert lovelace == amount_lovelace

    # see if we are ordering from having most lovelace, descending
    res3, lovelace, amount_lovelace = tx_in(utxo1, 'lovelace', 11, 3)
    assert len(res3) == 1
    assert lovelace == 100
    assert amount_lovelace == lovelace
    assert res3[0] == ('c#0')

    # see if we respect the max transaction count
    res4, lovelace, amount_lovelace = tx_in(utxo1, 'lovelace', 101, 1)
    assert len(res4) == 0
    assert lovelace == 100
    assert amount_lovelace == lovelace

    # see if we respect no tx limit
    res5, lovelace, amount_lovelace = tx_in(utxo1, 'lovelace', 111, 0)
    assert len(res) == 3
    assert lovelace == 112
    assert amount_lovelace == lovelace
    assert res[0] == ('c#0')
    assert res[1] == ('b#1')
    assert res[2] == ('a#0')

    # see if we respect no amount limit, aka take all transactions
    res6, lovelace, amount_lovelace = tx_in(utxo1, 'lovelace', 0, 0)
    assert len(res) == 3
    assert lovelace == 112
    assert amount_lovelace == lovelace
    assert res[0] == ('c#0')
    assert res[1] == ('b#1')
    assert res[2] == ('a#0')


def test_creating_tx_in_using_custom_tokens():
    utxo1 = '''
                               TxHash                                 TxIx        Amount
    --------------------------------------------------------------------------------------
    a     0        2 lovelace + 11 x.SecondTesttoken + 101 y.Testtoken
    b     1        10 lovelace + 102 y.Testtoken
    c     0        100 lovelace + 211 x.SecondTesttoken + 103 y.Testtoken
        '''

    # a happy path
    res, amount, amount_lovelace = tx_in(utxo1, 'x.SecondTesttoken', 111, 3)
    assert len(res) == 1
    assert amount == 211
    assert res[0] == ('c#0')
    assert amount_lovelace == 100

    # multiple txs
    res, amount, amount_lovelace = tx_in(utxo1, 'x.SecondTesttoken', 222, 3)
    assert len(res) == 2
    assert amount == 222
    assert res[0] == ('c#0')
    assert res[1] == ('a#0')
    assert amount_lovelace == 102

    # multiple txs
    res, amount, amount_lovelace = tx_in(utxo1, 'x.SecondTesttoken', 200, 3)
    assert len(res) == 1
    assert amount == 211
    assert res[0] == ('c#0')
    assert amount_lovelace == 100


def test_cli_formatting_in():
    txs = ['a#0', 'b#2']
    formatted = format_cli_in(txs)

    assert formatted == "--tx-in a#0 --tx-in b#2"


def test_cli_formatting_out():
    txs = {'x.SecondTesttoken': 0, 'y.Testtoken': 103}
    formatted = format_cli_out(txs)

    assert formatted == "0 x.SecondTesttoken + 103 y.Testtoken"

    txs = {}
    formatted = format_cli_out(txs)

    assert formatted == ""