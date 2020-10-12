# -*- coding: utf-8 -*-

import os

from curibio.sdk import ExcelWellFile
from stdlib_utils import get_current_file_abs_directory

PATH_OF_CURRENT_FILE = get_current_file_abs_directory()


def test_ExcelWellFile__opens_and_get_file_name():
    file_name = None  # TODO
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            file_name,
        )
    )
    assert wf.get_file_name() == file_name


def test_ExcelWellFile__get_file_version():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_file_version() == "0.0.0"  # TODO


def test_ExcelWellFile__get_unique_recording_key():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_unique_recording_key() == -1  # TODO


def test_ExcelWellFile__get_well_name():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_well_name() == "A0"  # TODO


def test_ExcelWellFile__get_well_index():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_well_index() == -1  # TODO


def test_ExcelWellFile__get_plate_barcode():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_plate_barcode() == -1  # TODO


def test_ExcelWellFile__get_user_account():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_user_account() == -1  # TODO


def test_ExcelWellFile__get_timestamp_of_beginning_of_data_acquisition():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_timestamp_of_beginning_of_data_acquisition() == -1  # TODO


def test_ExcelWellFile__get_customer_account():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_customer_account() == -1  # TODO


def test_ExcelWellFile__get_mantarray_serial_number():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_mantarray_serial_number() == -1  # TODO


def test_ExcelWellFile__get_begin_recording():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_begin_recording() == -1  # TODO


def test_ExcelWellFile__get_timestamp_of_first_tissue_data_point():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_timestamp_of_first_tissue_data_point() == -1  # TODO


def test_ExcelWellFile__get_timestamp_of_first_ref_data_point():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_timestamp_of_first_ref_data_point() == -1  # TODO


def test_ExcelWellFile__get_tissue_sampling_period_microseconds():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_tissue_sampling_period_microseconds() == -1  # TODO


def test_ExcelWellFile__get_reference_sampling_period_microseconds():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_reference_sampling_period_microseconds() == -1  # TODO


def test_ExcelWellFile__get_recording_start_index():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_recording_start_index() == -1  # TODO


def test_ExcelWellFile__get_raw_tissue_reading():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_raw_tissue_reading() == -1  # TODO


def test_ExcelWellFile__get_raw_reference_reading():
    wf = ExcelWellFile(
        os.path.join(
            PATH_OF_CURRENT_FILE,
            "excel_optical_data",
            # TODO
        )
    )
    assert wf.get_raw_reference_reading() == -1  # TODO
