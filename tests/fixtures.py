# -*- coding: utf-8 -*-
import os
import tempfile

from curibio.sdk import PlateRecording
from curibio.sdk import WellFile
import pytest
from stdlib_utils import get_current_file_abs_directory

PATH_OF_CURRENT_FILE = get_current_file_abs_directory()


@pytest.fixture(scope="function", name="generic_well_file_0_3_1")
def fixture_generic_well_file_0_3_1():
    wf = WellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "h5",
            "v0.3.1",
            "MA20123456__2020_08_17_145752__B3.h5",
        )
    )
    yield wf


@pytest.fixture(
    scope="function", name="plate_recording_in_tmp_dir_for_generic_well_file_0_3_1"
)
def fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1():
    wf = WellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "h5",
            "v0.3.1",
            "MA20123456__2020_08_17_145752__B3.h5",
        )
    )
    pr = PlateRecording([wf])
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pr, tmp_dir


@pytest.fixture(scope="function", name="generic_well_file_0_3_1__2")
def fixture_generic_well_file_0_3_1__2():
    wf = WellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "h5",
            "v0.3.1",
            "MA20123456__2020_08_17_145752__A2.h5",
        )
    )
    yield wf
