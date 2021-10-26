import pytest

from library.cardano_token_lookup import (
    tokens_from_utxo
)


def test_token_listing():
    utxo1 = '''
                               TxHash                                 TxIx        Amount
    --------------------------------------------------------------------------------------
    a     0        2 lovelace
    b     1        10 lovelace + 2 x.token1 + 100 y.token1
    c     0        100 lovelace + 20 y.token1 + 103 z.token2
        '''

    # a happy path
    tokens = tokens_from_utxo(utxo1)
    assert len(tokens) == 4
    assert tokens['lovelace'] == 112
    assert tokens['x.token1'] == 2
    assert tokens['y.token1'] == 120
    assert tokens['z.token2'] == 103
