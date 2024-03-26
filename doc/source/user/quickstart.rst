.. _quickstart:

==========
Quickstart
==========

After completing the :ref:`install`, it is possible to start executing Turbomole
workflows.

Create and run a Turbomole Flow
===============================

To create a Flow with atomate2-turbomole, the first step is to instantiate the
´Maker´ used to generate the flows. This maker is then used to generate a
Flow for a given molecule. The Flow can then be executed using, e.g., the local
manager. Below is an example for a jobex (i.e. relaxation) calculation for the
H_2 molecule:

.. code-block:: python

    from jobflow import run_locally
    from pymatgen.core.structure import Molecule

    from atomate2.turbomole.flows.core import JobexFlowMaker

    # Create a simple molecule
    h2_mlc = Molecule(species=["H", "H"], coords=[[0.0, 0.0, -0.7], [0.0, 0.0, 0.7]])

    # Create a maker for ridft calculations
    maker = JobexFlowMaker.ridft()

    # Generate the flow
    flow = maker.make(h2_mlc)

    # Run the flow with the "local manager"
    # Results won't be stored in a database with run_locally
    output = run_locally(flow=flow, create_folders=True)
    print(output)

Note that this is only an example for testing and that for production runs, we strongly
advise to install and use `jobflow-remote <https://github.com/Matgenix/jobflow-remote>`_.
