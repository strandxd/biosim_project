"""
Testing of the animal module.
"""
import pytest
from pytest import approx
import math
from scipy.stats import normaltest
from biosim.animal import Herbivore, Carnivore


class TestClassMethods:
    @pytest.fixture(autouse=True)
    def setup_animal(self):
        self.species = {'Herbivore': Herbivore,
                        'Carnivore': Carnivore}
        self.default_init = {'age': 2, 'weight': 25, 'position': (2, 3)}

    def test_get_attributes(self):
        """Test that we can use the get_attributes class method to store class attributes in dict"""
        target = {'w_birth': 6.0,
                  'sigma_birth': 1.0,
                  'beta': 0.75,
                  'eta': 0.125,
                  'a_half': 40.0,
                  'phi_age': 0.3,
                  'w_half': 4.0,
                  'phi_weight': 0.4,
                  'mu': 0.4,
                  'gamma': 0.8,
                  'zeta': 3.5,
                  'xi': 1.1,
                  'omega': 0.8,
                  'F': 50.0,
                  'DeltaPhiMax': 10.0,
                  'species': 'Carnivore'}

        carnivore_attr = Carnivore.get_attributes()
        key_attr_test, value_attr_test = list(carnivore_attr.keys()), list(carnivore_attr.values())
        key_target, value_target = list(target.keys()), list(target.values())

        # Checks to see that all keys and values are in the target dictionary, also that length is
        # the same.
        assert all([key for key in key_attr_test if key in key_target]) and \
               all([value for value in value_attr_test if value in value_target]) and \
               len(key_attr_test) == len(key_target) and \
               len(value_attr_test) == len(value_target)

    @pytest.mark.parametrize('invalid_param',
                             [{'species': 'cow'},
                              {'eta': 2},
                              {'w_birth': -3},
                              {'DeltaPhiMax': 0},
                              {'wrong_name': 4}])
    def test_change_class_attributes_fail(self, invalid_param):
        """Test that invalid parameters for class attributes raises ValueError."""
        herb = self.species['Carnivore'](**self.default_init)

        with pytest.raises(ValueError):
            herb.update_attributes(invalid_param)

    @pytest.mark.parametrize('param_name, param_value',
                             [['w_birth', 4],
                              ['zeta', 3],
                              ['F', 13],
                              ['phi_age', 19]])
    def test_change_class_attributes_pass(self, param_name, param_value):
        """Test that valid parameters for class attributes changes the values."""
        Herbivore.update_attributes({param_name: param_value})
        herb = self.species['Herbivore'](**self.default_init)
        herb_attr = herb.get_attributes()

        assert herb_attr[param_name] == param_value


