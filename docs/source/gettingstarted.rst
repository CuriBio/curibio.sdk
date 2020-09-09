.. _gettingstarted:

Installing the SDK
==================

This section will demonstrate how to install the SDK and get started with it.

Download curibio.sdk
---------------------

Local install:

* If you haven't installed Python proceed to the following URL: https://www.python.org/downloads/
* If you haven't installed PIP run in your command line:

  * Windows: ``python get-pip.py``
  * Mac: ``sudo easy_install pip``

*  ``pip install Cython``
*  ``pip install curibio.sdk --no-binary "mantarray-waveform-analysis"``

Online Jupyter noteboook install:

Add the following lines to a cell and run before running any code from the package::

    !pip install Cython
    !pip install curibio.sdk --no-binary "mantarray-waveform-analysis"


Working With the SDK
====================

Writing Plate Recording data to an excel file::

    import os
    from curibio.sdk import PlateRecording
    pr = PlateRecording.from_directory(os.path.join('path','to','folder','containing','h5','files','from a recording')
    pr.write_xlsx('.')
