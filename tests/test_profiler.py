import time

import pytest
from pyprofile import profile


@pytest.fixture
def dump_dir(tmp_path):
    d = tmp_path / "pyprofile_test_dumps"
    d.mkdir()
    return d


def test_profile_decorator(dump_dir):
    """Only test if the profile decorator is written correctly.
    """

    @profile(dump_dir=dump_dir)
    def fn_with_parameters(seconds):
        time.sleep(seconds)
        return seconds

    @profile()
    def fn():
        seconds = 2
        time.sleep(seconds)
        return seconds

    assert fn() == 2, "fn with no parameters failed."
    assert fn_with_parameters(5) == 5, "fn with parameters failed."
