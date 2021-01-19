# -*- coding: utf-8 -*-
from curibio.sdk import __version__
from curibio.sdk import check_if_latest_version
from curibio.sdk import get_latest_version_from_pypi
from curibio.sdk import jupyter_helpers
import pytest
import requests
import semver


@pytest.mark.slow  # connects to actual PyPI website
def test_get_latest_version_from_pypi__When_invoked_to_real_PyPI_url__Then_it_returns_something_that_looks_like_semver():
    actual = get_latest_version_from_pypi()
    parsed = semver.VersionInfo.parse(
        actual
    )  # will raise a ValueError if the string is not valid semantic versioning
    assert isinstance(parsed.major, int)


def test_get_latest_version_from_pypi__Given_Response_json_is_mocked_to_return_a_specific_version__and__get_is_mocked_to_return_a_dummy_response__When_invoked__Then_URL_matches_expectations_and_return_value_is_extracted_correctly_from_json(
    mocker,
):
    expected = "0.0.1"
    mocker.patch.object(
        requests.Response,
        "json",
        autospec=True,
        return_value={"info": {"version": expected}},
    )
    mocked_get = mocker.patch.object(
        requests, "get", autospec=True, return_value=requests.Response()
    )

    actual = get_latest_version_from_pypi()

    mocked_get.assert_called_once_with("https://pypi.org/pypi/curibio.sdk/json")

    assert actual == expected


def test_check_if_latest_version__Given_pypi_is_mocked_to_return_not_current_version__When_function_is_invoked__Then_message_is_printed(
    mocker,
):
    mocked_print = mocker.patch("builtins.print", autospec=True)
    mocked_version = "0.0.0"
    mocker.patch.object(
        jupyter_helpers,
        "get_latest_version_from_pypi",
        autospec=True,
        return_value=mocked_version,
    )
    check_if_latest_version()
    first_call_to_print = mocked_print.call_args_list[0][0][0]
    assert __version__ in first_call_to_print
    assert mocked_version in first_call_to_print
    assert mocked_print.call_count == 1


def test_check_if_latest_version__Given_pypi_is_mocked_to_return_current_version__When_function_is_invoked__Then_nothing_is_printed(
    mocker,
):
    mocker.patch.object(
        jupyter_helpers,
        "get_latest_version_from_pypi",
        autospec=True,
        return_value=__version__,
    )
    mocked_print = mocker.patch("builtins.print", autospec=True)
    check_if_latest_version()
    assert mocked_print.call_count == 0
