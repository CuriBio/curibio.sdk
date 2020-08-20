# -*- coding: utf-8 -*-
from curibio.sdk import CONTINUOUS_WAVEFORM_SHEET_NAME
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_INSTRUMENT_ROW_START
from curibio.sdk import METADATA_RECORDING_ROW_START


def test_excel_sheet_names():
    assert METADATA_EXCEL_SHEET_NAME == "recording-information"
    assert CONTINUOUS_WAVEFORM_SHEET_NAME == "continuous-waveforms"


def test_excel_sheet_rows():
    assert METADATA_RECORDING_ROW_START == 0
    assert METADATA_INSTRUMENT_ROW_START == METADATA_RECORDING_ROW_START + 4
