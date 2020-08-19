# -*- coding: utf-8 -*-
"""Docstring."""
import os
from typing import Optional

from mantarray_file_manager import PlateRecording as FileManagerPlateRecording
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
        workbook = Workbook(file_path)
        metadata_sheet = workbook.add_worksheet(METADATA_EXCEL_SHEET_NAME)
        metadata_sheet.write(METADATA_RECORDING_ROW_START, 0, "Recording Information:")
        workbook.close()  # This is actually when the file gets written to disk. If someone has the existing file open, then an EnvironmentError will probably be raised
