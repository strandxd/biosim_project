.. _params:

Parameters
==========
.. warning::

   For some :ref:`examples <examples>` it is used different parameter values than default. This is merely showing their
   names as well as examples of what values they could have.


Animal parameters
-----------------

| Here you can find an overview of the default animal parameters used in this project.
| To change these setting you can use the method :meth:`~biosim.simulation.BioSim.set_animal_parameters`
  from the BioSim class.
| Example:

::

    sim = BioSim(geogr, ini_pop, seed=123)
    sim.set_animal_parameters('Herbivore',
                              {'mu': 1, 'omega': 0, 'gamma': 0,
                               'a_half': 1000})
    sim.set_animal_parameters('Carnivore',
                              {'mu': 1, 'omega': 0, 'gamma': 0,
                               'F': 0, 'a_half': 1000})


.. csv-table:: Default parameter values animal species
   :header: "Parameter", "Herbivores", "Carnivores", "Name"
   :widths: 15, 10, 10, 15
   :align: center

   :math:`w_{birth}`, 8.0, 6.0, w_birth
   :math:`\sigma_{birth}`, 1.5, 1.0, sigma_birth
   :math:`\beta`, 0.9, 0.75, beta
   :math:`\eta`, 0.05, 0.125, eta
   :math:`a_\frac{1}{2}`, 40.0, 40.0, a_half
   :math:`\phi_{age}`, 0.6, 0.3, phi_age
   :math:`w_\frac{1}{2}`, 10.0, 4.0, w_half
   :math:`\phi_{weight}`, 0.1, 0.4, phi_weight
   :math:`\mu`, 0.25, 0.4, mu
   :math:`\gamma`, 0.2, 0.8, gamma
   :math:`\zeta`, 3.5, 3.5, zeta
   :math:`\xi`, 1.2, 1.1, xi
   :math:`\omega`, 0.4, 0.8, omega
   :math:`F`, 10.0, 50.0, F
   :math:`\Delta\Phi_{max}`, ---, 10.0, DeltaPhiMax


Landscape parameters:
---------------------
| Here you can find an overview of the default landscape parameters used in this project.
| To change these setting you can use the method :meth:`~biosim.simulation.BioSim.set_landscape_parameters` from the
  BioSim class.
| Example:

::

    sim = BioSim(geogr, ini_pop, seed=123)
    sim.set_landscape_parameters('L', {'f_max': 150.0})

.. csv-table:: Default parameter values landscape types
   :header: "Parameter", "Lowland", "Highland", "Desert", "Water", "Name"
   :widths: 15, 10, 10, 10, 10, 15
   :align: center

   :math:`f_{max}`, 800.0, 300.0, 0.0, 0.0, f_max
