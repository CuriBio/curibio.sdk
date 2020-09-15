.. _gettingstarted:

Jupyter Notebooks
=================

Jupyter is the environment that CuriBio SDK is designed to be used in. It allows creation
of Python Notebooks which consist of Code Cells (also referred to as just 'cells') that contain Python code,
each of which can be executed independently of others.

Getting Started with Jupyter
----------------------------

Click `here <https://hub-binder.mybinder.ovh/user/curibio-curibio.sdk-mag3pmek/tre>`_ to go to Jupyter Online.



Installing the SDK
==================

This section will demonstrate how to install the SDK and get started with it.

Download curibio.sdk to Online Jupyter notebook
-----------------------------------------------

First, create a new code cell

Add the following lines to a code cell and run before running any code from the package::

    !pip install Cython
    !pip install curibio.sdk --no-binary "mantarray-waveform-analysis"


Test that the SDK downloaded correctly and is working
-----------------------------------------------------

In another code cell run the following code::

    import curibio.sdk
    print(curibio.sdk.__version__)

This should display "REPLACEWITHCURRENTSDKVERSION" underneath the cell.


Working With the SDK
====================

Uploading H5 files
------------------

Files should be placed in this directory:


Exporting data to an excel file
-------------------------------

Export data from a Plate Recording::

    import os
    from curibio.sdk import PlateRecording
    pr = PlateRecording.from_directory(os.path.join('path','to','folder','containing','h5','files','from a recording'))
    pr.write_xlsx('.')
