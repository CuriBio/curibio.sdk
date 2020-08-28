# -*- coding: utf-8 -*-
from curibio.sdk import CONTINUOUS_WAVEFORM_SHEET_NAME
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_INSTRUMENT_ROW_START
from curibio.sdk import METADATA_RECORDING_ROW_START
from curibio.sdk import TSP_TO_INTERPOLATED_DATA_PERIOD


def test_excel_sheet_names():
    assert METADATA_EXCEL_SHEET_NAME == "recording-information"
    assert CONTINUOUS_WAVEFORM_SHEET_NAME == "continuous-waveforms"


def test_excel_sheet_rows():
    assert METADATA_RECORDING_ROW_START == 0
    assert METADATA_INSTRUMENT_ROW_START == METADATA_RECORDING_ROW_START + 4


def test_interpolated_data_period_dict():
    assert TSP_TO_INTERPOLATED_DATA_PERIOD == {
        9600: 1 / 100,
        1600: 1 / 625,
    }
