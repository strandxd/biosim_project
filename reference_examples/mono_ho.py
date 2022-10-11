"""
Island with single lowland cell, first herbivores only, later carnivores.
"""


__author__ = 'Hans Ekkehard Plesser, NMBU'


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

for seed in range(100, 101):
    sim = BioSim(geogr, ini_herbs, seed=seed,
                 img_dir='results', img_base=f'mono_ho_{seed:05d}',
                 log_file=f'../data/mono_ho_{seed:05d}.csv', img_years=300)
    sim.simulate(20)
    # sim.make_movie()
