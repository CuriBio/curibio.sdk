.. _gettingstarted:

Jupyter Notebooks
=================

Jupyter is the environment that CuriBio SDK is designed to be used in. It allows creation
of Python Notebooks which consist of Code Cells (also referred to as just 'cells') that contain Python code,
each of which can be executed independently of others.

Getting Started with Jupyter
----------------------------

Click `here <https://mybinder.org/v2/gh/curibio/curibio.sdk/master?filepath=intro.ipynb>`_ to navigate to the online
notebook.

You should land on a page that looks like this:

INSERT SCREENSHOT OF MYBINDER LOADING PAGE HERE

It may take a few minutes to load the notebook. Once it's loaded you should see this page:

INSERT SCREENSHOT OF FRESH NB HERE


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
