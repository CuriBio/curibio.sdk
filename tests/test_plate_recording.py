# -*- coding: utf-8 -*-
import datetime
import os

from curibio.sdk import CONTINUOUS_WAVEFORM_SHEET_NAME
from curibio.sdk import INTERPOLATED_DATA_PERIOD
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_INSTRUMENT_ROW_START
from curibio.sdk import METADATA_RECORDING_ROW_START
from mantarray_file_manager import MANTARRAY_SERIAL_NUMBER_UUID
from mantarray_file_manager import METADATA_UUID_DESCRIPTIONS
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from openpyxl import load_workbook

from .fixtures import fixture_generic_well_file_0_3_1
from .fixtures import fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1

__fixtures__ = (
    fixture_generic_well_file_0_3_1,
    fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
)

# to create a file to look at: python3 -c "import os; from curibio.sdk import PlateRecording; PlateRecording([os.path.join('tests','h5','v0.3.1','MA20123456__2020_08_17_145752__A1.h5')]).write_xlsx('.',file_name='temp.xlsx')"


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
    for iter_row, metadata_uuid, expected_value in [
        (0, PLATE_BARCODE_UUID, "MA20123456"),
        (
            1,
            UTC_BEGINNING_RECORDING_UUID,
            datetime.datetime(2020, 8, 17, 14, 58, 10, 728253),
        ),
    ]:
        actual_label = metadata_sheet.cell(
            row=METADATA_RECORDING_ROW_START + 1 + iter_row + 1, column=1 + 1
        ).value
        actual_value = metadata_sheet.cell(
            row=METADATA_RECORDING_ROW_START + 1 + iter_row + 1, column=2 + 1
        ).value

        assert (iter_row, actual_label) == (
            iter_row,
            METADATA_UUID_DESCRIPTIONS[metadata_uuid],
        )
        assert (iter_row, actual_value) == (iter_row, expected_value)


def test_write_xlsx__creates_metadata_sheet_with_mantarray_info(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1

    pr.write_xlsx(tmp_dir)
    expected_file_name = "MA20123456-2020-08-17-14-58-10.xlsx"
    actual_workbook = load_workbook(os.path.join(tmp_dir, expected_file_name))
    assert actual_workbook.sheetnames[0] == METADATA_EXCEL_SHEET_NAME

    metadata_sheet = actual_workbook[METADATA_EXCEL_SHEET_NAME]
    row_start = METADATA_INSTRUMENT_ROW_START
    assert (
        metadata_sheet.cell(row=row_start + 1, column=0 + 1).value
        == "Device Information:"
    )
    for iter_row, metadata_uuid, expected_value in [
        (0, MANTARRAY_SERIAL_NUMBER_UUID, "M02001900"),
    ]:
        actual_label = metadata_sheet.cell(
            row=row_start + 1 + iter_row + 1, column=1 + 1
        ).value
        actual_value = metadata_sheet.cell(
            row=row_start + 1 + iter_row + 1, column=2 + 1
        ).value

        assert (iter_row, actual_label) == (
            iter_row,
            METADATA_UUID_DESCRIPTIONS[metadata_uuid],
        )
        assert (iter_row, actual_value) == (iter_row, expected_value)


def test_write_xlsx__creates_continuous_recording_sheet__with_single_well(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1

    pr.write_xlsx(tmp_dir)
    expected_file_name = "MA20123456-2020-08-17-14-58-10.xlsx"
    actual_workbook = load_workbook(os.path.join(tmp_dir, expected_file_name))
    expected_sheet_name = CONTINUOUS_WAVEFORM_SHEET_NAME
    assert actual_workbook.sheetnames[1] == expected_sheet_name
    actual_sheet = actual_workbook[expected_sheet_name]

    assert actual_sheet.cell(row=0 + 1, column=1 + 1).value == "A1"
    assert actual_sheet.cell(row=0 + 1, column=24 + 1).value == "D6"

    assert actual_sheet.cell(row=0 + 1, column=0 + 1).value == "Time (seconds)"
    assert actual_sheet.cell(row=1 + 1, column=0 + 1).value == 0
    assert (
        actual_sheet.cell(row=10 + 1, column=0 + 1).value
        == 9 * INTERPOLATED_DATA_PERIOD
    )

    assert actual_sheet.cell(row=0 + 1, column=10 + 1).value == "B3"
    assert actual_sheet.cell(row=1 + 1, column=10 + 1).value == -1230373
    assert actual_sheet.cell(row=10 + 1, column=10 + 1).value == -1590952.5
