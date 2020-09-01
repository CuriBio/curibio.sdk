# -*- coding: utf-8 -*-
"""Docstring."""

from mantarray_file_manager import WellFile

from .constants import CONTINUOUS_WAVEFORM_SHEET_NAME
from .constants import METADATA_EXCEL_SHEET_NAME
from .constants import METADATA_INSTRUMENT_ROW_START
from .constants import METADATA_RECORDING_ROW_START
from .constants import TSP_TO_INTERPOLATED_DATA_PERIOD
from .plate_recording import DEFAULT_PIPELINE_TEMPLATE
from .plate_recording import PlateRecording

try:  # adapted from https://packaging.python.org/guides/single-sourcing-package-version/
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata  # type: ignore # Eli (9/1/20): for some reason mypy is giving weird errors for this
__version__ = metadata.version("curibio.sdk")  # type: ignore # Eli (9/1/20): for some reason mypy is giving weird errors for this

__all__ = [
    "WellFile",
    "PlateRecording",
    "METADATA_EXCEL_SHEET_NAME",
    "METADATA_RECORDING_ROW_START",
    "METADATA_INSTRUMENT_ROW_START",
    "CONTINUOUS_WAVEFORM_SHEET_NAME",
    "TSP_TO_INTERPOLATED_DATA_PERIOD",
    "DEFAULT_PIPELINE_TEMPLATE",
    "__version__",
]
