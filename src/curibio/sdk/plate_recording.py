# -*- coding: utf-8 -*-
"""Docstring."""
import copy
import datetime
import os
from typing import Any
from typing import Dict
from typing import Optional

from mantarray_file_manager import MANTARRAY_SERIAL_NUMBER_UUID
from mantarray_file_manager import METADATA_UUID_DESCRIPTIONS
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import PlateRecording as FileManagerPlateRecording
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from mantarray_file_manager import WellFile
from mantarray_waveform_analysis import BESSEL_LOWPASS_10_UUID
from mantarray_waveform_analysis import PipelineTemplate
import numpy as np
from scipy import interpolate
import xlsxwriter
from xlsxwriter import Workbook

from .constants import CONTINUOUS_WAVEFORM_SHEET_NAME
from .constants import METADATA_EXCEL_SHEET_NAME
from .constants import METADATA_INSTRUMENT_ROW_START
from .constants import METADATA_RECORDING_ROW_START
from .constants import TSP_TO_INTERPOLATED_DATA_PERIOD
from .constants import TWENTY_FOUR_WELL_PLATE


DEFAULT_PIPELINE_TEMPLATE = PipelineTemplate(
    noise_filter_uuid=BESSEL_LOWPASS_10_UUID, tissue_sampling_period=160,
)


def _write_xlsx_device_metadata(
    curr_sheet: xlsxwriter.worksheet.Worksheet, first_well_file: WellFile
) -> None:
    row_start = METADATA_INSTRUMENT_ROW_START
    curr_sheet.write(row_start, 0, "Device Information:")
    for iter_row, (iter_metadata_uuid, iter_value) in enumerate(
        ((MANTARRAY_SERIAL_NUMBER_UUID, first_well_file.get_mantarray_serial_number()),)
    ):
        row_in_sheet = row_start + 1 + iter_row
        curr_sheet.write(
            row_in_sheet, 1, METADATA_UUID_DESCRIPTIONS[iter_metadata_uuid],
        )
        curr_sheet.write(
            row_in_sheet, 2, iter_value,
        )


def _write_xlsx_recording_metadata(
    curr_sheet: xlsxwriter.worksheet.Worksheet, first_well_file: WellFile
) -> None:
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


def _write_xlsx_metadata(
    workbook: xlsxwriter.workbook.Workbook, first_well_file: WellFile
) -> None:
    metadata_sheet = workbook.add_worksheet(METADATA_EXCEL_SHEET_NAME)
    curr_sheet = metadata_sheet
    _write_xlsx_recording_metadata(curr_sheet, first_well_file)
    _write_xlsx_device_metadata(curr_sheet, first_well_file)
    # Adjust the column widths to be able to see the data
    curr_sheet.set_column(0, 0, 25)
    curr_sheet.set_column(1, 1, 40)
    curr_sheet.set_column(2, 2, 25)


class PlateRecording(FileManagerPlateRecording):
    """Manages aspects of analyzing a plate recording session."""

    def __init__(
        self,
        *args: Any,
        pipeline_template: Optional[PipelineTemplate] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        super().__init__(*args, **kwargs)
        self._workbook: xlsxwriter.workbook.Workbook
        if pipeline_template is None:
            pipeline_template = copy.deepcopy(DEFAULT_PIPELINE_TEMPLATE)
        self._pipeline = pipeline_template.create_pipeline()

    def get_template(self) -> PipelineTemplate:
        return self._pipeline.get_template()

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
        self._workbook = Workbook(
            file_path, {"default_date_format": "YYYY-MM-DD hh:mm:ss UTC"}
        )
        _write_xlsx_metadata(self._workbook, first_well_file)
        self._write_xlsx_continuous_waveforms()
        self._workbook.close()  # This is actually when the file gets written to d

    def _write_xlsx_continuous_waveforms(self) -> None:
        continuous_waveform_sheet = self._workbook.add_worksheet(
            CONTINUOUS_WAVEFORM_SHEET_NAME
        )
        curr_sheet = continuous_waveform_sheet

        # create headings
        curr_sheet.write(0, 0, "Time (seconds)")
        for i in range(
            TWENTY_FOUR_WELL_PLATE.row_count * TWENTY_FOUR_WELL_PLATE.column_count
        ):
            curr_sheet.write(
                0, 1 + i, TWENTY_FOUR_WELL_PLATE.get_well_name_from_well_index(i)
            )

        # initialize time values
        first_well = self.get_well_by_index(self.get_well_indices()[0])
        tissue_sampling_period = first_well.get_tissue_sampling_period_microseconds()
        final_data_index = first_well.get_numpy_array()[0][-1]
        interpolated_data_indices = np.arange(
            0, final_data_index, TSP_TO_INTERPOLATED_DATA_PERIOD[tissue_sampling_period]
        )
        for i, data_index in enumerate(interpolated_data_indices):
            curr_sheet.write(i + 1, 0, data_index)

        # add data for valid wells
        for well_index in self.get_well_indices():
            well = self.get_well_by_index(well_index)
            data = well.get_numpy_array()
            # apply Bessel filter
            self._pipeline.load_raw_gmr_data(data, np.zeros(data.shape))
            filtered_data = self._pipeline.get_noise_filtered_gmr()
            # interpolate data (to 100 Hz)
            interpolated_data_function = interpolate.interp1d(
                filtered_data[0], filtered_data[1]
            )
            interpolated_data = interpolated_data_function(interpolated_data_indices)
            # write to sheet
            for i, data_point in enumerate(interpolated_data):
                curr_sheet.write(i + 1, well_index + 1, data_point)
