Wrappers
========

Many development work is done is different languages or with different code bases.
To maintain original authorship, the preferred way is to link directly to the original code.

Github
------

In github, this is done through submodules. A submodule....

Python
------

The preferred way to share code between python developments is through imports.


Why wrappers
------------

Wrappers are funcions in the cwarhm package that wrap around submodules.
An example is the wrapper to set up SUMMA models, from the summaWorkflow_public submodule:

.. autofunction:: cwarhm.wrappers.cwarhm_summa.create_folder_structure
