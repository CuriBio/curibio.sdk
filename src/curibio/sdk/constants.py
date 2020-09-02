# -*- coding: utf-8 -*-
"""Docstring."""
from labware_domain_models import LabwareDefinition

try:  # adapted from https://packaging.python.org/guides/single-sourcing-package-version/
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata  # type: ignore # Eli (9/1/20): for some reason mypy is giving weird errors for this
PACKAGE_VERSION = metadata.version("curibio.sdk")  # type: ignore # Eli (9/1/20): for some reason mypy is giving weird errors for this

TWENTY_FOUR_WELL_PLATE = LabwareDefinition(row_count=4, column_count=6)


METADATA_EXCEL_SHEET_NAME = "metadata"
METADATA_RECORDING_ROW_START = 0
METADATA_INSTRUMENT_ROW_START = METADATA_RECORDING_ROW_START + 4
METADATA_OUTPUT_FILE_ROW_START = METADATA_INSTRUMENT_ROW_START + 3

CONTINUOUS_WAVEFORM_SHEET_NAME = "continuous-waveforms"
AGGREGATE_METRICS_SHEET_NAME = "aggregate-metrics"
TSP_TO_INTERPOLATED_DATA_PERIOD = {  # Tissue Sampling Period (microseconds) to Interpolated Data Period (seconds)
    9600: 1 / 100,
    1600: 1 / 625,
}
