# -*- coding: utf-8 -*-

import datetime
import os

from curibio.sdk import ExcelWellFile
from stdlib_utils import get_current_file_abs_directory

from .fixtures import fixture_generic_excel_well_file_0_1_0


__fixtures__ = [
    fixture_generic_excel_well_file_0_1_0,
]

PATH_OF_CURRENT_FILE = get_current_file_abs_directory()


def test_ExcelWellFile__opens_and_get_file_name():
    file_name = os.path.join("excel_optical_data", "optical_data_filled_template.xlsx")
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            file_name,
        )
    )
    expected_path = os.path.join(PATH_OF_CURRENT_FILE, file_name)
    assert wf.get_file_name() == expected_path


def test_ExcelWellFile__get_file_version(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_file_version() == "0.1.0"


def test_ExcelWellFile__get_unique_recording_key(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_unique_recording_key() == -1  # TODO


def test_ExcelWellFile__get_well_name(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_well_name() == "A1"


def test_ExcelWellFile__get_well_index(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_well_index() == 0


def test_ExcelWellFile__get_plate_barcode(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_plate_barcode() == "M02001900"


def test_ExcelWellFile__get_user_account(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_user_account() == -1  # TODO


def test_ExcelWellFile__get_timestamp_of_beginning_of_data_acquisition(
    generic_excel_well_file_0_1_0,
):
    assert (
        generic_excel_well_file_0_1_0.get_timestamp_of_beginning_of_data_acquisition()
        == -1
    )


def test_ExcelWellFile__get_customer_account(generic_excel_well_file_0_1_0):
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            "optical_data_filled_template.xlsx",
        )
    )
    assert wf.get_customer_account() == -1  # TODO


def test_ExcelWellFile__get_mantarray_serial_number(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_mantarray_serial_number() == -1  # TODO


def test_ExcelWellFile__get_begin_recording(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_begin_recording() == datetime.datetime(
        2020, 10, 12, 4, 40
    )


def test_ExcelWellFile__get_timestamp_of_first_tissue_data_point(
    generic_excel_well_file_0_1_0,
):
    assert (
        generic_excel_well_file_0_1_0.get_timestamp_of_first_tissue_data_point() == -1
    )  # TODO


def test_ExcelWellFile__get_timestamp_of_first_ref_data_point(
    generic_excel_well_file_0_1_0,
):
    assert (
        generic_excel_well_file_0_1_0.get_timestamp_of_first_ref_data_point() == -1
    )  # TODO


def test_ExcelWellFile__get_tissue_sampling_period_microseconds(
    generic_excel_well_file_0_1_0,
):
    assert (
        generic_excel_well_file_0_1_0.get_tissue_sampling_period_microseconds()
        == 0.016666e6
    )


def test_ExcelWellFile__get_reference_sampling_period_microseconds(
    generic_excel_well_file_0_1_0,
):
    assert (
        generic_excel_well_file_0_1_0.get_reference_sampling_period_microseconds() == 0
    )


def test_ExcelWellFile__get_recording_start_index(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_recording_start_index() == -1  # TODO


def test_ExcelWellFile__get_twitches_point_up(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_twitches_point_up() is True


def test_ExcelWellFile__get_raw_tissue_reading(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_raw_tissue_reading().shape == (2, 1467)


def test_ExcelWellFile__get_raw_reference_reading(generic_excel_well_file_0_1_0):
    assert generic_excel_well_file_0_1_0.get_raw_reference_reading().shape == (2, 1467)
