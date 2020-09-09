.. _gettingstarted:

Installing the SDK
==================

This section will demonstrate how to install the SDK and get started with it.

Download curibio.sdk to Online Jupyter notebook
-----------------------------------------------

Add the following lines to a cell and run before running any code from the package::

    !pip install Cython
    !pip install curibio.sdk --no-binary "mantarray-waveform-analysis"


Test that the SDK downloaded correctly and is working
-----------------------------------------------------

In another cell run the following code::

    import curibio.sdk
    print(curibio.sdk.__version__)

This should display "REPLACEWITHCURRENTSDKVERSION" underneath the cell.


Working With the SDK
====================

Writing Plate Recording data to an excel file::

    import os
    from curibio.sdk import PlateRecording
    pr = PlateRecording.from_directory(os.path.join('path','to','folder','containing','h5','files','from a recording'))
    pr.write_xlsx('.')
