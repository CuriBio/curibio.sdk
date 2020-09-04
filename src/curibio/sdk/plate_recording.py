# -*- coding: utf-8 -*-
"""Docstring."""
import datetime
import os
from typing import Any
from typing import Dict
from typing import Optional

from mantarray_file_manager import MANTARRAY_SERIAL_NUMBER_UUID
from mantarray_file_manager import METADATA_UUID_DESCRIPTIONS
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import PlateRecording as FileManagerPlateRecording
from mantarray_file_manager import SOFTWARE_BUILD_NUMBER_UUID
from mantarray_file_manager import SOFTWARE_RELEASE_VERSION_UUID
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from mantarray_file_manager import WellFile
from mantarray_waveform_analysis import AMPLITUDE_UUID
from mantarray_waveform_analysis import CENTIMILLISECONDS_PER_SECOND
from mantarray_waveform_analysis import peak_detection
from mantarray_waveform_analysis import peak_detector
from mantarray_waveform_analysis import Pipeline
from mantarray_waveform_analysis import PipelineTemplate
import numpy as np
from scipy import interpolate
import xlsxwriter
from xlsxwriter import Workbook

from .constants import AGGREGATE_METRICS_SHEET_NAME
from .constants import CALCULATED_METRIC_DISPLAY_NAMES
from .constants import CONTINUOUS_WAVEFORM_SHEET_NAME
from .constants import METADATA_EXCEL_SHEET_NAME
from .constants import METADATA_INSTRUMENT_ROW_START
from .constants import METADATA_OUTPUT_FILE_ROW_START
from .constants import METADATA_RECORDING_ROW_START
from .constants import MICROSECONDS_PER_CENTIMILLISECOND
from .constants import PACKAGE_VERSION
from .constants import TSP_TO_DEFAULT_FILTER_UUID
from .constants import TSP_TO_INTERPOLATED_DATA_PERIOD
from .constants import TWENTY_FOUR_WELL_PLATE


def _write_xlsx_device_metadata(
    curr_sheet: xlsxwriter.worksheet.Worksheet, first_well_file: WellFile
) -> None:
    curr_row = METADATA_INSTRUMENT_ROW_START
    curr_sheet.write(curr_row, 0, "Device Information:")
    curr_row += 1
    curr_sheet.write(curr_row, 1, "H5 File Layout Version")
    curr_sheet.write(
        curr_row, 2, first_well_file.get_h5_attribute("File Format Version")
    )
    curr_row += 1
    for iter_row, (iter_metadata_uuid, iter_value) in enumerate(
        (
            (
                MANTARRAY_SERIAL_NUMBER_UUID,
                first_well_file.get_mantarray_serial_number(),
            ),
            (
                SOFTWARE_RELEASE_VERSION_UUID,
                first_well_file.get_h5_attribute(str(SOFTWARE_RELEASE_VERSION_UUID)),
            ),
            (
                SOFTWARE_BUILD_NUMBER_UUID,
                first_well_file.get_h5_attribute(str(SOFTWARE_BUILD_NUMBER_UUID)),
            ),
        )
    ):
        row_in_sheet = curr_row + iter_row
        curr_sheet.write(
            row_in_sheet, 1, METADATA_UUID_DESCRIPTIONS[iter_metadata_uuid],
        )
        curr_sheet.write(
            row_in_sheet, 2, iter_value,
        )