class TestAnimalBasics:

    @pytest.fixture
    def setup_params(self, request):
        Herbivore.update_attributes(request.param)
        Carnivore.update_attributes(request.param)
        self.param_request = request.param
        yield
        Herbivore.reset_default_attribute_values()
        Carnivore.reset_default_attribute_values()

    @pytest.fixture(autouse=True)
    def setup_animal(self):
        self.default_init = {'age': 2, 'weight': 22, 'position': (2, 3)}
        self.species = {'Herbivore': Herbivore,
                        'Carnivore': Carnivore}

    @pytest.mark.parametrize('age, weight, pos',
                             [[-2, 10, (2, 2)],  # Age is wrong
                              [5, -2, (2, 2)],  # Weight is wrong
                              [4, 1, [2, 4]]])  # Position is wrong
    def test_init_mistakes(self, age, weight, pos):
        """Test that invalid initialization input raises ValueError"""
        with pytest.raises(ValueError):
            Carnivore(age, weight, pos)

    def test_repr(self):
        """Test that __repr__ method produces correct output."""
        species_name = 'Herbivore'
        age = 5
        weight = 12
        pos = (4, 2)
        herb = self.species[species_name](age, weight, pos)

        assert herb.__repr__() == f'{species_name}({age}, {weight}, {pos})'

    def test_age_increase(self):
        """Test to see if the yearly age increase updates correctly"""
        animal = self.species['Carnivore'](**self.default_init)
        curr_age = animal.age
        target_age = curr_age + 1
        animal.age_increase()

        assert animal.age == target_age

    def test_annual_given_birth_status_update(self):
        """Test to see if given birth status updates to False"""
        herb = self.species['Herbivore'](**self.default_init)
        herb.given_birth = True
        herb.annual_given_birth_status_update()

        assert not herb.given_birth

    @pytest.mark.parametrize('pos', [(2, 2), (4, 5), (1, 0), (1, 4)])
    def test_update_position(self, pos):
        """Test to see if position updates correctly"""
        animal = self.species['Herbivore'](**self.default_init)
        animal.update_position(pos)

        assert animal._position == pos

    @pytest.mark.parametrize('pos', [(2, 2, 1), 'wrong', 2])
    def test_update_position_error(self, pos):
        """Test to see if wrong position updates raises ValueError"""
        herb = Herbivore(5, 5, (2, 2))

        with pytest.raises(ValueError):
            herb.update_position(pos)

    @pytest.mark.parametrize('setup_params',
                             [{'phi_age': 4,
                               'a_half': 13,
                               'phi_weight': 4,
                               'w_half': 2}], indirect=True)
    def test_fitness_update(self, setup_params):
        """Test that fitness is calculated correctly."""
        age = 15
        weight = 10
        phi_age, a_half = self.param_request['phi_age'], self.param_request['a_half']
        phi_weight, w_half = self.param_request['phi_weight'], self.param_request['w_half']
        herb = self.species['Herbivore'](age, weight, (2, 2))

        target_fitness = (1 / (1 + math.exp(phi_age * (age - a_half)))) * \
                         (1 / (1 + math.exp(-phi_weight * (weight - w_half))))

        # Fitness gets updated when herb is initialized, but to make it clear
        herb.fitness_update()
        assert approx(herb.fitness) == approx(target_fitness)

    def test_fitness_update_negative_weight(self):
        """Tests weight = 0 updates fitness to 0."""
        herb = self.species['Herbivore'](**self.default_init)
        herb._weight = 0
        herb.fitness_update()

        assert herb.fitness == 0

    @pytest.mark.parametrize("food_eaten",
                             [10, None, None, 15])
    def test_update_weight_post_eat(self, food_eaten):  #
        """Test that weight updates correctly after eating."""
        animal = self.species['Herbivore'](**self.default_init)
        if food_eaten:
            target_weight = animal.weight + (animal.beta * food_eaten)
        else:
            target_weight = animal.weight + (animal.beta * animal.F)

        animal.update_weight_post_eat(food_eaten)

        assert animal.weight == target_weight

    def test_yearly_weight_update(self):
        """Test if yearly weight decrease updates correctly."""
        animal = self.species['Carnivore'](**self.default_init)
        weight_decrease = animal.eta * animal.weight
        target_weight = animal.weight - weight_decrease
        animal.yearly_weight_update()

        assert animal.weight == target_weight

    @pytest.mark.parametrize('dead, eaten, rand_value, weight_reduce',
                             [[True, True, 1, 0],
                              [True, False, 1, 15],
                              [True, False, 0, 0]])
    def test_update_death_status(self, mocker, dead, eaten, rand_value, weight_reduce):
        """Tests that death status updates correctly."""
        mocker.patch('random.random', return_value=rand_value)
        herb = self.species['Herbivore'](2, 10, (2, 2))

        # Reduces weight to force the animal weight below 0
        herb._weight -= weight_reduce
        herb.update_death_status(eaten=eaten)

        assert herb.death_status == dead


class TestBirthRelated:
    """
    When testing birth conditions we essentially have these four conditions that has to fail or
    pass. In order to do so we will manipulate attributes, both class and instance specific.
    Condition 1: rand_num < birth_prob:
                 Passed by setting mocker value. Rand_num 0 = fail, rand_num 1 = pass
    Condition 2: animal weight >= scaled_birth_weight:
                 Passed by setting initial weight. Low = fail, high = pass.
                 Herbivore scaled_birth_weight = 3.5 * (8.0 + 1.5) = 33.25 (highest possible birth
                 weight with default parameters, so any greater weight passes)
    Condition 3: not (already given birth):
                 Passed by defining animal given birth status.
                 Given_birth True = fail, given_birth False/None = pass (default init value).
    Condition 4: animal weight >= animal weight loss:
                 Passed by setting initial weight. Low = fail,high = pass. High weight gives
                 guarantee for passing.
    """
    @pytest.fixture
    def setup_params(self, request):
        Herbivore.update_attributes(request.param)
        Carnivore.update_attributes(request.param)
        self.param_request = request.param
        yield
        Herbivore.reset_default_attribute_values()
        Carnivore.reset_default_attribute_values()

    @pytest.fixture(autouse=True)
    def setup_animal(self):
        self.default_init = {'age': 4, 'weight': 15, 'position': (4, 3)}
        self.species = {'Herbivore': Herbivore,
                        'Carnivore': Carnivore}

    def test_calculate_birth_weight(self):
        """Test H0: Birth weight follows gaussian distribution"""
        animal = self.species['Carnivore'](**self.default_init)
        birth_weights = [animal._calculate_birth_weight() for _ in range(1000)]
        alpha = 0.05
        _, p_value = normaltest(birth_weights)

        assert p_value > alpha

    @pytest.mark.parametrize('setup_params', [{'zeta': 0,
                                               'w_birth': 4,
                                               'sigma_birth': 0}], indirect=True)
    def test_check_birth_conditions_positive(self, mocker, setup_params):
        """Check that animal birth happens correctly."""
        mocker.patch('random.random', return_value=0)
        parent = self.species['Herbivore'](4, 100, (2, 2))
        N = 2
        year = 2
        w_birth = self.param_request['w_birth']
        baby_animal = parent.give_birth(N, year)

        assert baby_animal.age == 0 and baby_animal.weight == w_birth and \
               baby_animal.position == parent.position

    @pytest.mark.parametrize("N, year, zeta, w_birth, sigma_birth, xi, birth_year, r_value",
                             [[100, 2, 0, 0, 0, 0, None, 1],  # Failing condition 1
                              [200, 2, 1000, 5, 0.1, 0, None, 0],  # Failing condition 2
                              [100, 2, 0, 0, 0, 0, 2, 0],  # Failing condition 3
                              [100, 2, 0, 5, 0, 1000, None, 0]])  # Failing condition 4
    def test_check_birth_negative(self, mocker, N, year, zeta, w_birth, sigma_birth, xi,
                                  birth_year, r_value):
        """Test that negative birth conditions return None (as in no animal being born)."""
        mocker.patch('random.random', return_value=r_value)
        animal = self.species['Herbivore'](**self.default_init)
        animal.zeta = zeta
        animal.w_birth = w_birth
        animal.sigma_birth = sigma_birth
        animal.xi = xi
        animal._given_birth_year = birth_year

        new_animal = animal.give_birth(N, year)

        # Making sure that values are reset to avoid potential trouble
        Herbivore.reset_default_attribute_values()
        assert new_animal is None


