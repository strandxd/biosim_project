.. biosim-u03-mohamed-hakon documentation master file, created by
   sphinx-quickstart on Fri Jun 10 15:15:10 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

BioSim documentation
====================================================
.. toctree::
   :maxdepth: 2
   :hidden:

   parameters
   examples

.. toctree::
   :maxdepth: 2
   :caption: Modules:
   :hidden:

   animal
   landscape
   island
   graphics
   simulation

| The BioSim package consists of several modules used to simulate and paint graphics of the
  population dynamics in Rossumøya. It is a rather simple dynamic showing a population of
  herbivores and carnivores. The carnivores hunt the herbivores, while the herbivores feed
  on vegetation. Different land types supply various amount of fodder and currently we have no
  species that can stay in water. The following land types are available:

 * Highland
 * Lowland
 * Desert
 * Water

| To see an overview of land supply, as well as other parameters used as calculation metrics in the
  simulation, see :ref:`parameters <params>`. It is also possible to view :ref:`examples <examples>`
  of simulations as well as code snippets on how to execute these.
| You can get a rough overview of how the code in the package is currently structured from the
  image below.

.. imgur:: SVPuuze
   :width: 500pt
   :height: 200pt


Installation
------------
If you wish to install the package, please follow this short guide on how to do so.

Requirements
""""""""""""

The following packages are required to run BioSim:

* ``Numpy`` - https://numpy.org
* ``Pandas`` - https://pandas.pydata.org
* ``Scipy`` - https://scipy.org
* ``Matplotlib`` - https://matplotlib.org


Install
"""""""

.. code-block::

   git clone https://gitlab.com/nmbu.no/emner/inf200/h2021/june-teams/u03_mohamed_hakon/biosim-u03-mohamed-hakon
   cd to directory
   python build -m
   cd dist
   pip install biolab-1.0-py-none-any-whl


Package can be uninstalled using:

.. code-block::

    pip uninstall biolab-1.0-py-none-any-whl


Contact
^^^^^^^^
| Håkon Strand: hakon.strand@nmbu.no
| Mohamed Omar Atteyeh: mohamed.omar.atteyeh@nmbu.no
