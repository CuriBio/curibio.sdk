# -*- coding: utf-8 -*-
from curibio.sdk import METADATA_EXCEL_SHEET_NAME
from curibio.sdk import METADATA_RECORDING_ROW_START


def test_excel_sheet_names():
    assert METADATA_EXCEL_SHEET_NAME == "recording-information"


def test_excel_sheet_rows():
    assert METADATA_RECORDING_ROW_START == 0
