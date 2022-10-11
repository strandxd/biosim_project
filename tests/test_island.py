"""
Testing of the island module.
"""

import pytest
from biosim.animal import Herbivore, Carnivore
from biosim.island import Island
import numpy as np
import textwrap


class TestIsland:
    @pytest.fixture
    def setup_params(self, request):
        Herbivore.update_attributes(request.param)
        Carnivore.update_attributes(request.param)
        yield
        Herbivore.reset_default_attribute_values()
        Carnivore.reset_default_attribute_values()

    @pytest.fixture(autouse=True)
    def setup_island(self):
        geogr_map = """\
                   WWWW
                   WLHW
                   WWWW"""
        self.geogr = textwrap.dedent(geogr_map)

        self.ini_herbs = [{'loc': (2, 2),
                           'pop': [{'species': 'Herbivore',
                                    'age': 5,
                                    'weight': 20}
                                   for _ in range(5)]}]
        self.ini_carns = [{'loc': (2, 3),
                           'pop': [{'species': 'Carnivore',
                                    'age': 5,
                                    'weight': 20}
                                   for _ in range(5)]}]
        self.ini_pop = self.ini_herbs + self.ini_carns
        # self.simple_map_init = {'island_map': geogr, 'ini_pop': None}

    def test_build_numpy_map(self):
        """Test that it creates the correct numpy map."""
        island = Island(self.geogr, self.ini_herbs)
        rows = len(self.geogr.splitlines())
        cols = len(self.geogr.splitlines()[0])
        numpy_map = island._build_numpy_map()

        assert numpy_map.shape == (rows, cols) and type(numpy_map) == np.ndarray

    @pytest.mark.parametrize('map_str', ['WWW\nWSW\nWWW', 'WWW\nWQW\nWWW'])
    def test_legal_map_characters(self, map_str):
        """Test that illegal map string characters raises ValueError."""
        with pytest.raises(ValueError):
            Island(map_str, self.ini_carns)

    @pytest.mark.parametrize('map_str', ['WWW\nWLWW\nWWW', 'WWW\nWDW\nWWWW'])
    def test_map_line_length(self, map_str):
        """Test that illegal map string line length raises ValueError."""
        with pytest.raises(ValueError):
            Island(map_str, self.ini_carns)

    @pytest.mark.parametrize('map_str', ['LWW\nWLW\nWWW', 'WWW\nHHW\nWWW',
                                         'WWW\nWDW\nWDW', 'WWW\nWDD\nWWW'])
    def test_map_edges(self, map_str):
        """Test that illegal map edges raises ValueError."""
        with pytest.raises(ValueError):
            Island(map_str, self.ini_herbs)

    def test_build_map(self):
        """Test that it builds correct map from string."""
        # Builds map as part of initialization. Check if it is correct.
        map_single_line = self.geogr.replace('\n', '')
        island = Island(self.geogr, self.ini_herbs)
        matching_land_letter = []
        for land_type, land_letter in zip(island.complete_map.values(), map_single_line):
            matching_land_letter.append(land_type.get_landscape_letter() == land_letter)

        assert all(matching_land_letter)

    def test_animal_pop_map_distribution(self):
        """Test that numpy map population update gathers correct population at correct coords."""
        # Coord(2, 2) has 5 herbivores. Coord(2, 3) has 5 carnivores.
        num_herb = len(self.ini_herbs[0]['pop'])
        num_carn = len(self.ini_carns[0]['pop'])
        island = Island(self.geogr, self.ini_pop)
        map_herb, map_carn = island.get_animal_pop_map_distribution()

        # Coords for numpy map is (row-1, col-1) compared to dictionary map
        assert map_herb[2 - 1, 2 - 1] == num_herb and map_carn[2 - 1, 3 - 1] == num_carn

    def test_get_animal_statistics(self):
        """Test to see if correct statistics are returned. Used in histogram plots."""
        pos = (2, 2)
        age = 5
        weight = 10
        carn = [Carnivore(age, weight, pos) for _ in range(10)]
        for ani in carn:
            ani._fitness = 0.345
        island = Island(self.geogr, [])

        # Add some carnivores with manipulated fitness value
        for coord, value in island.complete_map.items():
            if coord == pos:
                island.complete_map[coord].animals['Carnivore'].extend(carn)

        ani_stats = island.get_animal_statistics()

        assert all([stat_fit == 0.345 for stat_fit in ani_stats['Carnivore']['fitness']]) and \
               all([stat_age == age for stat_age in ani_stats['Carnivore']['age']]) and \
               all([stat_weight == weight for stat_weight in ani_stats['Carnivore']['weight']])

    def test_store_new_population(self):
        """Test that the storing of new population returns the correct list of animals."""
        pos = (2, 2)
        age = 4
        weight = 20
        species = 'Carnivore'
        num = 5
        new_carns = [{'loc': pos,
                      'pop': [{'species': species,
                               'age': age,
                               'weight': weight}
                              for _ in range(num)]}]
        island = Island(self.geogr, [])

        new_pop = island.store_new_population(new_carns)

        assert (all([(ani.position == pos and ani.age == age and ani.weight == weight and
                      ani.species == species) for ani in new_pop])) and len(new_pop) == num

    def test_get_total_animals(self):
        """Test if the method returns correct amount of each species and total amount."""
        num_new_herbs = 15
        num_new_carns = 27
        num_total = num_new_herbs + num_new_carns
        new_herbs = [{'loc': (2, 2),
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 20}
                              for _ in range(num_new_herbs)]}]
        new_carns = [{'loc': (2, 3),
                      'pop': [{'species': 'Carnivore',
                               'age': 5,
                               'weight': 20}
                              for _ in range(num_new_carns)]}]
        tot_new_pop = new_herbs + new_carns

        island = Island(self.geogr, tot_new_pop)
        tot_animals_per_species, tot_animals_combined = island.get_total_animals()

        assert tot_animals_per_species['Herbivore'] == num_new_herbs and \
               tot_animals_per_species['Carnivore'] == num_new_carns and \
               tot_animals_combined == num_total

    def test_neighbor_cells(self):
        """Test to see if correct legal neighboring cells are returned from current position."""
        # Initialize herbivores with current pos (2, 2). Only legal moves are (2, 3) and (3, 2)
        neighbor_map = 'WWWW\nWLDW\nWDWW\nWWWW'
        legal_neighbors = [(2, 3), (3, 2)]
        island = Island(neighbor_map, self.ini_herbs)
        current_pos = self.ini_herbs[0]['loc']

        assert island.neighbor_cells(current_pos) == legal_neighbors

    @pytest.mark.parametrize('setup_params',
                             [{'mu': 1, 'omega': 0, 'gamma': 0, 'a_half': 2000}], indirect=True)
    def test_migration(self, setup_params):
        """
        Test to see that it's a roughly equal distribution of animals in neighboring cells when
        migration is forced. With 1000 initial animals in the center, the rough estimation would be
        that each legal neighbouring cell should average 250 animals in each cell.
        Stating point is (3, 3) making legal positions:
            (2, 3) - Up
            (3, 4) - Right
            (4, 3) - Down
            (3, 2) - Left

        Note: Definitely not the most robust test, and with quite high margin to compensate for
        fewer experiments. Guards against serious errors in migration function and ensures that
        it is roughly on point with expected outcome. See migration video in 'examples' inside docs
        for visualized testing of the migration cycle.
        """
        ini_herbs = [{'loc': (3, 3),
                      'pop': [{'species': 'Herbivore',
                               'age': 2,
                               'weight': 5000}
                              for _ in range(1000)]}]
        geogr = """\
                    WWWWW
                    WDDDW
                    WDDDW
                    WDDDW
                    WWWWW"""

        geogr = textwrap.dedent(geogr)
        island = Island(geogr, ini_herbs)

        # create dict with lists to store how many animals migrate to each position
        up_coord = {(2, 3): []}
        right_coord = {(3, 4): []}
        down_coord = {(4, 3): []}
        left_coord = {(3, 2): []}

        # Set a margin of error
        margin = 50

        for _ in range(1000):
            for coord, land_type in island.complete_map.items():

                if land_type.legal_land_type:
                    island.migrate_to_new_cell(land_type)
                    if coord == (2, 3):
                        up_coord[(2, 3)].append(
                            len(island.complete_map[coord].animals['Herbivore'])
                        )
                    if coord == (3, 4):
                        right_coord[(3, 4)].append(
                            len(island.complete_map[coord].animals['Herbivore'])
                        )
                    if coord == (4, 3):
                        down_coord[(4, 3)].append(
                            len(island.complete_map[coord].animals['Herbivore'])
                        )
                    if coord == (3, 2):
                        left_coord[(3, 2)].append(
                            len(island.complete_map[coord].animals['Herbivore'])
                        )

        assert abs((np.average(up_coord[(2, 3)]) - 250)) < margin and \
               abs((np.average(right_coord[(3, 4)])) - 250) < margin and \
               abs((np.average(down_coord[(4, 3)])) - 250) < margin and \
               abs((np.average(left_coord[(3, 2)])) - 250) < margin