class TestMigrationRelated:
    @pytest.fixture(autouse=True)
    def setup_animal(self):
        self.species = {'Herbivore': Herbivore, 'Carnivore': Carnivore}
        self.default_init = {'age': 4, 'weight': 15, 'position': (4, 3)}

    def test_annual_migration_status(self):
        """Test that migration status resets to False."""
        animal = self.species['Herbivore'](**self.default_init)
        animal.migration_status = True
        animal.annual_migration_status_update()

        assert not animal.migration_status

    def test_check_if_animal_migrates(self, mocker):
        """Test that animals can pass probability check for migration."""
        mocker.patch('random.random', return_value=0)
        animal = self.species['Herbivore'](**self.default_init)
        animal.migration_status = False
        a1 = animal.check_if_animal_migrates()
        assert a1

    @pytest.mark.parametrize("starting_position, test_position, potential_position",
                             [[(2, 2), (2, 2), [(1, 2), (2, 1), (2, 3), (3, 2)]],
                              [(3, 3), (200, 5), [(2, 3), (3, 2), (3, 4), (4, 3)]]])
    def test_choose_migration_move(self, starting_position, test_position, potential_position):
        """Test that choose_migration_move returns current and potential position correctly."""
        animal = self.species['Herbivore'](**self.default_init)
        animal._position = starting_position
        current_position, animal_potential_position = animal.choose_migration_move()

        animal._position = test_position

        if current_position == animal._position:
            assert animal_potential_position in potential_position
        else:
            assert current_position != animal._position


class TestHunt:
    @pytest.fixture(autouse=True)
    def setup_animal(self):
        self.species = {'Herbivore': Herbivore, 'Carnivore': Carnivore}
        self.default_init = {'age': 4, 'weight': 15, 'position': (4, 3)}

    @pytest.mark.parametrize('weight_prey, eaten_in_total, target_return',
                             [[15, 45, 5],
                              [27, 4, 27]])
    def test_check_excessive_eating(self, weight_prey, eaten_in_total, target_return):
        """Check if overeating returns remainder to get full or else the weight of prey."""
        carn = self.species['Carnivore'](**self.default_init)

        assert carn.check_excessive_eating(weight_prey, eaten_in_total) == target_return

    @pytest.mark.parametrize('death_status, herb_fitness, delta_phi_max, rand_val, herb_weight,'
                             'carn_weight, target_weight',
                             [[True, 0.2, 10, 0, 10, 25, 25],  # No weight change (dead animal)
                              [False, 0.99, 10, 0, 10, 25, 25],  # No weight change (prey fit>carn)
                              [False, 0.2, 10, 0, 10, 25, 32.5],  # Weight change +0.75*10
                              [False, 0.2, 0.01, 1, 15, 25, 36.25],  # Weight change +0.75*25
                              [False, 0.2, 10, 0, 85, 25, 62.5]])  # Weight change +0.75*50
    def test_hunt(self, mocker, death_status, herb_fitness, delta_phi_max, rand_val, herb_weight,
                  carn_weight, target_weight):
        """
        Test to see if hunting method works the way it should. The four first tests are for 1
        herbivore, the last is for multiple to check if it breaks out of the loop (i.e. stops
        hunting) if it is full.

        With a beta value of 0.75 it will gain weight equal to 0.75*weight of prey.
        """
        mocker.patch('random.random', return_value=rand_val)
        Carnivore.DeltaPhiMax = delta_phi_max
        list_of_single_prey = [self.species['Herbivore'](4, herb_weight, (2, 2))]

        carn = self.species['Carnivore'](5, carn_weight, (3, 2))

        for herb in list_of_single_prey:
            herb._death_status = death_status
            herb._fitness = herb_fitness
        carn._fitness = 0.8
        carn.hunt(list_of_single_prey)
        if carn_weight != target_weight or death_status:
            herb_eaten = True
        else:
            herb_eaten = False

        # To avoid potential trouble
        Carnivore.reset_default_attribute_values()
        # Check that carnivore gains correct weight on kill and herbivores updates status
        assert carn.weight == target_weight and list_of_single_prey[0].death_status == herb_eaten
