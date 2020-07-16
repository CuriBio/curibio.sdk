# -*- coding: utf-8 -*-
"""Classes and functinos for finding and managing files."""
import inspect
import os
from typing import List

import h5py
from nptyping import NDArray
import numpy as np

PATH_OF_CURRENT_FILE = os.path.dirname((inspect.stack()[0][1]))


class WellFile:
    """Wrapper around an H5 file for a single well of data.

    Args:
        file_name: The path of the H5 file to open.

    Attributes:
        _h5_file: The opened H5 file object.
    """

    def __init__(self, file_name: str) -> None:
        self._h5_file: h5py._hl.files.File = h5py.File(
            file_name, "r",
        )

    def get_well_name(self) -> str:
        return str(self._h5_file.attrs["Well Name"])

    def get_well_index(self) -> int:
        return int(self._h5_file.attrs["Well Index (zero-based)"])

    def get_numpy_array(self) -> NDArray[2, float]:
        """Return the data (tissue sensor vs time)."""
        time_step = 8 * 1.2e-3  # tissue sample rate is just over 100Hz
        tissue_data = self._h5_file["tissue_sensor_readings"]

        times = np.arange(len(tissue_data)) * time_step
        len_time = len(times)

        data = np.zeros((2, len_time))
        for i in range(len_time):
            data[0, i] = times[i]
            data[1, i] = tissue_data[i]

        return data

    def get_voltage_array(self) -> NDArray[2, float]:
        """Return the voltage vs time data."""
        time_step = 8 * 1.2e-3  # tissue sample rate is just over 100Hz
        vref = 3.3  # ADC reference voltage
        least_significant_bit = vref / 2 ** 23  # ADC quantization step
        gain = 1  # ADC gain
        tissue_data = self._h5_file["tissue_sensor_readings"]

        times = np.arange(len(tissue_data)) * time_step
        len_time = len(times)

        voltages = []
        for this_tissue_data in tissue_data:
            voltages.append(1e3 * (least_significant_bit * this_tissue_data) / gain)

        voltage_data = np.zeros((2, len_time))
        for i in range(len_time):
            voltage_data[0, i] = times[i]
            voltage_data[1, i] = voltages[i]

        return voltage_data


class PlateRecording:
    """Wrapper around 24 WellFiles fpr a single plate of data.

    Args:
        file_paths: A list of all the file paths for each h5 file to open.

    Attributes:
        _files_ : WellFiles of all the file paths provided.
    """

    def __init__(self, file_paths: List[str]) -> None:
        self._files_: List[str] = file_paths

    def get_wellfile_names(self) -> List[str]:
        well_files = []
        for well in self._files_:
            well_files.append(WellFile(well).get_well_name())
        return well_files

    def get_combined_csv(self) -> None:
        data = np.zeros((len(self._files_) + 1, 12315))
        for i, well in enumerate(self._files_):
            well_data = WellFile(well).get_numpy_array()
            data[0, :] = well_data[0, :]
            data[i + 1, :] = well_data[1, :]

        my_local_path_data = os.path.join(PATH_OF_CURRENT_FILE, "PlateRecording.csv")
        np.savetxt(my_local_path_data, data, delimiter=",", fmt="%d")
