# -*- coding: utf-8 -*-
from collections import OrderedDict

from curibio.sdk import AGGREGATE_METRICS_SHEET_NAME
from curibio.sdk import CALCULATED_METRIC_DISPLAY_NAMES
from curibio.sdk import CONTINUOUS_WAVEFORM_SHEET_NAME
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_INSTRUMENT_ROW_START
from curibio.sdk import METADATA_OUTPUT_FILE_ROW_START
from curibio.sdk import METADATA_RECORDING_ROW_START
from curibio.sdk import MICROSECONDS_PER_CENTIMILLISECOND
from curibio.sdk import TSP_TO_DEFAULT_FILTER_UUID
from curibio.sdk import TSP_TO_INTERPOLATED_DATA_PERIOD
from mantarray_waveform_analysis import AMPLITUDE_UUID
from mantarray_waveform_analysis import BESSEL_LOWPASS_10_UUID
from mantarray_waveform_analysis import BESSEL_LOWPASS_30_UUID
from mantarray_waveform_analysis import TWITCH_PERIOD_UUID


def test_misc():
    assert MICROSECONDS_PER_CENTIMILLISECOND == 10
    assert CALCULATED_METRIC_DISPLAY_NAMES == OrderedDict(
        [
            (TWITCH_PERIOD_UUID, "Twitch Period (seconds)"),
            (AMPLITUDE_UUID, "Twitch Amplitude"),
        ]
    )


def test_excel_sheet_names():
    assert METADATA_EXCEL_SHEET_NAME == "metadata"
    assert CONTINUOUS_WAVEFORM_SHEET_NAME == "continuous-waveforms"
    assert AGGREGATE_METRICS_SHEET_NAME == "aggregate-metrics"


def test_excel_sheet_rows():
    assert METADATA_RECORDING_ROW_START == 0
    assert METADATA_INSTRUMENT_ROW_START == METADATA_RECORDING_ROW_START + 4
    assert METADATA_OUTPUT_FILE_ROW_START == METADATA_INSTRUMENT_ROW_START + 6


def test_interpolated_data_period_dict():
    assert TSP_TO_INTERPOLATED_DATA_PERIOD == {
        960: 1000,
        160: 160,
    }


def test_default_filter_dict():
    assert TSP_TO_DEFAULT_FILTER_UUID == {
        960: BESSEL_LOWPASS_10_UUID,
        160: BESSEL_LOWPASS_30_UUID,
    }
