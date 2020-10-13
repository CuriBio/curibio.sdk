# -*- coding: utf-8 -*-
"""Classes and functions for finding and managing excel files."""
import datetime
from typing import Any
from typing import Optional
from typing import Tuple
from uuid import UUID

from mantarray_file_manager import MICROSECONDS_PER_CENTIMILLISECOND
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import TISSUE_SAMPLING_PERIOD_UUID
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from mantarray_file_manager import WELL_NAME_UUID
from mantarray_file_manager import WellFile
from nptyping import NDArray
import numpy as np
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from stdlib_utils import get_current_file_abs_directory
from xlsxwriter.utility import xl_cell_to_rowcol

from .constants import EXCEL_OPTICAL_METADATA_CELLS
from .constants import TWITCHES_POINT_UP_UUID

PATH_OF_CURRENT_FILE = get_current_file_abs_directory()


def _get_well_index_from_well_name(well_name: str) -> int:
    return (ord(well_name[0]) - ord("A")) * 4 + int(well_name[1]) - 1


def _get_single_sheet(file_name: str) -> Any:
    wb = load_workbook(file_name)
    return wb[wb.sheetnames[0]]


def _get_cell_value(sheet: Worksheet, zero_based_row: int, zero_based_col: int) -> str:
    return str(sheet.cell(row=zero_based_row + 1, column=zero_based_col + 1).value)


def _get_excel_metadata_value(sheet: Worksheet, metadata_uuid: UUID) -> str:
    # the metadata that we want users to for sure include in Excel files:
    #
    #   plate barcode
    #   some recording timestamp (it's going to be approximate since it's just their guess)
    #   well name (we can convert to well index using LabwareDefinition)
    #   sampling period / framerate of the camera
    #   twitches point up (bool)
    #
    cell_name = EXCEL_OPTICAL_METADATA_CELLS[metadata_uuid]
    row, col = xl_cell_to_rowcol(cell_name)
    return _get_cell_value(sheet, row, col)


class ExcelWellFile(WellFile):
    """Wrapper around an Excel file for a single well of optical data.

    Args:
        file_name: The path of the excel file to open.

    Attributes:
        _excel_sheet: The opened excel sheet.
    """

    def __init__(self, file_name: str) -> None:
        self._excel_sheet = _get_single_sheet(file_name)
        self._file_name = file_name
        self._file_version = "0.1.0"
        self._raw_tissue_reading: Optional[NDArray[(2, Any), int]] = None
        self._raw_ref_reading: Optional[NDArray[(2, Any), int]] = None

    def get_h5_file(self) -> None:
        raise NotImplementedError("ExcelWellFiles do not store an H5 file")

    def get_unique_recording_key(self) -> Tuple[str, datetime.datetime]:
        pass

    def get_well_name(self) -> str:
        return _get_excel_metadata_value(self._excel_sheet, WELL_NAME_UUID)

    def get_well_index(self) -> int:
        return _get_well_index_from_well_name(self.get_well_name())

    def get_plate_barcode(self) -> str:
        return _get_excel_metadata_value(self._excel_sheet, PLATE_BARCODE_UUID)

    def get_user_account(self) -> UUID:
        pass

    def get_timestamp_of_beginning_of_data_acquisition(self) -> datetime.datetime:
        pass

    def get_customer_account(self) -> UUID:
        pass

    def get_mantarray_serial_number(self) -> str:
        pass

    def get_begin_recording(self) -> datetime.datetime:
        timestamp_str = _get_excel_metadata_value(
            self._excel_sheet, UTC_BEGINNING_RECORDING_UUID
        )
        timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return timestamp

    def get_timestamp_of_first_tissue_data_point(self) -> datetime.datetime:
        pass

    def get_timestamp_of_first_ref_data_point(self) -> datetime.datetime:
        pass

    def get_tissue_sampling_period_microseconds(self) -> int:
        sampling_period_seconds = float(
            _get_excel_metadata_value(self._excel_sheet, TISSUE_SAMPLING_PERIOD_UUID)
        )
        return int(round(sampling_period_seconds, 6) * 1e6)

    def get_reference_sampling_period_microseconds(self) -> int:
        # TODO: ? this is a must have in the excel file
        pass

    def get_recording_start_index(self) -> int:
        pass

    def get_twitches_point_up(self) -> bool:
        return "y" in _get_excel_metadata_value(
            self._excel_sheet, TWITCHES_POINT_UP_UUID
        )

    def get_raw_tissue_reading(self) -> NDArray[(2, Any), int]:
        if self._raw_tissue_reading is None:
            recording_start_index_useconds = (
                self.get_recording_start_index() * MICROSECONDS_PER_CENTIMILLISECOND
            )
            timestamp_of_start_index = (
                self.get_timestamp_of_beginning_of_data_acquisition()
                + datetime.timedelta(microseconds=recording_start_index_useconds)
            )
            time_delta = (
                self.get_timestamp_of_first_ref_data_point() - timestamp_of_start_index
            )

            time_delta_centimilliseconds = int(
                time_delta
                / datetime.timedelta(microseconds=MICROSECONDS_PER_CENTIMILLISECOND)
            )

            time_step = int(
                self.get_reference_sampling_period_microseconds()
                / MICROSECONDS_PER_CENTIMILLISECOND
            )
            tissue_data = np.zeros((1, 1))  # TODO

            times = np.arange(len(tissue_data), dtype=np.int32) * time_step
            len_time = len(times)

            self._raw_tissue_reading = np.array(
                (times + time_delta_centimilliseconds, tissue_data[:len_time]),
                dtype=np.int32,
            )
        return self._raw_tissue_reading

    def get_raw_reference_reading(self) -> NDArray[(2, Any), int]:
        if self._raw_ref_reading is None:
            recording_start_index_useconds = (
                self.get_recording_start_index() * MICROSECONDS_PER_CENTIMILLISECOND
            )
            timestamp_of_start_index = (
                self.get_timestamp_of_beginning_of_data_acquisition()
                + datetime.timedelta(microseconds=recording_start_index_useconds)
            )
            time_delta = (
                self.get_timestamp_of_first_ref_data_point() - timestamp_of_start_index
            )

            time_delta_centimilliseconds = int(
                time_delta
                / datetime.timedelta(microseconds=MICROSECONDS_PER_CENTIMILLISECOND)
            )

            time_step = int(
                self.get_reference_sampling_period_microseconds()
                / MICROSECONDS_PER_CENTIMILLISECOND
            )
            ref_data = np.zeros((1, 1))  # TODO

            times = np.arange(len(ref_data), dtype=np.int32) * time_step
            len_time = len(times)

            self._raw_ref_reading = np.array(
                (times + time_delta_centimilliseconds, ref_data[:len_time]),
                dtype=np.int32,
            )
        return self._raw_ref_reading
