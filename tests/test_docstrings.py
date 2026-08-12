import doctest

from tbot223_base import exception_tracker, result


def test_public_docstrings_are_deterministic_doctests():
    result_outcome = doctest.testmod(result, optionflags=doctest.ELLIPSIS)
    tracker_outcome = doctest.testmod(exception_tracker, optionflags=doctest.ELLIPSIS)

    assert result_outcome.failed == 0
    assert tracker_outcome.failed == 0
