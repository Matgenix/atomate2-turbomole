.. _install:

************
Installation
************

``atomate2-turbomole`` is a Python 3.9+ library and can be installed using pip::

  pip install atomate2-turbomole

or, for the development version::

  pip install git+https://github.com/Matgenix/atomate2-turbomole.git

In order to execute atomate2-turbomole workflows, you should also use a workflow
manager. The simplest one, which should only be used for testing/trying purposes,
is the local manager (i.e. ´run_locally´, see jobflow tutorials) included within `jobflow
<https://materialsproject.github.io/jobflow/>`_. For production runs, we recommend
using `jobflow-remote <https://github.com/Matgenix/jobflow-remote>`_, which provides
an extensive list of features for managing, checking, submitting, restarting, ...
your workflows.
