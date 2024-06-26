.. _introduction:

************
Introduction
************

atomate2-turbomole is a free, open-source add-on to `atomate2
<https://github.com/materialsproject/atomate2>`_, providing workflows for `Turbomole
<https://www.turbomole.org/>`_ using
`jobflow <https://materialsproject.github.io/jobflow/>`_. In order to use atomate2-turbomole,
you must have a Turbomole license (see `here <https://store.turbomole.org/>`_).

atomate2-turbomole's functionalities are very similar to those in atomate2. Jobs and
Flows are generated using Makers. These Makers are serializable, and can thus
be easily stored in a file or a database, providing full reproducibility of simulations.

Similarly to atomate2, inputs are generated by pre-defined, customizable input set
generators whose back-end is based on the `turbomoleio
<https://github.com/Matgenix/turbomoleio>`_ package. Outputs are well-defined `pydantic
<https://github.com/pydantic/pydantic>`_
schemas based on `emmet <https://github.com/materialsproject/emmet>`_ and adhere
to the same structure as those found in atomate2.
