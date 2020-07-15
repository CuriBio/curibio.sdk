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
