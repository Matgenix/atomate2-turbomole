.. _devinstall:

********************************
Developer setup and installation
********************************

When developing atomate2-turbomole, one does not necessarily need a Turbomole
license although it is very much recommended for testing your features. Indeed, tests
can be executed using a mocked execution of Turbomole. For small modifications to
atomate2-turbomole, you may not need to create new tests from scratch (i.e. generate
Turbomole reference output files used for mocking).

By default the unit tests are executed using the mocked Turbomole executables:

.. code-block:: shell

    pip install .[tests]
    pytest tests/integration

When adding new features to atomate2-turbomole, please consider adding a
test to ensure that the feature works as expected, before
following the contributing instructions at :ref:`contributing`.
