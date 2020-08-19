# -*- coding: utf-8 -*-
import os

from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_RECORDING_ROW_START
from openpyxl import load_workbook

from .fixtures import fixture_generic_well_file_0_3_1
from .fixtures import fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1

__fixtures__ = (
    fixture_generic_well_file_0_3_1,
    fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
)


def test_write_xlsx__creates_file_at_supplied_path_and_name(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1
    file_dir = tmp_dir
    file_name = "my_file.xlsx"
    pr.write_xlsx(file_dir, file_name=file_name)
    assert os.path.exists(os.path.join(file_dir, file_name)) is True


def test_write_xlsx__creates_file_at_supplied_path_with_auto_generated_name(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1

    file_dir = tmp_dir

    pr.write_xlsx(file_dir)
    expected_file_name = "MA20123456-2020-08-17-14-58-10.xlsx"
    assert os.path.exists(os.path.join(file_dir, expected_file_name)) is True


def test_write_xlsx__creates_metadata_sheet_with_recording_info(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1
    file_dir = tmp_dir

    pr.write_xlsx(file_dir)
    expected_file_name = "MA20123456-2020-08-17-14-58-10.xlsx"
    actual_workbook = load_workbook(os.path.join(file_dir, expected_file_name))
    assert actual_workbook.sheetnames[0] == METADATA_EXCEL_SHEET_NAME

    metadata_sheet = actual_workbook[METADATA_EXCEL_SHEET_NAME]
    assert (
        metadata_sheet.cell(row=METADATA_RECORDING_ROW_START + 1, column=0 + 1).value
        == "Recording Information:"
    )
