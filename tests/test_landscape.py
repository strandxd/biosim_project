import pytest
import random
from biosim.landscape import Lowland, Highland, Desert, Water
from biosim.animal import Herbivore, Carnivore


class TestLandscape:
    @pytest.fixture(autouse=True)
    def cell_setup(self):
        self.default_init = {'age': 2, 'weight': 22, 'position': (2, 2)}
        self.species = {'Herbivore': Herbivore, 'Carnivore': Carnivore}
        self.list_of_carnivores = [self.species['Carnivore'](**self.default_init) for _ in range(4)]
        self.list_of_herbivores = [self.species['Herbivore'](**self.default_init) for _ in range(4)]

    def test_update_available_fodder(self):
        cell_lowland = Lowland()
        cell_lowland.update_available_fodder(5)
        target = 795
        assert cell_lowland.available_food == target

    @pytest.mark.parametrize('land_type, f_max_target',
                             [[Highland((2, 3)), 300.0],
                              [Lowland((2, 1)), 800.0],
                              [Desert((1, 8)), None],
                              [Water((4, 5)), None]])
    def test_initialize_land_types(self, land_type, f_max_target):
        """Test that the land type initializes with the correct amount of available food."""
        assert land_type.available_food == f_max_target

    def test_add_animals_to_cell(self):
        """Check to see if animals are correctly added to cell."""
        cell_lowland = Lowland()
        cell_total_number = cell_lowland.total_animals
        new_animal = self.species['Herbivore'](age=3, weight=25, position=(2, 2))
        cell_lowland.add_animals_to_cell(new_animal, new_animal.species)
        in_cell_animal = cell_lowland.animals['Herbivore'][0]

        assert in_cell_animal.age == new_animal.age and \
               cell_lowland.total_animals == cell_total_number + 1

    def test_decrease_total_animals(self):
        """Test that decrease in total animal counter happens correctly."""
        cell_lowland = Lowland()
        # Add 4 herbivores
        for herb in self.list_of_herbivores:
            cell_lowland.add_animals_to_cell(herb, 'Herbivore')

        total_animals = cell_lowland.total_animals
        cell_lowland.decrease_total_animals()

        assert cell_lowland.total_animals == total_animals - 1

    def test_update_animal_after_migration(self):
        """Test that animals who do not match the cell position are removed from species list"""
        # Add initial 6 herbivores
        num = 6
        animal_init_pos_herb = [self.species['Herbivore'](**self.default_init) for _ in range(num)]
        cell_lowland = Lowland((2, 2))  # initial pos
        for herb in animal_init_pos_herb:
            cell_lowland.add_animals_to_cell(herb, 'Herbivore')

        # Add one more, but with wrong position
        new_animal = self.species['Herbivore'](age=3, weight=25, position=(2, 3))
        cell_lowland.animals['Herbivore'].append(new_animal)
        cell_lowland.update_animals_after_migration()

        # Check that every herb has the same position and that the correct amount is in the list.
        assert all([herb.position == cell_lowland.position for herb in
                    cell_lowland.animals['Herbivore']]) and \
               len(cell_lowland.animals['Herbivore']) == num

    @pytest.mark.parametrize("available_food, F, target",
                             [[None, 0, None],
                              [800, 10, 760],
                              [6, 10, 0]])
    def test_feeding_herbivores(self, available_food, F, target):
        """Test that herbivore feeding updates available food correctly."""
        cell_lowland = Lowland()
        cell_lowland.available_food = available_food
        Herbivore.update_attributes({'F': F})

        for herb in self.list_of_herbivores:
            cell_lowland.add_animals_to_cell(herb, 'Herbivore')

        cell_lowland.feeding_herbivores()

        # Reset params
        Herbivore.reset_default_attribute_values()
        assert target == cell_lowland.available_food

    def test_feeding_carnivores(self, mocker):
        """Check that carnivore feeding updates weight correctly."""
        mocker.patch('random.random', return_value=0)
        num_herb = 10
        cell = Lowland()
        herb = [Herbivore(age=12, weight=2, position=(2, 2)) for _ in range(num_herb)]
        carn = Carnivore(age=20, weight=90, position=(2, 2))
        original_weight = carn.weight
        for animal in herb:
            cell.add_animals_to_cell(animal, animal.species)
        cell.add_animals_to_cell(carn, carn.species)

        cell.feeding_carnivores()

        assert cell.animals['Carnivore'][0].weight != original_weight

    def test_migrate_animals(self, mocker):
        """
        Check to see if correct information is added to the returned dictionary of migrate_animals.

        Potential positions from position (2, 2):
            (3, 2), (2, 3), (1, 2), (2, 1)
        """
        mocker.patch('random.random', return_value=0)  # This forces migration
        pos = (2, 2)
        cell = Highland(pos)
        cell.animals['Herbivore'].extend([Herbivore(2, 10, pos) for _ in range(5)])
        potentials = [(3, 2), (2, 3), (1, 2), (2, 1)]

        migration_dict = cell.migrate_animals()

        assert all((ani.position == pos and ani.species == 'Herbivore')
                   for ani in migration_dict['Animal']) and \
               all(pot_pos in potentials for pot_pos in migration_dict['Potential position'])

    @pytest.mark.parametrize("return_value,target,newborns_age_list",
                             [[0, 100, 50], [1, 50, 0]])
    def test_procreation(self, mocker, return_value, target, newborns_age_list):
        """Test procreation in a cycle."""
        mocker.patch('random.random', return_value=return_value)
        num = 25
        cell_lowland = Lowland()

        carnivores_in_local_cell = [Carnivore(age=12, weight=90,
                                              position=(2, 2)) for _ in range(num)]
        herbivores_in_local_cell = [Herbivore(age=14, weight=90,
                                              position=(2, 2)) for _ in range(num)]

        for carnivore in carnivores_in_local_cell:
            cell_lowland.add_animals_to_cell(carnivore, 'Carnivore')
        for herbivore in herbivores_in_local_cell:
            cell_lowland.add_animals_to_cell(herbivore, 'Herbivore')

        cell_lowland.procreation(1)
        animals_aged_0_herbivore = [i for i in cell_lowland.animals['Herbivore'] if i.age == 0]
        animals_aged_0_carnivore = [i for i in cell_lowland.animals['Carnivore'] if i.age == 0]
        newborns = animals_aged_0_carnivore + animals_aged_0_herbivore

        assert cell_lowland.total_animals == target and len(newborns) == newborns_age_list

    def test_aging(self):
        """Test that animals ages +1 as part of the annual cycle."""
        num = 2
        carnivores_in_local_cell = [Carnivore(age=12, weight=90,
                                              position=(2, 2)) for _ in range(num)]
        cell_lowland = Lowland()
        for carnivore in carnivores_in_local_cell:
            cell_lowland.add_animals_to_cell(carnivore, 'Carnivore')

        start_age = cell_lowland.animals['Carnivore'][0].age
        cell_lowland.aging()

        assert all([ani.age == start_age + 1 for ani in cell_lowland.animals['Carnivore']])

    def test_loss_of_weight(self):
        """Test that animals loose weight as part of the annual cycle."""
        num = 50
        carnivores_in_local_cell = [Carnivore(age=12, weight=90,
                                              position=(2, 2)) for _ in range(num)]
        cell_lowland = Lowland()
        for carnivore in carnivores_in_local_cell:
            cell_lowland.add_animals_to_cell(carnivore, 'Carnivore')

        animal = cell_lowland.animals['Carnivore'][0]
        weight = animal.weight
        weight_change = weight - (animal.eta * weight)

        cell_lowland.loss_of_weight()

        assert all([(ani.weight == weight_change and ani.weight < weight) for ani in
                    cell_lowland.animals['Carnivore']])

    def test_death(self):
        """Test that dead animals correctly updates number of animals in the cell."""
        herb = self.species['Herbivore'](2, 2, (2, 2))

        cell = Lowland((2, 2))
        cell.add_animals_to_cell(herb, herb.species)
        herb._death_status = True
        cell.death()

        assert cell.total_animals == 0

    def test_yearly_updates(self):
        """Test that yearly updates resets certain status settings and updates available food."""
        herb = self.species['Herbivore'](2, 2, (2, 2))
        cell = Lowland()
        cell.add_animals_to_cell(herb, herb.species)

        cell.available_food = 30
        herb.given_birth = True
        herb.migration_status = True

        cell.yearly_updates()

        assert not herb.given_birth and not herb.migration_status and \
               cell.available_food == cell.f_max

    @pytest.mark.parametrize('herb_only, num_herb_end, num_carn_end',
                             [[True, 5, 10],
                              [False, 5, 5]])
    def test_update_population(self, herb_only, num_herb_end, num_carn_end):
        """Test that the population is correctly updated without dead animals."""
        cell = Lowland((2, 2))
        cell.animals['Herbivore'].extend([Herbivore(2, 5, (2, 2)) for _ in range(10)])
        cell.animals['Carnivore'].extend([Carnivore(5, 4, (2, 2)) for _ in range(10)])

        # Set death status to true for half the population of each species
        for herb, carn in zip(cell.animals['Herbivore'][::2], cell.animals['Carnivore'][::2]):
            herb._death_status = True
            carn._death_status = True

        # When only herbivores updates, number of carnivores should stay unchanged. If not, they
        # are also updated.
        cell.update_population(herb_only=herb_only)

        assert len(cell.animals['Herbivore']) == num_herb_end \
               and len(cell.animals['Carnivore']) == num_carn_end

    def test_animal_sorting_herbivores(self):
        """Test that herbivores gets sorted by descending fitness."""
        cell = Lowland((2, 2))
        num = 20
        # Add herbivores with various fitness
        cell.animals['Herbivore'].extend([Herbivore(random.randint(10, 15), random.randint(5, 20),
                                                    (2, 2)) for _ in range(num)])

        cell.update_animal_sorting()
        list_of_herb = cell.animals['Herbivore']

        assert all([herb_left.fitness >= herb_right.fitness for herb_left, herb_right
                    in zip(list_of_herb[:], list_of_herb[1:])])

    @pytest.mark.parametrize('shuffle',
                             [False, True])
    def test_animal_sorting_carnivore(self, shuffle):
        """Test that list of carnivores gets shuffled."""
        cell = Lowland((2, 2))
        num = 50
        cell.animals['Carnivore'].extend([Carnivore(2, 5, (2, 2)) for _ in range(num)])
        carn_list_copy = cell.animals['Carnivore'].copy()

        if shuffle:
            cell.update_animal_sorting()
            assert cell.animals != carn_list_copy
        else:
            assert cell.animals['Carnivore'] == carn_list_copy
