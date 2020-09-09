.. _gettingstarted:

Installing the SDK
==================

This section will demonstrate how to install the SDK and get started with it.

Download curibio.sdk
---------------------

 * If you haven't installed Python proceed to the following URL: https://www.python.org/downloads/
 * If you haven't installed PIP run in your command line (WINDOWS): ``python get-pip.py``.
 * If you haven't installed PIP run in your terminal (MAC): ``sudo easy_install pip``.
 * Install commands (locally in terminal):

   *  ``pip install Cython``
   *  ``pip install curibio.sdk --no-binary "mantarray-waveform-analysis"``

 * Install commands (jupyter notebook):

   *  ``!pip install Cython``
   *  ``!pip install curibio.sdk --no-binary "mantarray-waveform-analysis"``


Working With the SDK
====================

Writing Plate Recording data to an excel file::

    import os
    from curibio.sdk import PlateRecording
    pr = PlateRecording.from_directory(os.path.join('path','to','folder','containing','h5','files','from a recording'))
    pr.write_xlsx('.')
