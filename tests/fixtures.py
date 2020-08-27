# -*- coding: utf-8 -*-
import os
import tempfile

from curibio.sdk import PlateRecording
from curibio.sdk import WellFile
from mantarray_waveform_analysis import BESSEL_LOWPASS_10_UUID
from mantarray_waveform_analysis import PipelineTemplate
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
    pt = PipelineTemplate(
        noise_filter_uuid=BESSEL_LOWPASS_10_UUID,
        tissue_sampling_period=960,  # Tanner (8/27/20): This well data uses the Beta1.0 960cms tissue sampling period
    )
    pr = PlateRecording([wf], pt=pt)
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
