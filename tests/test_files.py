# -*- coding: utf-8 -*-
import inspect
import os

from curibio.sdk import PlateRecording
from curibio.sdk import WellFile
import numpy as np

PATH_OF_CURRENT_FILE = os.path.dirname((inspect.stack()[0][1]))


def test_WellFile__opens_and_get_well_name():
    wf = WellFile(
        os.path.join(PATH_OF_CURRENT_FILE, "h5", "my_barcode__2020_03_17_163600__D6.h5")
    )
    assert wf.get_well_name() == "D6"


def test_WellFile__opens_and_get_well_index():
    wf = WellFile(
        os.path.join(PATH_OF_CURRENT_FILE, "h5", "my_barcode__2020_03_17_163600__D6.h5")
    )
    assert wf.get_well_index() == 23


def test_WellFile__opens_and_get_numpy_array():
    wf = WellFile(
        os.path.join(PATH_OF_CURRENT_FILE, "h5", "my_barcode__2020_03_17_163600__D6.h5")
    )

    assert np.size(wf.get_numpy_array()) == 25986


def test_WellFile__opens_and_get_voltage_array():
    wf = WellFile(
        os.path.join(PATH_OF_CURRENT_FILE, "h5", "my_barcode__2020_03_17_163600__D6.h5")
    )

    assert np.size(wf.get_voltage_array()) == 25986


def test_PlateRecording__opens_and_get_wellfiles():
    wf1 = os.path.join(
        PATH_OF_CURRENT_FILE, "h5_New", "my_barcode__2020_05_24_203716__B1.h5"
    )
    wf2 = os.path.join(
        PATH_OF_CURRENT_FILE, "h5_New", "my_barcode__2020_05_24_203716__B2.h5"
    )
    wf3 = os.path.join(
        PATH_OF_CURRENT_FILE, "h5_New", "my_barcode__2020_05_24_203716__B3.h5"
    )
    wf4 = os.path.join(
        PATH_OF_CURRENT_FILE, "h5_New", "my_barcode__2020_05_24_203716__B4.h5"
    )
    wf5 = os.path.join(
        PATH_OF_CURRENT_FILE, "h5_New", "my_barcode__2020_05_24_203716__B5.h5"
    )
    wf6 = os.path.join(
        PATH_OF_CURRENT_FILE, "h5_New", "my_barcode__2020_05_24_203716__B6.h5"
    )

    files = PlateRecording([wf1, wf2, wf3, wf4, wf5, wf6])

    # test csv writer
    files.get_combined_csv()

    assert np.size(files.get_wellfile_names()) == 6
