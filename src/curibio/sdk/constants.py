# -*- coding: utf-8 -*-
"""Docstring."""
from labware_domain_models import LabwareDefinition

TWENTY_FOUR_WELL_PLATE = LabwareDefinition(row_count=4, column_count=6)


METADATA_EXCEL_SHEET_NAME = "recording-information"
CONTINUOUS_WAVEFORM_SHEET_NAME = "continuous-waveforms"
METADATA_RECORDING_ROW_START = 0
METADATA_INSTRUMENT_ROW_START = METADATA_RECORDING_ROW_START + 4

INTERPOLATED_DATA_PERIOD = 1 / 100
