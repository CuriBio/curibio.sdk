# -*- coding: utf-8 -*-
import inspect
import os

from curibio.sdk import WellFile

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
