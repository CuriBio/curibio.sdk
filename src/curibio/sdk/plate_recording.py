# -*- coding: utf-8 -*-
"""Docstring."""
import datetime
import logging
import os
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union
import uuid
import zipfile

from mantarray_file_manager import MAIN_FIRMWARE_VERSION_UUID
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
from mantarray_waveform_analysis import Pipeline
from mantarray_waveform_analysis import PipelineTemplate
from mantarray_waveform_analysis import TooFewPeaksDetectedError
from mantarray_waveform_analysis import TWITCH_PERIOD_UUID
from mantarray_waveform_analysis import TwoPeaksInARowError
from mantarray_waveform_analysis import TwoValleysInARowError
from mantarray_waveform_analysis import WIDTH_UUID
from mantarray_waveform_analysis.exceptions import PeakDetectionError
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from nptyping import NDArray
import numpy as np
from scipy import interpolate
from stdlib_utils import configure_logging
import xlsxwriter
from xlsxwriter import Workbook
from xlsxwriter.format import Format
from xlsxwriter.utility import xl_col_to_name

from .constants import AGGREGATE_METRICS_SHEET_NAME
from .constants import ALL_FORMATS
from .constants import CALCULATED_METRIC_DISPLAY_NAMES
from .constants import CHART_FIXED_WIDTH
from .constants import CHART_FIXED_WIDTH_CELLS
from .constants import CHART_HEIGHT
from .constants import CHART_HEIGHT_CELLS
from .constants import CHART_WINDOW_NUM_DATA_POINTS
from .constants import CONTINUOUS_WAVEFORM_SHEET_NAME
from .constants import INTERPOLATED_DATA_PERIOD_CMS
from .constants import METADATA_EXCEL_SHEET_NAME
from .constants import METADATA_INSTRUMENT_ROW_START
from .constants import METADATA_OUTPUT_FILE_ROW_START
from .constants import METADATA_RECORDING_ROW_START
from .constants import MICROSECONDS_PER_CENTIMILLISECOND
from .constants import PACKAGE_VERSION
from .constants import PEAK_VALLEY_COLUMN_START
from .constants import TSP_TO_DEFAULT_FILTER_UUID
from .constants import TWENTY_FOUR_WELL_PLATE
from .constants import WAVEFORM_CHART_SHEET_NAME
from .excel_well_file import ExcelWellFile

logger = logging.getLogger(__name__)
configure_logging(logging_format="notebook")


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
                MAIN_FIRMWARE_VERSION_UUID,
                first_well_file.get_h5_attribute(str(MAIN_FIRMWARE_VERSION_UUID)),
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
            row_in_sheet,
            1,
            METADATA_UUID_DESCRIPTIONS[iter_metadata_uuid],
        )
        curr_sheet.write(
            row_in_sheet,
            2,
            iter_value,
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
            row_in_sheet,
            1,
            METADATA_UUID_DESCRIPTIONS[iter_metadata_uuid],
        )
        if isinstance(iter_value, datetime.datetime):
            # Excel doesn't support timezones in datetimes
            iter_value = iter_value.replace(tzinfo=None)
        curr_sheet.write(
            row_in_sheet,
            2,
            iter_value,
        )


