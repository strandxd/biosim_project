from .animal import Herbivore, Carnivore
from .landscape import Lowland, Highland, Water, Desert, Landscape
import numpy as np


class Island:
    """
    The island class controls the entire map. The map is constructed in a dictionary where every
    key is a coordinate. The values are landscape objects of different land types. These land types
    could inhabit animals.
    """

    def __init__(self, island_map, initial_pop):
        """
        Initialize the island. In this initialization, it builds the island and adds initial
        population to the correct cell coordinates.

        In addition, it creates a numpy map that imitates the island in numpy array coordinates.
        This will be used for heatmap plots when visualizing simulations.

        Parameters
        ----------
        island_map : str
            String of letters, separated by line split.
        initial_pop : list
            A list of dictionaries containing species to add. Should give age, weight and position.
        """
        self.island_map = island_map
        self.define_animals = {'Herbivore': Herbivore, 'Carnivore': Carnivore}
        self._total_animals_species = {'Herbivore': 0, 'Carnivore': 0}
        self._total_animals = 0

        self._map_moves = {'Up': [-1, 0],
                           'Right': [0, 1],
                           'Down': [1, 0],
                           'Left': [0, -1]}

        # Land checks
        self.land_letter_map = {'W': Water,
                                'H': Highland,
                                'L': Lowland,
                                'D': Desert}
        self._map_string_lines = self.island_map.splitlines()

        # Build initial island. Include initial population
        self.complete_map = {}
        self.build_island()
        self.initial_pop = self.store_new_population(initial_pop)
        self._add_initial_population()

        # Build a numpy map to store values used for heatmap visualization
        self._numpy_map_herb = self._build_numpy_map()
        self._numpy_map_carn = self._build_numpy_map()

    def _build_numpy_map(self):
        """Sets up a numpy array for heatmap visualization."""
        rows = len(self._map_string_lines)  # length of the list
        cols = len(self._map_string_lines[0])  # Length of first element of map list.

        return np.zeros((rows, cols))

    def get_animal_pop_map_distribution(self):
        """
        Translates coordinates and animal species population from the dictionary map to a numpy
        array. This array is used in heatmap visualization of animal distribution.

        Returns
        -------
        numpy.ndarray
            N-dimensional numpy arrays with animal species population distribution. Shape equal to
            map size. Separate numpy maps for herbivores and carnivores.
        """
        for coord in self.complete_map.keys():
            x, y = coord
            # Numpy starts indexing at 0, our dictionary at 1. (i.e. upper left corner is
            # (1, 1) for dict (0, 0) for numpy)
            x -= 1
            y -= 1
            self._numpy_map_herb[x, y] = len(self.complete_map[coord].animals['Herbivore'])
            self._numpy_map_carn[x, y] = len(self.complete_map[coord].animals['Carnivore'])

        return self._numpy_map_herb, self._numpy_map_carn

    def get_animal_statistics(self):
        """
        Gather animal statistics, fitness, age and weight, used for histogram plots.

        Returns
        -------
        dict
            Dictionary with statistics for each species.
        """
        animal_statistics = {'Herbivore': {'fitness': [], 'age': [], 'weight': []},
                             'Carnivore': {'fitness': [], 'age': [], 'weight': []}}
        for coord in self.complete_map.keys():
            for species, animal in self.complete_map[coord].animals.items():
                animal_statistics[species]['fitness'].extend(
                    [ani.fitness for ani in self.complete_map[coord].animals[species]]
                )
                animal_statistics[species]['age'].extend(
                    [ani.age for ani in self.complete_map[coord].animals[species]]
                )
                animal_statistics[species]['weight'].extend(
                    [ani.weight for ani in self.complete_map[coord].animals[species]]
                )
        return animal_statistics

    def _check_map_legal_characters(self):
        """Check to see if letters passed to map are legal."""
        island_map_stripped_string = self.island_map.replace('\n', '')
        # Initialize land types with position None to extract the landscape letters
        legal_land_letters = [land_type().get_landscape_letter() for land_type in
                              self.land_letter_map.values()]

        for letter in island_map_stripped_string:
            if letter not in legal_land_letters:
                raise ValueError('Invalid landscape letter assigned to map.')

    def _check_map_line_length(self):
        """Check to see if each line of the passed in map is of equal length."""
        first_line_length = len(self._map_string_lines[0])

        if not all([len(line) == first_line_length for line in self._map_string_lines[1:]]):
            raise ValueError('Map lines does not have equal length.')

    def _check_map_edges(self):
        """Check to see if edges of the map is water, i.e. contains the letter for Water (W)."""
        for land_type in self._map_string_lines[0]:
            if land_type != 'W':
                raise ValueError('Edge of map does not contain water.')

        for land_type in self._map_string_lines[-1]:
            if land_type != 'W':
                raise ValueError('Edge of map does not contain water.')

        for land_type in self._map_string_lines[1:-1]:
            if land_type[0] != 'W':
                raise ValueError('Edge of map does not contain water.')
            if land_type[-1] != 'W':
                raise ValueError('Edge of map does not contain water')

    def build_island(self):
        """
        After initial checks in order to determine if the input string used for generating the
        island is valid, build island in dictionary form.

        Examples
        --------
        >>> island_string = 'WWW/nWLW/nWWW'
        >>> self.build_island()
        {(1, 1): <src.biosim.landscape.Water at 0x22ef46fa3a0>,
         (1, 2): <src.biosim.landscape.Water at 0x22ef46fac10>,
         (1, 3): <src.biosim.landscape.Water at 0x22ef46fae50>,
         (2, 1): <src.biosim.landscape.Water at 0x22ef46fae80>,
         (2, 2): <src.biosim.landscape.Lowland at 0x22ef46fa7c0>,
         (2, 3): <src.biosim.landscape.Water at 0x22ef46faa90>,
         (3, 1): <src.biosim.landscape.Water at 0x22ef46fa880>,
         (3, 2): <src.biosim.landscape.Water at 0x22ef46fab80>,
         (3, 3): <src.biosim.landscape.Water at 0x22ef46fab50>}
        """
        # Do some initial checks:
        self._check_map_legal_characters()
        self._check_map_line_length()
        self._check_map_edges()

        # Start to build the island
        row_pos = 1
        col_pos = 1
        for land_type in self.island_map:
            if land_type != '\n':
                self.complete_map.update(({(row_pos, col_pos): self.land_letter_map[land_type](
                    (row_pos, col_pos))})
                )
                col_pos += 1
            else:
                col_pos = 1
                row_pos += 1

    def store_new_population(self, population_list):
        """
        Stores all new animals from ``population_list`` as class instances of the specified animal
        in a list. This list is essentially a preparation of adding animals to individual cells.

        Parameters
        ----------
        population_list : list
            A list of dictionaries containing species to add. Should give age, weight and position.

        Returns
        -------
        list
            Containing class instances of animals.
        """
        new_animals = []
        for population in population_list:
            for animal in population['pop']:
                species = animal['species']
                new_animals.append(self.define_animals[species](age=animal['age'],
                                                                weight=animal['weight'],
                                                                position=population['loc']))

        return new_animals

    def _add_initial_population(self):
        """Adds population specified during island initialization (initial_pop)."""
        for animal in self.initial_pop:
            self.complete_map[animal.position].add_animals_to_cell(animal, animal.species)

    def neighbor_cells(self, current_pos):
        """
        Get neighbouring cells of the current position. Try to access part on map based on new
        position, but if the move is illegal (i.e. you move to pos (0, 1) --> doesn't exist in the
        dictionary map), the neighboring coordinate is false.

        If it exists we then check if it's a legal land type (i.e. not water).
        Append only legal neighbors to the list.

        Parameters
        ----------
        current_pos : tuple
            Current position of the animal that wants to move

        Returns
        -------
        list
            Containing legal neighboring cells
        """
        row, col = current_pos
        legal_neighbor_coords = []

        # Try to access the neighboring cell. If it is out of reach it will raise a KeyError. This
        # neighboring cell is then an invalid move
        for move in self._map_moves.keys():
            row_increase, col_increase = self._map_moves[move]
            temp_row, temp_col = row + row_increase, col + col_increase
            try:
                neighbor = self.complete_map[(temp_row, temp_col)]
                if neighbor.legal_land_type:
                    coord = (temp_row, temp_col)
                else:
                    coord = False
            # In the current setup, this won't happen as corners are covered in water.
            except KeyError:
                coord = False

            # Append coordinate value if it's a legal move.
            if coord:
                legal_neighbor_coords.append(coord)

        return legal_neighbor_coords

    def migrate_to_new_cell(self, land_type: Landscape):
        """
        Performs migration by updating landscape cell with new animals. Also update the specific
        animal position as well as total animals in the cell.

        Loop through each element of the dictionary containing animals who passed the migration
        check. Check if the position it wants to move to is a legal move. Then, if it is legal,
        perform migration by updating the animals position, add it to the new cell and
        remove total animals from the current cell (removes the actual animal from the cell in
        ``year_loop`` after migration).

        Parameters
        ----------
        land_type : object
            ``Water``, ``Desert``, ``Highland`` or ``Lowland`` object with inherited ``Landscape``
            methods.
        """

        animals_to_migrate = land_type.migrate_animals()
        for curr_pos, potential_pos, animal, species in zip(*animals_to_migrate.values()):
            legal_neighbor_cells = self.neighbor_cells(curr_pos)

            if potential_pos in legal_neighbor_cells:
                animal.update_position(potential_pos)
                self.complete_map[potential_pos].add_animals_to_cell(animal, species)
                land_type.decrease_total_animals()

    def get_total_animals(self):
        """
        Get the total number of animals per species as well as the combined total. Resets counter
        every time the method is called. Then loop through the map and add species count.

        Returns
        -------
        dict, int
            Dictionary with total number of animals per species name (key). Total number of animals
            as a combined number of the per species total.
        """
        # Reset counter for species
        self._total_animals = 0
        for species in self._total_animals_species.keys():
            self._total_animals_species[species] = 0

        for coord, land_type in self.complete_map.items():
            if land_type.legal_land_type:
                for species in self._total_animals_species.keys():
                    self._total_animals_species[species] += \
                        len(self.complete_map[coord].animals[species])

        for species in self._total_animals_species.keys():
            self._total_animals += self._total_animals_species[species]

        return self._total_animals_species, self._total_animals

    def year_loop(self, year):
        """
        Simulates an annual cycle in Rossumøya.

        Loops through the map and executes each step for all animals in the cell. It is split
        into three separate phases:

        * First phase:
            Updates sorting order and resets yearly attribute values. Then herbivores feed before
            carnivores, the population is updated to get rid of animals that died during the hunt.
            Then the animals tries to procreate and new babies are added.
        * Second phase:
            Animals migrate and changes cell (if successful).
        * Third phase:
            In the final phase animals mostly update attributes. They age, gets a weight reduction
            as well as a chance to die. Finally, animals who die gets removed from the island.

        Parameters
        ----------
        year : int
            Current year of the simulation.
        """
        for land_type in self.complete_map.values():
            if land_type.legal_land_type:
                land_type.update_animal_sorting()
                land_type.yearly_updates()

                land_type.feeding_herbivores()
                land_type.feeding_carnivores()

                land_type.update_population(herb_only=True)
                land_type.procreation(year)

        for land_type in self.complete_map.values():
            if land_type.legal_land_type:
                self.migrate_to_new_cell(land_type)
                land_type.update_animals_after_migration()

        for land_type in self.complete_map.values():
            if land_type.legal_land_type:
                land_type.aging()
                land_type.loss_of_weight()
                land_type.death()
                land_type.update_population()
