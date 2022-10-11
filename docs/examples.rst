.. _examples:

Examples
========

Full simulation
---------------
| Results from full simulation.
| Default parameters with initial population consisting of 50 carnivores and 200 herbivores at the
  same location.


.. raw:: html

   <details>
   <summary><a>Python code</a></summary>

.. code-block::

    import textwrap
    from biosim.simulation import BioSim



    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WWHHLLLLLLLWWLLLLLLLW
               WWHHLLLLLLLWWLLLLLLLW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDWWLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDDLWWWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WWWHHHHLLLLLLLWWWWWWW
               WWWHHHHHHWWWWWWWWWWWW
               WWWWWWWWWWWWWWWWWWWWW"""

    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (2, 7),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(200)]}]
    ini_carns = [{'loc': (2, 7),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(50)]}]

    sim = BioSim(geogr, ini_herbs + ini_carns, seed=1,
                 hist_specs={'fitness': {'max': 1.0, 'delta': 0.05},
                             'age': {'max': 60.0, 'delta': 2},
                             'weight': {'max': 60, 'delta': 2}},

                 cmax_animals={'Herbivore': 200, 'Carnivore': 50},
                 img_dir='results',
                 img_base='sample')

    sim.simulate(400)

.. raw:: html

   </details>

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/k-IVg5klh9c" title="YouTube video player"
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>


Migration
---------
Results from migration test with forced movement and no feeding, procreation, dying or hunting.

.. raw:: html

   <details>
   <summary><a>Python code</a></summary>

.. code-block::

    from biosim.simulation import BioSim
    import textwrap

    geogr = """\
                WWWWWWWWWWW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WDDDDDDDDDW
                WWWWWWWWWWW"""


    geogr = textwrap.dedent(geogr)
    ini_herbs = [{'loc': (6, 6),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 500}
                           for _ in range(1000)]}]
    ini_carns = [{'loc': (6, 6),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 500}
                           for _ in range(1000)]}]

    ini_pop = ini_herbs + ini_carns

    sim = BioSim(geogr, ini_pop, seed=123, pause_time=2, img_dir='results', img_base='migrate_simple')
    sim.set_animal_parameters('Herbivore',
                              {'mu': 1, 'omega': 0, 'gamma': 0,
                               'a_half': 1000})
    sim.set_animal_parameters('Carnivore',
                              {'mu': 1, 'omega': 0, 'gamma': 0,
                               'F': 0, 'a_half': 1000})

    sim.simulate(7)

.. raw:: html

   </details>

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/cPZpSUCYWLc" title="YouTube video player"
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>


Single landscape cell herbivores
--------------------------------
Results from single cell simulations of only herbivores on a ``lowland`` cell. 50 different
simulations with different random seeds stacked on top of each other.

.. raw:: html

   <details>
   <summary><a>Python code</a></summary>

.. code-block::

    import textwrap
    from biosim.simulation import BioSim

    geogr = """\
               WWW
               WLW
               WWW"""

    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(50)]}]

    for seed in range(100, 150):
        sim = BioSim(geogr, ini_herbs, seed=seed,
                     img_dir='results', img_base=f'mono_ho_{seed:05d}',
                     log_file=f'../data/mono_ho_{seed:05d}.csv', img_years=300)

        sim.simulate(301)

.. raw:: html

   </details>

.. imgur:: lV4ILfC
   :width: 500pt
   :height: 200pt


Single landscape cell herbivores & carnivores
-----------------------------------------------
Results from testing interaction with herbivores and carnivores in a single ``lowland`` cell. Below
you can see the results from different variations of the ``DeltaPhiMax`` parameter. Higher value
translates to higher chance that carnivores survive in the simulation.

100 simulations with different random seeds stacked on top of each other.

DeltaPhiMax = 15
""""""""""""""""

.. raw:: html

   <details>
   <summary><a>Python code</a></summary>

.. code-block::

    import textwrap
    from biosim.simulation import BioSim

    geogr = """\
               WWW
               WLW
               WWW"""

    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(50)]}]
    ini_carns = [{'loc': (2, 2),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(20)]}]

    for seed in range(100, 200):
        sim = BioSim(geogr, ini_herbs, seed=seed,
                     img_dir='results', log_file=f'../data/mono_hc_{seed:05d}.csv', img_years=300)

        sim.set_animal_parameters('Carnivore', {'DeltaPhiMax': 15})
        sim.simulate(50)
        sim.add_population(ini_carns)
        sim.simulate(251)

.. raw:: html

   </details>

.. imgur:: 9XxJQdA
   :width: 500pt
   :height: 200pt


DeltaPhiMax = 10
""""""""""""""""

.. raw:: html

   <details>
   <summary><a>Python code</a></summary>

.. code-block::

    import textwrap
    from biosim.simulation import BioSim

    geogr = """\
               WWW
               WLW
               WWW"""

    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(50)]}]
    ini_carns = [{'loc': (2, 2),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                           for _ in range(20)]}]

    for seed in range(100, 200):
        sim = BioSim(geogr, ini_herbs, seed=seed,
                     img_dir='results', log_file=f'../data/mono_hc_delta10_{seed:05d}.csv', img_years=300)

        sim.set_animal_parameters('Carnivore', {'DeltaPhiMax': 10})
        sim.simulate(50)
        sim.add_population(ini_carns)
        sim.simulate(251)

.. raw:: html

   </details>

.. imgur:: KiitDMS
   :width: 500pt
   :height: 200pt
