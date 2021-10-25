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
    assert len(tokens) == 2
    assert tokens['token1'] == 122
    assert tokens['token2'] == 103