def _write_xlsx_metadata(
    workbook: xlsxwriter.workbook.Workbook, first_well_file: WellFile
) -> None:
    logger.info("Writing H5 file metadata")
    metadata_sheet = workbook.add_worksheet(METADATA_EXCEL_SHEET_NAME)
    curr_sheet = metadata_sheet
    _write_xlsx_recording_metadata(curr_sheet, first_well_file)
    if not isinstance(first_well_file, ExcelWellFile):
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
        self._is_optical_recording = isinstance(self._files[0], ExcelWellFile)
        self._workbook: xlsxwriter.workbook.Workbook
        self._workbook_formats: Dict[str, Format] = dict()
        if pipeline_template is None:
            first_well_index = self.get_well_indices()[0]
            # this file is used to get general information applicable across the recording
            first_well_file = self.get_well_by_index(first_well_index)
            tissue_sampling_period = (
                first_well_file.get_tissue_sampling_period_microseconds()
                / MICROSECONDS_PER_CENTIMILLISECOND
            )
            noise_filter_uuid = (
                None
                if self._is_optical_recording
                else TSP_TO_DEFAULT_FILTER_UUID[tissue_sampling_period]
            )
            pipeline_template = PipelineTemplate(
                tissue_sampling_period=tissue_sampling_period,
                noise_filter_uuid=noise_filter_uuid,
            )
        self._pipeline_template = pipeline_template
        self._pipelines: Dict[int, Pipeline]

    @classmethod
    def from_directory(cls, dir_to_load_files_from: str) -> "PlateRecording":
        first_item = os.listdir(dir_to_load_files_from)[0]
        if first_item.endswith(".zip"):
            path_to_zip_file = os.path.join(dir_to_load_files_from, first_item)
            with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
                members = [
                    member
                    for member in zip_ref.namelist()
                    if (member.endswith(".h5") or member.endswith(".xlsx"))
                    and "__MACOSX" not in member
                    # Tanner (10/1/20): "__MACOSX" is an artifact of zipping a file on MacOS that is not needed by the SDK. This is likely not a typically use case, but this gaurds against in case a user does zip their files on Mac
                ]
                path_sep = "/"  # Tanner (10/7/20): When zipfile unzips files, it always uses the unix style separator in the names of members
                zip_contains_folder = all(path_sep in member for member in members)
                zip_ref.extractall(dir_to_load_files_from, members=members)
            if zip_contains_folder:
                unzipped_dir_to_load_files_from = os.path.join(
                    dir_to_load_files_from, os.path.dirname(members[0])
                )
                return cls.from_directory(unzipped_dir_to_load_files_from)
            if members[0].endswith(".xlsx"):
                optical_well_files = [
                    ExcelWellFile(os.path.join(dir_to_load_files_from, member))
                    for member in members
                ]
                return cls(optical_well_files)
        if first_item.endswith(".xlsx"):
            optical_well_files = [
                ExcelWellFile(os.path.join(dir_to_load_files_from, item))
                for item in os.listdir(dir_to_load_files_from)
                if item.endswith(".xlsx")
            ]
            return cls(optical_well_files)
        return super().from_directory(dir_to_load_files_from)  # type: ignore # Tanner (10/1/20): Not sure why mypy doesn't see the super class method's return type

    def _init_pipelines(self) -> None:
        try:
            self._pipelines  # pylint:disable=pointless-statement # Eli (9/11/20): this will cause the attribute error to be raised if the pipelines haven't yet been initialized
            return
        except AttributeError:
            pass
        self._pipelines = dict()
        num_wells = len(self.get_well_indices())
        for i, iter_well_idx in enumerate(self.get_well_indices()):
            iter_pipeline = self.get_pipeline_template().create_pipeline()
            well = self.get_well_by_index(iter_well_idx)
            well_name = TWENTY_FOUR_WELL_PLATE.get_well_name_from_well_index(
                iter_well_idx
            )
            msg = f"Loading tissue and reference data... {int(round(i / 24, 2) * 100)}% (Well {well_name}, {i + 1} out of {num_wells})"
            logger.info(msg)
            raw_tissue_reading = well.get_raw_tissue_reading()
            if self._is_optical_recording:
                raw_tissue_reading[0] *= CENTIMILLISECONDS_PER_SECOND
            iter_pipeline.load_raw_magnetic_data(
                raw_tissue_reading,
                well.get_raw_reference_reading(),
            )
            self._pipelines[iter_well_idx] = iter_pipeline

    def get_pipeline_template(self) -> PipelineTemplate:
        return self._pipeline_template

    def get_reference_magnetic_data(self, well_idx: int) -> NDArray[(2, Any), int]:
        self._init_pipelines()
        return self._pipelines[well_idx].get_raw_reference_magnetic_data()

    def create_stacked_plot(self) -> Figure:
        """Create a stacked plot of all wells in the recording."""
        # Note Eli (9/11/20): this is hardcoded for a very specific use case at the moment and just visually tested using the newly evolving visual regression tool
        self._init_pipelines()
        factor = 0.25
        plt.figure(figsize=(15 * factor, 35 * 1), dpi=300)
        ax1 = plt.subplot(24, 1, 1)
        ax1.set(ylabel="A1")
        plt.setp(ax1.get_xticklabels(), visible=False)
        count = 0
        for _, iter_pipeline in self._pipelines.items():
            if count == 0:
                pass
            else:
                iter_ax = plt.subplot(24, 1, count + 1, sharex=ax1)
                iter_ax.set(
                    ylabel=TWENTY_FOUR_WELL_PLATE.get_well_name_from_well_index(count)
                )
                if count != 23:
                    plt.setp(iter_ax.get_xticklabels(), visible=False)
                else:
                    iter_ax.set(xlabel="Time (seconds)")
            filtered_data = iter_pipeline.get_noise_filtered_magnetic_data()
            plt.plot(
                filtered_data[0] / CENTIMILLISECONDS_PER_SECOND,
                filtered_data[1],
                linewidth=0.5,
            )
            # plt.plot(filtered_data[0,:int(30*CENTIMILLISECONDS_PER_SECOND/960)]/CENTIMILLISECONDS_PER_SECOND,filtered_data[1,:int(30*CENTIMILLISECONDS_PER_SECOND/960)])
            count += 1
        return plt.gcf()

    def write_xlsx(
        self,
        file_dir: str,
        file_name: Optional[str] = None,
        create_continuous_waveforms: bool = True,
        create_waveform_charts: bool = True,
    ) -> None:
        """Create an XLSX file.

        Args:
            file_dir: the directory in which to create the file.
            file_name: By default an automatic name is generated based on barcode and recording date. Extension will always be xlsx---if user provides something else then it is stripped
            create_continuous_waveforms: typically used in unit testing, if set to True, the continuous-waveforms sheet and continuous-waveform-plots sheet will be created with no content
            create_waveform_charts: typically used in unit testing, if set to True, only the continuous-waveform-plots sheet will be created with no content
        """
        first_well_index = self.get_well_indices()[0]
        # this file is used to get general information applicable across the recording
        first_well_file = self.get_well_by_index(first_well_index)
        logger.info("Loading data from H5 file(s)")
        self._init_pipelines()
        if file_name is None:
            file_name = f"{first_well_file.get_plate_barcode()}-{first_well_file.get_begin_recording().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx"
        file_path = os.path.join(file_dir, file_name)
        logger.info("Opening .xlsx file")
        self._workbook = Workbook(
            file_path, {"default_date_format": "YYYY-MM-DD hh:mm:ss UTC"}
        )
        for iter_format_name, iter_format in ALL_FORMATS.items():
            self._workbook_formats[iter_format_name] = self._workbook.add_format(
                iter_format
            )
        _write_xlsx_metadata(self._workbook, first_well_file)
        self._write_xlsx_continuous_waveforms(
            skip_content=(not create_continuous_waveforms),
            skip_charts=(not create_waveform_charts),
        )
        self._write_xlsx_aggregate_metrics()
        logger.info("Saving .xlsx file")
        self._workbook.close()  # This is actually when the file gets written to d
        logger.info("Done writing to .xlsx")

    def _write_xlsx_continuous_waveforms(
        self,
        skip_content: bool = False,
        skip_charts: bool = False,
    ) -> None:
        continuous_waveform_sheet = self._workbook.add_worksheet(
            CONTINUOUS_WAVEFORM_SHEET_NAME
        )
        self._workbook.add_worksheet(WAVEFORM_CHART_SHEET_NAME)
        if skip_content:
            return
        logger.info("Creating waveform data sheet")

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
        max_time_index = 0
        for well_index in self.get_well_indices():
            well_pipeline = self._pipelines[well_index]
            last_time_index = well_pipeline.get_raw_tissue_magnetic_data()[0][-1]
            if last_time_index > max_time_index:
                max_time_index = last_time_index
        interpolated_data_period = (
            int(self._files[0].get_interpolation_value() / 10)
            if self._is_optical_recording
            else INTERPOLATED_DATA_PERIOD_CMS
        )
        interpolated_data_indices = np.arange(
            interpolated_data_period,  # don't start at time zero, because some wells don't have data at exactly zero (causing interpolation to fail), so just start at the next timepoint
            max_time_index,
            interpolated_data_period,
        )
        for i, data_index in enumerate(interpolated_data_indices):
            curr_sheet.write(
                i + 1,
                0,
                data_index
                / CENTIMILLISECONDS_PER_SECOND,  # display in seconds in the Excel sheet
            )

        # add data for valid wells
        well_indices = self.get_well_indices()
        num_wells = len(well_indices)
        for iter_well_idx, well_index in enumerate(well_indices):
            filtered_data = self._pipelines[
                well_index
            ].get_noise_filtered_magnetic_data()
            # interpolate data (at 100 Hz for H5) to max valid interpolated data point
            interpolated_data_function = interpolate.interp1d(
                filtered_data[0], filtered_data[1]
            )

            well_name = TWENTY_FOUR_WELL_PLATE.get_well_name_from_well_index(well_index)
            msg = f"Writing waveform data of well {well_name} ({iter_well_idx + 1} out of {num_wells})"
            logger.info(msg)
            last_index = len(interpolated_data_indices)
            first_index = 0
            if filtered_data[0][-1] < interpolated_data_indices[-1]:
                last_index -= 1
            while filtered_data[0][0] > interpolated_data_indices[first_index]:
                first_index += 1
            interpolated_data = interpolated_data_function(
                interpolated_data_indices[first_index:last_index]
            )
            # write to sheet
            for i, data_point in enumerate(interpolated_data):
                curr_sheet.write(i + 1, well_index + 1, data_point)
            if skip_charts:
                continue
            self._create_waveform_chart(
                last_index,
                well_index,
                well_name,
                filtered_data[0],
                interpolated_data_function,
            )

        # The formatting items below are not explicitly unit-tested...not sure the best way to do this
        # Adjust the column widths to be able to see the data
        curr_sheet.set_column(0, 0, 18)
        well_indices = self.get_well_indices()
        for iter_well_idx in range(24):
            curr_sheet.set_column(
                iter_well_idx + 1,
                iter_well_idx + 1,
                13,
                options={"hidden": iter_well_idx not in well_indices},
            )
        curr_sheet.freeze_panes(1, 1)

    def _create_waveform_chart(
        self,
        num_data_points: int,
        well_index: int,
        well_name: str,
        time_values: NDArray[(2, Any), int],
        interpolated_data_function: interpolate.interpolate.interp1d,
    ) -> None:
        waveform_chart_sheet = self._workbook.get_worksheet_by_name(
            WAVEFORM_CHART_SHEET_NAME
        )

        msg = f"Creating chart of waveform data of well {well_name}"
        logger.info(msg)
        waveform_chart = self._workbook.add_chart({"type": "line"})
        well_column = xl_col_to_name(well_index + 1)
        first_chart_data_point = (
            2
            if num_data_points <= CHART_WINDOW_NUM_DATA_POINTS
            else int((num_data_points - CHART_WINDOW_NUM_DATA_POINTS) // 2)
        )
        last_chart_data_point = (
            num_data_points + 1
            if num_data_points <= CHART_WINDOW_NUM_DATA_POINTS
            else int((num_data_points + CHART_WINDOW_NUM_DATA_POINTS) // 2)
        )
        waveform_chart.add_series(
            {
                "name": "Waveform Data",
                "categories": f"='continuous-waveforms'!$A${first_chart_data_point}:$A${last_chart_data_point}",
                "values": f"='continuous-waveforms'!${well_column}${first_chart_data_point}:${well_column}${last_chart_data_point}",
                "line": {"color": "#1B9E77"},
            }
        )

        msg = f"Adding peak and valley markers to chart of well {well_name}"
        logger.info(msg)
        peak_indices, valley_indices = self._pipelines[
            well_index
        ].get_peak_detection_results()
        peak_detection_chart = self._workbook.add_chart({"type": "scatter"})
        self._add_peak_detection_chart_series(
            peak_detection_chart,
            "Peak",
            well_index,
            well_name,
            (first_chart_data_point, last_chart_data_point),
            peak_indices,
            interpolated_data_function,
            time_values,
        )
        self._add_peak_detection_chart_series(
            peak_detection_chart,
            "Valley",
            well_index,
            well_name,
            (first_chart_data_point, last_chart_data_point),
            valley_indices,
            interpolated_data_function,
            time_values,
        )
        waveform_chart.combine(peak_detection_chart)

        well_row, well_col = TWENTY_FOUR_WELL_PLATE.get_row_and_column_from_well_index(
            well_index
        )
        waveform_chart.set_x_axis({"name": "Time (seconds)", "interval_tick": 100})
        waveform_chart.set_y_axis(
            {"name": "Magnetic Sensor Data", "major_gridlines": {"visible": 0}}
        )
        waveform_chart.set_size({"width": CHART_FIXED_WIDTH, "height": CHART_HEIGHT})
        waveform_chart.set_title({"name": f"Well {well_name}"})

        waveform_chart_sheet.insert_chart(
            1 + well_row * (CHART_HEIGHT_CELLS + 1),
            1 + well_col * (CHART_FIXED_WIDTH_CELLS + 1),
            waveform_chart,
        )

    def _add_peak_detection_chart_series(
        self,
        peak_detection_chart: xlsxwriter.chart_scatter.ChartScatter,
        detector_type: str,
        well_index: int,
        well_name: str,
        data_start_stop: Tuple[int, int],
        indices: NDArray[(1, Any), int],
        interpolated_data_function: interpolate.interpolate.interp1d,
        time_values: NDArray[(2, Any), int],
    ) -> None:
        label = "Relaxation" if detector_type == "Valley" else "Contraction"
        offset = 1 if detector_type == "Valley" else 0
        marker_color = "#D95F02" if detector_type == "Valley" else "#7570B3"
        continuous_waveform_sheet = self._workbook.get_worksheet_by_name(
            CONTINUOUS_WAVEFORM_SHEET_NAME
        )

        # index_column = xl_col_to_name(
        #     PEAK_VALLEY_COLUMN_START + (well_index * 2) + offset
        # )
        result_column = xl_col_to_name(
            PEAK_VALLEY_COLUMN_START + (well_index * 2) + offset
        )
        # continuous_waveform_sheet.write(
        #     f"{index_column}1", f"{well_name} {detector_type} Timepoints"
        # )
        continuous_waveform_sheet.write(
            f"{result_column}1", f"{well_name} {detector_type} Values"
        )
        for idx in indices:
            interpolated_time_value = round(
                time_values[idx] / CENTIMILLISECONDS_PER_SECOND, 2
            )
            continuous_waveform_sheet.write(
                f"{result_column}{interpolated_time_value * 100 + 1}",
                interpolated_data_function(
                    interpolated_time_value * CENTIMILLISECONDS_PER_SECOND
                ),
            )
        peak_detection_chart.add_series(
            {
                "name": label,
                "categories": "=",
                "values": f"='continuous-waveforms'!${result_column}${data_start_stop[0]}:${result_column}${data_start_stop[1]}",
                "marker": {
                    "type": "circle",
                    "size": 8,
                    "border": {"color": marker_color, "width": 1.5},
                    "fill": {"none": True},
                },
            }
        )

    def _write_xlsx_aggregate_metrics(self) -> None:
        logger.info("Creating aggregate metrics sheet")
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
        well_indices = self.get_well_indices()
        for iter_well_idx in well_indices:
            iter_pipeline = self._pipelines[iter_well_idx]
            error_msg = ""
            try:
                _, aggregate_metrics_dict = iter_pipeline.get_magnetic_data_metrics()
            except PeakDetectionError as e:
                error_msg = "Error: "
                if isinstance(e, TwoPeaksInARowError):
                    error_msg += "Two Contractions in a Row Detected"
                elif isinstance(e, TwoValleysInARowError):
                    error_msg += "Two Relaxations in a Row Detected"
                elif isinstance(e, TooFewPeaksDetectedError):
                    error_msg += "Not Enough Twitches Detected"
                else:
                    raise NotImplementedError("Unknown PeakDetectionError") from e
                curr_sheet.write(curr_row, 2 + iter_well_idx, "N/A")
                curr_sheet.write(curr_row + 1, 2 + iter_well_idx, error_msg)
            else:
                curr_sheet.write(
                    curr_row,
                    2 + iter_well_idx,
                    aggregate_metrics_dict[AMPLITUDE_UUID]["n"],
                )

        curr_row += 1
        # row_where_data_starts=curr_row
        for (
            iter_metric_uuid,
            iter_metric_name,
        ) in CALCULATED_METRIC_DISPLAY_NAMES.items():
            curr_row += 1
            new_row = self._write_submetrics(
                curr_sheet,
                curr_row,
                iter_metric_uuid,
                iter_metric_name,
            )
            curr_row = new_row

        # The formatting items below are not explicitly unit-tested...not sure the best way to do this
        # Adjust the column widths to be able to see the data
        for iter_column_idx, iter_column_width in ((0, 40), (1, 25)):
            curr_sheet.set_column(iter_column_idx, iter_column_idx, iter_column_width)
        # adjust widths of well columns
        for iter_column_idx in range(24):
            curr_sheet.set_column(
                iter_column_idx + 2,
                iter_column_idx + 2,
                19,
                options={"hidden": iter_column_idx not in well_indices},
            )
        curr_sheet.freeze_panes(2, 2)

    def _write_submetrics(
        self,
        curr_sheet: xlsxwriter.worksheet.Worksheet,
        curr_row: int,
        iter_metric_uuid: uuid.UUID,
        iter_metric_name: Union[str, Tuple[int, str]],
    ) -> int:
        submetrics = ("Mean", "StDev", "CoV", "SEM")
        if isinstance(iter_metric_name, tuple):
            iter_width_percent, iter_metric_name = iter_metric_name
        curr_sheet.write(curr_row, 0, iter_metric_name)
        for iter_sub_metric_name in submetrics:
            msg = f"Writing {iter_sub_metric_name} of {iter_metric_name}"
            logger.info(msg)
            curr_sheet.write(curr_row, 1, iter_sub_metric_name)
            well_indices = self.get_well_indices()
            for well_index in well_indices:
                value_to_write: Optional[Union[float, int, str]] = None
                cell_format: Optional[Format] = None
                iter_pipeline = self._pipelines[well_index]

                try:
                    (
                        _,
                        aggregate_metrics_dict,
                    ) = iter_pipeline.get_magnetic_data_metrics()
                except PeakDetectionError:
                    value_to_write = "N/A"
                else:
                    metrics_dict = dict()
                    if iter_metric_uuid == WIDTH_UUID:
                        metrics_dict = aggregate_metrics_dict[iter_metric_uuid][
                            iter_width_percent
                        ]
                    else:
                        metrics_dict = aggregate_metrics_dict[iter_metric_uuid]
                    if iter_sub_metric_name == "Mean":
                        value_to_write = metrics_dict["mean"]
                    elif iter_sub_metric_name == "StDev":
                        value_to_write = metrics_dict["std"]
                    elif iter_sub_metric_name == "CoV":
                        value_to_write = metrics_dict["std"] / metrics_dict["mean"]
                        cell_format = self._workbook_formats["CoV"]
                    elif iter_sub_metric_name == "SEM":
                        value_to_write = metrics_dict["std"] / metrics_dict["n"] ** 0.5
                    else:
                        raise NotImplementedError(
                            f"Unrecognized submetric name: {iter_sub_metric_name}"
                        )

                    if iter_metric_uuid in (
                        TWITCH_PERIOD_UUID,
                        WIDTH_UUID,
                    ):  # for time-based metrics, convert from centi-milliseconds to seconds before writing to Excel
                        if (
                            iter_sub_metric_name != "CoV"
                        ):  # coefficients of variation are %, not a raw time unit
                            value_to_write /= CENTIMILLISECONDS_PER_SECOND
                curr_sheet.write(curr_row, 2 + well_index, value_to_write, cell_format)

            curr_row += 1
        return curr_row
