# -*- coding: utf-8 -*-
"""Docstring."""
import datetime
import os
from typing import Optional

from mantarray_file_manager import METADATA_UUID_DESCRIPTIONS
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import PlateRecording as FileManagerPlateRecording
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from xlsxwriter import Workbook

from .constants import METADATA_EXCEL_SHEET_NAME
from .constants import METADATA_RECORDING_ROW_START


class PlateRecording(FileManagerPlateRecording):
    """Manages aspects of analyzing a plate recording session."""

    def write_xlsx(self, file_dir: str, file_name: Optional[str] = None) -> None:
        """Create an XLSX file.

        Args:
            file_dir: the directory in which to create the file.
            file_name: By default an automatic name is generated based on barcode and recording date. Extension will always be xlsx---if user provides something else then it is stripped
        """
        first_well_index = self.get_well_indices()[0]
        # this file is used to get general information applicable across the recording
        first_well_file = self.get_well_by_index(first_well_index)

        if file_name is None:
            file_name = f"{first_well_file.get_plate_barcode()}-{first_well_file.get_begin_recording().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx"
        file_path = os.path.join(file_dir, file_name)
        workbook = Workbook(
            file_path, {"default_date_format": "YYYY-MM-DD hh:mm:ss UTC"}
        )
        metadata_sheet = workbook.add_worksheet(METADATA_EXCEL_SHEET_NAME)
        curr_sheet = metadata_sheet
        curr_sheet.write(METADATA_RECORDING_ROW_START, 0, "Recording Information:")
        for iter_row, (iter_metadata_uuid, iter_value) in enumerate(
            (
                (PLATE_BARCODE_UUID, first_well_file.get_plate_barcode()),
                (UTC_BEGINNING_RECORDING_UUID, first_well_file.get_begin_recording()),
            )
        ):
            row_in_sheet = METADATA_RECORDING_ROW_START + 1 + iter_row
            curr_sheet.write(
                row_in_sheet, 1, METADATA_UUID_DESCRIPTIONS[iter_metadata_uuid],
            )
            if isinstance(iter_value, datetime.datetime):
                # Excel doesn't support timezones in datetimes
                iter_value = iter_value.replace(tzinfo=None)
            curr_sheet.write(
                row_in_sheet, 2, iter_value,
            )
        curr_sheet.set_column(0, 0, 25)
        curr_sheet.set_column(1, 1, 40)
        curr_sheet.set_column(2, 2, 25)
        workbook.close()  # This is actually when the file gets written to d