def _write_xlsx_output_format_metadata(
    curr_sheet: xlsxwriter.worksheet.Worksheet,
) -> None:
    curr_row = METADATA_OUTPUT_FILE_ROW_START
    curr_sheet.write(curr_row, 0, "Output Format:")
    curr_row += 1
    curr_sheet.write(curr_row, 1, "SDK Version")
    curr_sheet.write(curr_row, 2, PACKAGE_VERSION)
    curr_row += 1
    curr_sheet.write(curr_row, 1, "File Creation Timestamp")
    curr_sheet.write(curr_row, 2, datetime.datetime.utcnow().replace(microsecond=0))


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
    _write_xlsx_output_format_metadata(curr_sheet)
    # Adjust the column widths to be able to see the data
    for iter_column_idx, iter_column_width in ((0, 25), (1, 40), (2, 25)):
        curr_sheet.set_column(iter_column_idx, iter_column_idx, iter_column_width)


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
            first_well_index = self.get_well_indices()[0]
            # this file is used to get general information applicable across the recording
            first_well_file = self.get_well_by_index(first_well_index)
            tissue_sampling_period = (
                first_well_file.get_tissue_sampling_period_microseconds()
                / MICROSECONDS_PER_CENTIMILLISECOND
            )
            pipeline_template = PipelineTemplate(
                tissue_sampling_period=tissue_sampling_period,
                noise_filter_uuid=TSP_TO_DEFAULT_FILTER_UUID[tissue_sampling_period],
            )
        self._pipeline_template = pipeline_template
        self._pipelines: Dict[int, Pipeline]

    def _init_pipelines(self) -> None:
        self._pipelines = dict()
        for iter_well_idx in self.get_well_indices():
            iter_pipeline = self.get_pipeline_template().create_pipeline()
            well = self.get_well_by_index(iter_well_idx)
            # data = well.get_numpy_array()
            data = well.get_raw_tissue_reading()
            iter_pipeline.load_raw_gmr_data(data, np.zeros(data.shape))
            self._pipelines[iter_well_idx] = iter_pipeline

    def get_pipeline_template(self) -> PipelineTemplate:
        return self._pipeline_template

    def write_xlsx(self, file_dir: str, file_name: Optional[str] = None) -> None:
        """Create an XLSX file.

        Args:
            file_dir: the directory in which to create the file.
            file_name: By default an automatic name is generated based on barcode and recording date. Extension will always be xlsx---if user provides something else then it is stripped
        """
        first_well_index = self.get_well_indices()[0]
        # this file is used to get general information applicable across the recording
        first_well_file = self.get_well_by_index(first_well_index)
        self._init_pipelines()
        if file_name is None:
            file_name = f"{first_well_file.get_plate_barcode()}-{first_well_file.get_begin_recording().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx"
        file_path = os.path.join(file_dir, file_name)
        self._workbook = Workbook(
            file_path, {"default_date_format": "YYYY-MM-DD hh:mm:ss UTC"}
        )
        _write_xlsx_metadata(self._workbook, first_well_file)
        self._write_xlsx_continuous_waveforms()
        self._write_xlsx_aggregate_metrics()
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

        # initialize time values (use longest data)
        first_well = self.get_well_by_index(self.get_well_indices()[0])
        tissue_sampling_period = (
            first_well.get_tissue_sampling_period_microseconds()
            / MICROSECONDS_PER_CENTIMILLISECOND
        )
        max_time_index = 0
        for well_index in self.get_well_indices():
            well = self.get_well_by_index(well_index)
            last_time_index = well.get_raw_tissue_reading()[0][-1]
            if last_time_index > max_time_index:
                max_time_index = last_time_index
        interpolated_data_indices = np.arange(
            TSP_TO_INTERPOLATED_DATA_PERIOD[
                tissue_sampling_period
            ],  # don't start at time zero, because some wells don't have data at exactly zero (causing interpolation to fail), so just start at the next timepoint
            max_time_index,
            TSP_TO_INTERPOLATED_DATA_PERIOD[tissue_sampling_period],
        )
        for i, data_index in enumerate(interpolated_data_indices):
            curr_sheet.write(
                i + 1,
                0,
                data_index
                / CENTIMILLISECONDS_PER_SECOND,  # display in seconds in the Excel sheet
            )

        # add data for valid wells
        for well_index in self.get_well_indices():
            filtered_data = self._pipelines[well_index].get_noise_filtered_gmr()
            # interpolate data (at 100 Hz) to max valid interpolated data point
            interpolated_data_function = interpolate.interp1d(
                filtered_data[0], filtered_data[1]
            )
            for i, time_index in enumerate(np.flip(interpolated_data_indices)):
                if filtered_data[0][-1] >= time_index:
                    break
            else:
                raise NotImplementedError(
                    "There should be at least one valid data point when interpolating"
                )
            last_index = len(interpolated_data_indices) - i
            interpolated_data = interpolated_data_function(
                interpolated_data_indices[:last_index]
            )
            # write to sheet
            for i, data_point in enumerate(interpolated_data):
                curr_sheet.write(i + 1, well_index + 1, data_point)

    def _write_xlsx_aggregate_metrics(self) -> None:
        aggregate_metrics_sheet = self._workbook.add_worksheet(
            AGGREGATE_METRICS_SHEET_NAME
        )
        curr_row = 0
        curr_sheet = aggregate_metrics_sheet
        for iter_well_idx in range(
            TWENTY_FOUR_WELL_PLATE.row_count * TWENTY_FOUR_WELL_PLATE.column_count
        ):
            curr_sheet.write(
                curr_row,
                2 + iter_well_idx,
                TWENTY_FOUR_WELL_PLATE.get_well_name_from_well_index(iter_well_idx),
            )
        curr_row += 1
        curr_sheet.write(curr_row, 1, "Treatment Description")
        curr_row += 1
        curr_sheet.write(curr_row, 1, "n (twitches)")
        for iter_well_idx in self.get_well_indices():
            iter_pipeline = self._pipelines[iter_well_idx]
            magnetic_sensor_data = iter_pipeline.get_noise_filtered_gmr()

            peak_and_valley_timepoints = peak_detector(
                magnetic_sensor_data, twitches_point_up=False
            )
            _, aggregate_metrics_dict = peak_detection.data_metrics(
                peak_and_valley_timepoints, magnetic_sensor_data
            )
            curr_sheet.write(
                curr_row, 2 + iter_well_idx, aggregate_metrics_dict[AMPLITUDE_UUID]["n"]
            )

        curr_row += 1
        # row_where_data_starts=curr_row
        sub_metrics = ("Mean", "StDev", "CoV", "SEM")
        for (_, iter_metric_name,) in CALCULATED_METRIC_DISPLAY_NAMES.items():
            if isinstance(iter_metric_name, tuple):
                _, iter_metric_name = iter_metric_name
            curr_sheet.write(curr_row, 0, iter_metric_name)
            for iter_sub_metric_name in sub_metrics:
                curr_sheet.write(curr_row, 1, iter_sub_metric_name)
                for iter_well_idx in self.get_well_indices():
                    iter_pipeline = self._pipelines[iter_well_idx]
                    magnetic_sensor_data = iter_pipeline.get_noise_filtered_gmr()

                    peak_and_valley_timepoints = peak_detector(
                        magnetic_sensor_data, twitches_point_up=False
                    )

                    _, aggregate_metrics_dict = peak_detection.data_metrics(
                        peak_and_valley_timepoints, magnetic_sensor_data
                    )

                curr_row += 1

        # The formatting items below are not explicitly unit-tested...not sure the best way to do this
        # Adjust the column widths to be able to see the data
        for iter_column_idx, iter_column_width in ((0, 40), (1, 25)):
            curr_sheet.set_column(iter_column_idx, iter_column_idx, iter_column_width)
        # adjust widths of well columns
        for iter_column_idx in range(2, 2 + 24):
            curr_sheet.set_column(iter_column_idx, iter_column_idx, 19)
        curr_sheet.freeze_panes(2, 2)
