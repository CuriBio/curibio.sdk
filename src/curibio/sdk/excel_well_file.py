# -*- coding: utf-8 -*-
"""Classes and functions for finding and managing excel files."""
import datetime
from typing import Any
from typing import Optional
from typing import Tuple
from uuid import UUID

from mantarray_file_manager import MICROSECONDS_PER_CENTIMILLISECOND
from mantarray_file_manager import WellFile
from nptyping import NDArray
import numpy as np
from stdlib_utils import get_current_file_abs_directory

PATH_OF_CURRENT_FILE = get_current_file_abs_directory()


def _get_excel_metadata_value() -> Any:
    # the metadata that we want users to for sure include in Excel files:
    #
    #   plate barcode
    #   some recording timestamp (it's going to be approximate since it's just their guess)
    #   well name (we can convert to well index using LabwareDefinition)
    #   sampling period / framerate of the camera
    #
    pass


class ExcelWellFile(WellFile):
    """Wrapper around an Excel file for a single well of optical data.

    Args:
        file_name: The path of the H5 file to open.

    Attributes:
        _excel_file: The opened H5 file object.
    """

    def __init__(self, file_name: str) -> None:
        self._excel_file = None
        self._file_name = file_name
        self._file_version = "0.1.0"
        self._raw_tissue_reading: Optional[NDArray[(2, Any), int]] = None
        self._raw_ref_reading: Optional[NDArray[(2, Any), int]] = None

    def get_unique_recording_key(self) -> Tuple[str, datetime.datetime]:
        pass

    def get_well_name(self) -> str:
        # TODO: this is a must have in the excel file
        pass

    def get_well_index(self) -> int:
        # TODO: this is a must have in the excel file
        pass

    def get_plate_barcode(self) -> str:
        # TODO: this is a must have in the excel file
        pass

    def get_user_account(self) -> UUID:
        pass

    def get_timestamp_of_beginning_of_data_acquisition(self) -> datetime.datetime:
        pass

    def get_customer_account(self) -> UUID:
        pass

    def get_mantarray_serial_number(self) -> str:
        pass

    def get_begin_recording(self) -> datetime.datetime:
        # TODO: this is a must have in the excel file
        pass

    def get_timestamp_of_first_tissue_data_point(self) -> datetime.datetime:
        pass

    def get_timestamp_of_first_ref_data_point(self) -> datetime.datetime:
        pass

    def get_tissue_sampling_period_microseconds(self) -> int:
        # TODO: this is a must have in the excel file
        pass

    def get_reference_sampling_period_microseconds(self) -> int:
        # TODO: ? this is a must have in the excel file
        pass

    def get_recording_start_index(self) -> int:
        pass

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
