# -*- coding: utf-8 -*-
"""Classes and functinos for finding and managing files."""
import h5py
from nptyping import NDArray
import numpy as np


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

    def get_numpy_array(self) -> NDArray[2, int]:
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

    def get_voltage_array(self) -> NDArray[2, int]:
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
