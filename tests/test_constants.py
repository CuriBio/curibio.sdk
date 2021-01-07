# -*- coding: utf-8 -*-
from collections import OrderedDict
import uuid

from curibio.sdk import AGGREGATE_METRICS_SHEET_NAME
from curibio.sdk import ALL_FORMATS
from curibio.sdk import CALCULATED_METRIC_DISPLAY_NAMES
from curibio.sdk import CHART_BASE_WIDTH
from curibio.sdk import CHART_FIXED_WIDTH
from curibio.sdk import CHART_FIXED_WIDTH_CELLS
from curibio.sdk import CHART_HEIGHT
from curibio.sdk import CHART_HEIGHT_CELLS
from curibio.sdk import CHART_WINDOW_NUM_DATA_POINTS
from curibio.sdk import CHART_WINDOW_NUM_SECONDS
from curibio.sdk import CONTINUOUS_WAVEFORM_SHEET_NAME
from curibio.sdk import DEFAULT_CELL_WIDTH
from curibio.sdk import EXCEL_OPTICAL_METADATA_CELLS
from curibio.sdk import FREQUENCY_VS_TIME_SHEET_NAME
from curibio.sdk import FULL_CHART_SHEET_NAME
from curibio.sdk import INTERPOLATED_DATA_PERIOD_CMS
from curibio.sdk import INTERPOLATED_DATA_PERIOD_SECONDS
from curibio.sdk import INTERPOLATION_VALUE_UUID
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_INSTRUMENT_ROW_START
from curibio.sdk import METADATA_OUTPUT_FILE_ROW_START
from curibio.sdk import METADATA_RECORDING_ROW_START
from curibio.sdk import METADATA_UUID_DESCRIPTIONS
from curibio.sdk import MICROSECONDS_PER_CENTIMILLISECOND
from curibio.sdk import NUMBER_OF_PER_TWITCH_METRICS
from curibio.sdk import PEAK_VALLEY_COLUMN_START
from curibio.sdk import PER_TWITCH_METRICS_SHEET_NAME
from curibio.sdk import SECONDS_PER_CELL
from curibio.sdk import SNAPSHOT_CHART_SHEET_NAME
from curibio.sdk import TSP_TO_DEFAULT_FILTER_UUID
from curibio.sdk import TWITCHES_POINT_UP_UUID
from mantarray_file_manager import MANTARRAY_SERIAL_NUMBER_UUID
from mantarray_file_manager import PLATE_BARCODE_UUID
from mantarray_file_manager import TISSUE_SAMPLING_PERIOD_UUID
from mantarray_file_manager import UTC_BEGINNING_RECORDING_UUID
from mantarray_file_manager import WELL_NAME_UUID
from mantarray_waveform_analysis import AMPLITUDE_UUID
from mantarray_waveform_analysis import AUC_UUID
from mantarray_waveform_analysis import BESSEL_LOWPASS_10_UUID
from mantarray_waveform_analysis import BUTTERWORTH_LOWPASS_30_UUID
from mantarray_waveform_analysis import CENTIMILLISECONDS_PER_SECOND
from mantarray_waveform_analysis import TWITCH_FREQUENCY_UUID
from mantarray_waveform_analysis import TWITCH_PERIOD_UUID
from mantarray_waveform_analysis import WIDTH_UUID


def test_formats():
    assert ALL_FORMATS == {"CoV": {"num_format": "0.00%"}}


def test_misc():
    assert MICROSECONDS_PER_CENTIMILLISECOND == 10
    assert CALCULATED_METRIC_DISPLAY_NAMES == OrderedDict(
        [
            (TWITCH_PERIOD_UUID, "Twitch Period (seconds)"),
            (TWITCH_FREQUENCY_UUID, "Twitch Frequency (Hz)"),
            (AMPLITUDE_UUID, "Twitch Amplitude"),
            (WIDTH_UUID, (50, "Twitch Width 50 (FWHM) (seconds)")),
            (AUC_UUID, "Twitch Area Under the Curve (AUC)"),
        ]
    )


def test_excel_sheet_names():
    assert METADATA_EXCEL_SHEET_NAME == "metadata"
    assert CONTINUOUS_WAVEFORM_SHEET_NAME == "continuous-waveforms"
    assert AGGREGATE_METRICS_SHEET_NAME == "aggregate-metrics"
    assert PER_TWITCH_METRICS_SHEET_NAME == "per-twitch-metrics"
    assert SNAPSHOT_CHART_SHEET_NAME == "continuous-waveform-snapshots"
    assert FULL_CHART_SHEET_NAME == "full-continuous-waveform-plots"
    assert FREQUENCY_VS_TIME_SHEET_NAME == "frequency-vs-time-plots"


def test_excel_sheet_rows():
    assert METADATA_RECORDING_ROW_START == 0
    assert NUMBER_OF_PER_TWITCH_METRICS == 18
    assert METADATA_INSTRUMENT_ROW_START == METADATA_RECORDING_ROW_START + 4
    assert METADATA_OUTPUT_FILE_ROW_START == METADATA_INSTRUMENT_ROW_START + 6


def test_interpolated_data_period():
    assert INTERPOLATED_DATA_PERIOD_SECONDS == 1 / 100
    assert (
        INTERPOLATED_DATA_PERIOD_CMS
        == INTERPOLATED_DATA_PERIOD_SECONDS * CENTIMILLISECONDS_PER_SECOND
    )


def test_default_filter_dict():
    assert TSP_TO_DEFAULT_FILTER_UUID == {
        960: BESSEL_LOWPASS_10_UUID,
        160: BUTTERWORTH_LOWPASS_30_UUID,
    }


def test_charts():
    assert CHART_HEIGHT == 300
    assert CHART_BASE_WIDTH == 120
    assert CHART_HEIGHT_CELLS == 15
    assert PEAK_VALLEY_COLUMN_START == 100
    assert DEFAULT_CELL_WIDTH == 64
    assert CHART_FIXED_WIDTH == DEFAULT_CELL_WIDTH * CHART_FIXED_WIDTH_CELLS
    assert CHART_FIXED_WIDTH_CELLS == 8
    assert CHART_WINDOW_NUM_SECONDS == 10
    assert (
        CHART_WINDOW_NUM_DATA_POINTS
        == CHART_WINDOW_NUM_SECONDS / INTERPOLATED_DATA_PERIOD_SECONDS
    )
    assert SECONDS_PER_CELL == 2.5


def test_excel_optical_metadata():
    assert TWITCHES_POINT_UP_UUID == uuid.UUID("97f69f56-f1c6-4c50-8590-7332570ed3c5")
    assert INTERPOLATION_VALUE_UUID == uuid.UUID("466d0131-06b7-4f0f-ba1e-062a771cb280")

    assert (
        METADATA_UUID_DESCRIPTIONS[TWITCHES_POINT_UP_UUID]
        == "Flag indicating whether or not the twitches in the data point up or not"
    )
    assert (
        METADATA_UUID_DESCRIPTIONS[INTERPOLATION_VALUE_UUID]
        == "Desired value for optical well data interpolation"
    )

    assert EXCEL_OPTICAL_METADATA_CELLS == {
        WELL_NAME_UUID: "E2",
        UTC_BEGINNING_RECORDING_UUID: "E3",
        PLATE_BARCODE_UUID: "E4",
        TISSUE_SAMPLING_PERIOD_UUID: "E5",
        TWITCHES_POINT_UP_UUID: "E6",
        MANTARRAY_SERIAL_NUMBER_UUID: "E7",
        INTERPOLATION_VALUE_UUID: "E8",
    }
