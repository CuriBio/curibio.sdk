# -*- coding: utf-8 -*-
"""Tests for PlateRecording subclass.

To create a file to look at: python3 -c "import os; from curibio.sdk import PlateRecording; PlateRecording([os.path.join('tests','h5','v0.3.1','MA20123456__2020_08_17_145752__A1.h5')]).write_xlsx('.',file_name='temp.xlsx')"
To create a file to look at: python3 -c "import os; from curibio.sdk import PlateRecording; PlateRecording.from_directory(os.path.join('tests','h5','v0.3.1')).write_xlsx('.',file_name='temp.xlsx')"
"""
import datetime
import os

from curibio.sdk import __version__
from curibio.sdk import AGGREGATE_METRICS_SHEET_NAME
from curibio.sdk import CONTINUOUS_WAVEFORM_SHEET_NAME
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_INSTRUMENT_ROW_START
from curibio.sdk import METADATA_OUTPUT_FILE_ROW_START
from curibio.sdk import METADATA_RECORDING_ROW_START
from curibio.sdk import PlateRecording
from curibio.sdk import TSP_TO_INTERPOLATED_DATA_PERIOD
from freezegun import freeze_time
from mantarray_file_manager import MANTARRAY_SERIAL_NUMBER_UUID
from mantarray_file_manager import METADATA_UUID_DESCRIPTIONS
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import SOFTWARE_BUILD_NUMBER_UUID
from mantarray_file_manager import SOFTWARE_RELEASE_VERSION_UUID
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from mantarray_waveform_analysis import BESSEL_LOWPASS_10_UUID
from mantarray_waveform_analysis import BESSEL_LOWPASS_30_UUID
from mantarray_waveform_analysis import CENTIMILLISECONDS_PER_SECOND
from openpyxl import load_workbook

from .fixtures import fixture_generic_well_file_0_3_1
from .fixtures import fixture_generic_well_file_0_3_1__2
from .fixtures import fixture_generic_well_file_0_3_2
from .fixtures import fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1
from .fixtures import fixture_plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1
from .utils import get_cell_value

__fixtures__ = (
    fixture_generic_well_file_0_3_1,
    fixture_generic_well_file_0_3_2,
    fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
    fixture_plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1,
    fixture_generic_well_file_0_3_1__2,
)


def test_init__creates_a_pipeline_template_with_correct_sampling_frequency_and_bessel_for_960cms_if_none_is_given(
    generic_well_file_0_3_1,
):
    pr = PlateRecording([generic_well_file_0_3_1])
    actual = pr.get_pipeline_template()
    assert actual.noise_filter_uuid == BESSEL_LOWPASS_10_UUID
    assert actual.tissue_sampling_period == 960


def test_init__creates_a_pipeline_template_with_correct_sampling_frequency_and_bessel_for_160cms_if_none_is_given(
    generic_well_file_0_3_2,
):
    pr = PlateRecording([generic_well_file_0_3_2])
    actual = pr.get_pipeline_template()
    assert actual.noise_filter_uuid == BESSEL_LOWPASS_30_UUID
    assert actual.tissue_sampling_period == 160


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


def test_write_xlsx__creates_aggregate_metrics_sheet(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1
    file_dir = tmp_dir

    pr.write_xlsx(file_dir)
    expected_file_name = "MA20123456-2020-08-17-14-58-10.xlsx"
    actual_workbook = load_workbook(os.path.join(file_dir, expected_file_name))
    assert actual_workbook.sheetnames[2] == AGGREGATE_METRICS_SHEET_NAME
    aggregate_metrics_sheet = actual_workbook[AGGREGATE_METRICS_SHEET_NAME]
    assert get_cell_value(aggregate_metrics_sheet, 0, 2) == "A1"
    assert get_cell_value(aggregate_metrics_sheet, 1, 1) == "n"


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
        get_cell_value(metadata_sheet, METADATA_RECORDING_ROW_START, 0)
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
        actual_label = get_cell_value(
            metadata_sheet, METADATA_RECORDING_ROW_START + 1 + iter_row, 1
        )
        actual_value = get_cell_value(
            metadata_sheet, METADATA_RECORDING_ROW_START + 1 + iter_row, 2
        )

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
    curr_row = METADATA_INSTRUMENT_ROW_START
    assert get_cell_value(metadata_sheet, curr_row, 0) == "Device Information:"
    curr_row += 1
    assert get_cell_value(metadata_sheet, curr_row, 1) == "H5 File Layout Version"
    assert get_cell_value(metadata_sheet, curr_row, 2) == "0.3.1"
    curr_row += 1
    for iter_row, metadata_uuid, expected_value in [
        (0, MANTARRAY_SERIAL_NUMBER_UUID, "M02001900"),
        (1, SOFTWARE_RELEASE_VERSION_UUID, "0.2.2"),
        (2, SOFTWARE_BUILD_NUMBER_UUID, "200817143923--820"),
    ]:
        actual_label = get_cell_value(metadata_sheet, curr_row + iter_row, 1)
        actual_value = get_cell_value(metadata_sheet, curr_row + iter_row, 2)

        assert (iter_row, actual_label) == (
            iter_row,
            METADATA_UUID_DESCRIPTIONS[metadata_uuid],
        )
        assert (iter_row, actual_value) == (iter_row, expected_value)


@freeze_time("2020-09-02 12:20:12.223344")
def test_write_xlsx__creates_metadata_sheet_with_output_format_info(
    plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_generic_well_file_0_3_1

    pr.write_xlsx(tmp_dir)
    expected_file_name = "MA20123456-2020-08-17-14-58-10.xlsx"
    actual_workbook = load_workbook(os.path.join(tmp_dir, expected_file_name))
    assert actual_workbook.sheetnames[0] == METADATA_EXCEL_SHEET_NAME

    metadata_sheet = actual_workbook[METADATA_EXCEL_SHEET_NAME]
    curr_row = METADATA_OUTPUT_FILE_ROW_START
    assert get_cell_value(metadata_sheet, curr_row, 0) == "Output Format:"

    curr_row += 1
    assert get_cell_value(metadata_sheet, curr_row, 1) == "SDK Version"
    assert get_cell_value(metadata_sheet, curr_row, 2) == __version__

    curr_row += 1
    assert get_cell_value(metadata_sheet, curr_row, 1) == "File Creation Timestamp"
    assert get_cell_value(metadata_sheet, curr_row, 2) == datetime.datetime(
        2020, 9, 2, 12, 20, 12
    )


def test_write_xlsx__creates_continuous_recording_sheet__with_multiple_well_data(
    plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1,
):
    pr, tmp_dir = plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1

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
        == 9 * TSP_TO_INTERPOLATED_DATA_PERIOD[960] / CENTIMILLISECONDS_PER_SECOND
    )

    assert actual_sheet.cell(row=0 + 1, column=5 + 1).value == "A2"
    assert actual_sheet.cell(row=1 + 1, column=10 + 1).value == -1230360
    assert actual_sheet.cell(row=10 + 1, column=10 + 1).value == -1535254.625

    assert actual_sheet.cell(row=0 + 1, column=10 + 1).value == "B3"
    assert actual_sheet.cell(row=1 + 1, column=10 + 1).value == -1230360
    assert actual_sheet.cell(row=10 + 1, column=10 + 1).value == -1535254.625
