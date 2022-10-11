"""
Template for BioSim class.
"""

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU

from .island import Island
from .graphics import Graphics
import pandas as pd  # Need this when logger is uncommented --> aware of warning
import random


class BioSim:
    """
    Controls the simulation for the population dynamics of Rossumøya.
    """

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None, pause_time=1e-6):
        """
        Parameters
        ----------
        island_map : str
            Multi-line string specifying island geography
        ini_pop : list
            A list of dictionaries specifying initial population
        seed : int
            Integer used as random number seed
        vis_years : int
            Years between visualization updates (if 0, disable graphics)
        ymax_animals : int
            Number specifying y-axis limit for graph showing animal numbers
        cmax_animals : dict
            Specifying color-code limits for animal densities
        hist_specs : dict
            Specifications for histograms, see below
        img_dir : str
            String with path to directory for figures
        img_base : str
            String with beginning of file name for figures
        img_fmt : str
            String with file type for figures, e.g. 'png'
        img_years :
            Years between visualizations saved to file (default: vis_years)
        log_file : str
            If given, write animal counts to this file
        pause_time : int
            Pause time for drawing graphics. Default 1e-6


        If ymax_animals is None, the y-axis limit should be adjusted automatically.
        If cmax_animals is None, sensible, fixed default values should be used.
        cmax_animals is a dict mapping species names to numbers, e.g.,

            {'Herbivore': 50, 'Carnivore': 20}

        hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
        For each property, a dictionary providing the maximum value and the bin width must be
        given, e.g.,

            {'weight': {'max': 80, 'delta': 2}, 'fitness': {'max': 1.0, 'delta': 0.05}}

        Permitted properties are 'weight', 'age', 'fitness'.

        If img_dir is None, no figures are written to file. Filenames are formed as

            f'{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}'

        where img_number are consecutive image numbers starting from 0.

        img_dir and img_base must either be both None or both strings.

        """
        random.seed(seed)
        self._island_map = island_map
        self._ini_pop = ini_pop

        # Image/movie related
        self._vis_years = vis_years
        if ymax_animals is None:
            self._ymax_animals = 2000
        else:
            self._ymax_animals = ymax_animals
        if cmax_animals is None:
            self._cmax_animals = {'Herbivore': 100, 'Carnivore': 50}
        else:
            self._cmax_animals = cmax_animals
        if img_years is None:
            self._img_years = vis_years
        else:
            self._img_years = img_years

        self._year = 0
        self._final_step = None
        self.island = Island(self._island_map, self._ini_pop)
        self.graphics = Graphics(hist_specs, pause_time, self._ymax_animals,
                                 self._cmax_animals, img_dir, img_base, img_fmt)

        # If logging
        if log_file is not None:
            self._log_file_name = log_file
            self._log_file_dict = {'Herbivore': [], 'Carnivore': []}
        else:
            self._log_file_name = None

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        Parameters
        ----------
        species : str
            String, name of animal species
        params : dict
            Valid parameter specification for species
        """

        if "Herbivore" in species and len(species) == len('Herbivore'):
            self.island.define_animals['Herbivore'].update_attributes(params)
        elif 'Carnivore' in species and len(species) == len('Carnivore'):
            self.island.define_animals['Carnivore'].update_attributes(params)
        else:
            raise ValueError(f'No animal with the name {species} can live on the island.')

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        Parameters
        ----------
        landscape : str
            String, code letter for landscape
        params : dict
            Dictionary with valid parameter specification for landscape
        """
        for f_max_value in params.values():
            if f_max_value < 0:
                raise ValueError('Maximum fodder in a landscape can not be initialized with a '
                                 'negative value.')

        if landscape in self.island.land_letter_map.keys():
            self.island.land_letter_map[landscape].update_attributes(params)
        else:
            raise ValueError(f'No landscape corresponding to the letter {landscape}. Legal '
                             f'landscape letters: {list(self.island.land_letter_map.keys())}')

    def simulate(self, num_years=None):
        """
        Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            number of years to simulate
        """

        self._final_step = num_years
        if self._vis_years > 0:
            self.graphics.setup(self._final_step, self._island_map, self._img_years)

        for year in range(num_years):
            # Update information to use in graphics
            total_herbivores, total_carnivores = self.num_animals_per_species['Herbivore'], \
                                                 self.num_animals_per_species['Carnivore']
            herbivores_in_cell, carnivores_in_cell = self.island.get_animal_pop_map_distribution()
            animal_statistics = self.island.get_animal_statistics()

            # Extract the information from dict. Makes it more readable when used as input.
            herb_fitness = animal_statistics['Herbivore']['fitness']
            carn_fitness = animal_statistics['Carnivore']['fitness']
            herb_age = animal_statistics['Herbivore']['age']
            carn_age = animal_statistics['Carnivore']['age']
            herb_weight = animal_statistics['Herbivore']['weight']
            carn_weight = animal_statistics['Carnivore']['weight']

            if self._vis_years > 0:
                if self._year % self._vis_years == 0:
                    # Graphics
                    self.graphics.update(self.year,
                                         total_herbivores,
                                         total_carnivores,
                                         herbivores_in_cell,
                                         carnivores_in_cell, herb_fitness, carn_fitness,
                                         herb_age, carn_age, herb_weight, carn_weight)
                # Ensures that the line plots gets values every year.
                else:
                    self.graphics.update_total_animals(self._year, total_herbivores,
                                                       total_carnivores)

            # Simulate an annual session
            self.island.year_loop(year)
            self._year += 1

            # Logging
            if self._log_file_name:
                self._log_file_dict['Herbivore'].append(total_herbivores)
                self._log_file_dict['Carnivore'].append(total_carnivores)

        if self._log_file_name:
            log_file = pd.DataFrame.from_dict(self._log_file_dict)
            log_file.to_csv(self._log_file_name)

    def add_population(self, population):
        """
        Add a population to the island

        Parameters
        ----------
        population : list
            List of dictionaries specifying population
        """

        new_population = self.island.store_new_population(population)

        for animal in new_population:
            # This will then be e.g. Highland.add_animals_to_cell...
            self.island.complete_map[animal.position].add_animals_to_cell(animal, animal.species)

    @property
    def year(self):
        """Last year simulated."""
        return self._year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return self.island.get_total_animals()[1]

    @property
    def num_animals_per_species(self):
        """Calculate and return number of animals per species in dict form. Key is species name."""

        return self.island.get_total_animals()[0]

    def make_movie(self, movie_fmt=None):
        """Create MPEG4 movie from visualization images saved."""
        self.graphics.make_movie(movie_fmt)
