import pytest

from library.assert_cardano_synced import (
    get_progress_from_response
)

def test_getting_progress_from_response():

    progress = 15.56

    sample_response='''
    {
        "epoch": 25,
        "hash": "dd8b365827530410b2be09f7f018dbcc09df5c2727eb06ddef195c2d75252ebb",
        "slot": 547585,
        "block": 546517,
        "era": "Byron",
        "syncProgress": "%.2f"
    }
    ''' % progress

    sync_progress = get_progress_from_response(sample_response)

    assert sync_progress == progress