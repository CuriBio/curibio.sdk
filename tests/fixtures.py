# -*- coding: utf-8 -*-
import os
import tempfile

from curibio.sdk import ExcelWellFile
from curibio.sdk import PlateRecording
from curibio.sdk import WellFile
from mantarray_waveform_analysis import BESSEL_LOWPASS_10_UUID
from mantarray_waveform_analysis import CENTIMILLISECONDS_PER_SECOND
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


@pytest.fixture(scope="session", name="generic_well_file_0_3_2")
def fixture_generic_well_file_0_3_2():
    wf = WellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "h5",
            "v0.3.2",
            "MA20223322__2020_09_02_173919",
            "MA20223322__2020_09_02_173919__A2.h5",
        )
    )
    yield wf


@pytest.fixture(
    scope="session", name="plate_recording_in_tmp_dir_for_generic_well_file_0_3_2"
)
def fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_2(
    generic_well_file_0_3_2,
):
    period = (
        generic_well_file_0_3_2.get_tissue_sampling_period_microseconds()
        / 1000000
        * CENTIMILLISECONDS_PER_SECOND
    )
    pt = PipelineTemplate(
        noise_filter_uuid=BESSEL_LOWPASS_10_UUID,
        tissue_sampling_period=period,
    )
    pr = PlateRecording([generic_well_file_0_3_2], pipeline_template=pt)
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pr, tmp_dir


@pytest.fixture(scope="session", name="plate_recording_in_tmp_dir_for_24_wells_0_3_2")
def fixture_plate_recording_in_tmp_dir_for_24_wells_0_3_2():
    pr = PlateRecording.from_directory(
        os.path.join(
            PATH_OF_CURRENT_FILE, "h5", "v0.3.2", "MA20223322__2020_09_02_173919"
        )
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pr, tmp_dir


@pytest.fixture(scope="session", name="real_3min_well_file_0_3_1")
def fixture_real_3min_well_file_0_3_1():
    wf = WellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "h5",
            "v0.3.1",
            "MA201110001__2020_09_03_213024__A3.h5",
        )
    )
    yield wf


@pytest.fixture(
    scope="session", name="plate_recording_in_tmp_dir_for_real_3min_well_file_0_3_1"
)
def fixture_plate_recording_in_tmp_dir_for_real_3min_well_file_0_3_1(
    real_3min_well_file_0_3_1,
):
    period = (
        real_3min_well_file_0_3_1.get_tissue_sampling_period_microseconds()
        / 1000000
        * CENTIMILLISECONDS_PER_SECOND
    )
    pt = PipelineTemplate(
        noise_filter_uuid=BESSEL_LOWPASS_10_UUID,
        tissue_sampling_period=period,
    )
    pr = PlateRecording([real_3min_well_file_0_3_1], pipeline_template=pt)
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pr, tmp_dir


@pytest.fixture(
    scope="function", name="plate_recording_in_tmp_dir_for_generic_well_file_0_3_1"
)
def fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1(
    generic_well_file_0_3_1,
):
    period = (
        generic_well_file_0_3_1.get_tissue_sampling_period_microseconds()
        / 1000000
        * CENTIMILLISECONDS_PER_SECOND
    )
    pt = PipelineTemplate(
        noise_filter_uuid=BESSEL_LOWPASS_10_UUID,
        tissue_sampling_period=period,
    )
    pr = PlateRecording([generic_well_file_0_3_1], pipeline_template=pt)
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


@pytest.fixture(
    scope="function", name="plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1"
)
def fixture_plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1(
    generic_well_file_0_3_1, generic_well_file_0_3_1__2
):
    period = (
        generic_well_file_0_3_1.get_tissue_sampling_period_microseconds()
        / 1000000
        * CENTIMILLISECONDS_PER_SECOND
    )
    pt = PipelineTemplate(
        noise_filter_uuid=BESSEL_LOWPASS_10_UUID,
        tissue_sampling_period=period,
    )
    pr = PlateRecording(
        [generic_well_file_0_3_1, generic_well_file_0_3_1__2], pipeline_template=pt
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pr, tmp_dir


@pytest.fixture(scope="function", name="generic_excel_well_file_0_1_0")
def fixture_generic_excel_well_file_0_1_0():
    file_name = "optical_data_filled_template.xlsx"
    ewf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            file_name,
        )
    )
    yield ewf
