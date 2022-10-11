import random

from .animal import Herbivore, Carnivore


class Landscape:
    """
    The landscape class controls the individual cells of the island. Land types are defined in
    separate classes, see ``Highland``, ``Lowland``, ``Desert`` and ``Water``.
    """
    total_animals = 0

    # Defined in respective land type classes.
    available_food = None
    f_max = None
    position = None
    legal_land_type = None

    @classmethod
    def update_attributes(cls, update_attributes_dict):
        """
        Update class attribute values from dictionary.

        Parameters
        ----------
        update_attributes_dict : dict
            Dictionary with class attribute name and value.
        """
        for attribute_name, new_value in update_attributes_dict.items():
            setattr(cls, attribute_name, new_value)

    def __init__(self):
        """
        Initialize landscape cell. Creates a dictionary with species names and a list to contain
        animal objects.

        Add a dictionary containing dicts that can keep track of potentially newborn babies.
        """
        self.animals = {'Herbivore': [], 'Carnivore': []}
        self._animal_babies = {'Herbivore': {'class type': Herbivore, 'number in cell': 0,
                                             'newborns': []},
                               'Carnivore': {'class type': Carnivore, 'number in cell': 0,
                                             'newborns': []}}

    def update_available_fodder(self, herb_eaten):
        """Reduces available food by the amount eaten by a herbivore."""
        self.available_food -= herb_eaten

    def add_animals_to_cell(self, animal, species):
        """
        Add a single animal to the cell.

        Parameters
        ----------
        animal : object
            Class instance of animal
        species : str
            Name of species
        """
        self.animals[species].append(animal)
        self.increase_total_animals()

    def increase_total_animals(self):
        """Increases total animal counter by 1."""
        self.total_animals += 1

    def decrease_total_animals(self):
        """Decreases total animal counter by 1."""
        self.total_animals -= 1

    def update_animals_after_migration(self):
        """Update animals after migration with those who match the current cell position."""
        for species, animal_list in self.animals.items():
            self.animals[species] = [ani for ani in animal_list if ani.position == self.position]

    def feeding_herbivores(self):
        """
        Feeding cycle for herbivores.

        Checks that available food on the given land type is not none (as this is default for land
        types with no food), and then determine how much food is available. If it is plenty of food,
        i.e. more food than the herbivore can eat, it will eat F. Otherwise it will eat the
        remainder of the available food.
        """
        for herb in self.animals['Herbivore']:
            if self.available_food is not None and herb.F <= self.available_food:
                herb.update_weight_post_eat()
                self.available_food -= herb.F
            elif self.available_food is not None and self.available_food > 0:
                herb.update_weight_post_eat(self.available_food)
                self.available_food -= self.available_food  # Amounts to 0
            else:
                # Breaks if no food is available. Prevents unnecessary looping
                break

    def feeding_carnivores(self):
        """Feeding cycle for carnivores. See ``hunt`` in ``Animal``."""
        for carn in self.animals['Carnivore']:
            carn.hunt(self.animals['Herbivore'])

    def migrate_animals(self):
        """
        Get information from animals that passes migration check. Store current position as well as
        potential position in case the animal tries migrating to an illegal cell, determined by
        ``Island``. Animal object and species name are also saved to give as input to
        ``add_animals_to_cell`` in the potential new cell.

        Returns
        -------
        dict
            Dictionary containing information about all the animals that *could* migrate
            (still need to check legal moves in map).
        """
        migration_animals = {'Current position': [],
                             'Potential position': [],
                             'Animal': [],
                             'Species': []}

        for species, animal_list in self.animals.items():
            for animal in animal_list:
                if animal.check_if_animal_migrates():
                    current_position, potential_position = animal.choose_migration_move()
                    migration_animals['Current position'].append(current_position)
                    migration_animals['Potential position'].append(potential_position)
                    migration_animals['Animal'].append(animal)
                    migration_animals['Species'].append(animal.species)

        return migration_animals

    def procreation(self, year):
        """
        Simulate procreation of animals.

        Reset the list of babies for each method call and get access to the number of animals per
        species present in the cell (>2 are needed to give birth). Check if the animal type gives
        birth, and if they do, add the new animals to the species list and increase the counter.

        Parameters
        ----------
        year : int
            Current year of the simulation.
        """
        # Empty the list of animals when called again (inside new cell)
        for species in self._animal_babies.keys():
            self._animal_babies[species]['newborns'] = []

        self._animal_babies['Herbivore']['number'] = len(self.animals['Herbivore'])
        self._animal_babies['Carnivore']['number'] = len(self.animals['Carnivore'])

        for species, animal_list in self.animals.items():
            for animal in animal_list:
                if type(animal) == self._animal_babies[species]['class type']:
                    animals_in_cell = self._animal_babies[species]['number']
                    if new_baby := animal.give_birth(animals_in_cell, year):
                        self._animal_babies[species]['newborns'].append(new_baby)

                if animal.given_birth:
                    self.increase_total_animals()

        # Add babies to list of animals in the cell
        self.animals['Herbivore'] += self._animal_babies['Herbivore']['newborns']
        self.animals['Carnivore'] += self._animal_babies['Carnivore']['newborns']

    def aging(self):
        """Aging cycle for animals in a cell."""
        for species, animal_list in self.animals.items():
            self.animals[species] = [ani.age_increase() for ani in animal_list]

    def loss_of_weight(self):
        """Weight loss cycle for animals in a cell."""
        for species, animal_list in self.animals.items():
            self.animals[species] = [ani.yearly_weight_update() for ani in animal_list]

    def death(self):
        """Death cycle for animals in a cell."""
        for species, animal_list in self.animals.items():
            for animal in animal_list:
                animal.update_death_status()
                if animal.death_status:
                    self.decrease_total_animals()

    def yearly_updates(self):
        """
        Yearly resets for cell and animals in the cell.

        In the beginning of each year certain attributes needs to be reset to original values.
         * Food regenerates in cell. (Still None if no food is available)
         * Animals' birth status is reset, they can now attempt to procreate again.
         * Animals' migration status is reset, they can now attempt to migrate again.
        """
        self.available_food = self.f_max

        for species, animal_list in self.animals.items():
            for animal in animal_list:
                animal.given_birth = False
                animal.migration_status = False

    def update_population(self, herb_only=False):
        """
        Updates how many animals there are of each species by removing dead ones. This has to happen
        after hunting, which is why an option to only sort herbivores is present.

        Parameters
        ----------
        herb_only : bool, default=False
            Whether to only sort herbivores or all species.
        """
        if herb_only:
            self.animals['Herbivore'] = [herb for herb in self.animals['Herbivore'] if
                                         not herb.death_status]
        else:
            # Remove animals that are dead. I.e. keep animals that are not dead
            for animal_type, animal_list in self.animals.items():
                self.animals[animal_type] = [ani for ani in animal_list if not ani.death_status]

    def update_animal_sorting(self):
        """Updates sort order. Herbivores based on fitness, carnivores randomly shuffled"""
        for animal_type in self.animals.keys():
            if animal_type == 'Herbivore':
                self.animals[animal_type] = sorted(self.animals[animal_type],
                                                   key=lambda animal: animal.fitness, reverse=True)
            else:
                random.shuffle(self.animals[animal_type])

    def get_landscape_letter(self):
        """Get first letter for given land type"""
        return type(self).__name__[0]


class Lowland(Landscape):
    """
    Lowland land type. Contains typically the most available fodder and is considered a legal land
    type to stay in.
    """

    f_max = 800.0
    legal_land_type = True

    def __init__(self, position=None):
        Landscape.__init__(self)
        self.position = position

        self.available_food = self.f_max


class Highland(Landscape):
    """
    Highland land type. Contains typically the second most available fodder and is considered a
    legal land type to stay in.
    """
    f_max = 300.0
    legal_land_type = True

    def __init__(self, position=None):
        Landscape.__init__(self)
        self.position = position

        self.available_food = self.f_max


class Desert(Landscape):
    """
    Desert land type. Contains typically no fodder and is considered a legal land type to stay in.
    """
    f_max = None
    legal_land_type = True

    def __init__(self, position=None):
        Landscape.__init__(self)
        self.position = position

        self.available_food = self.f_max


class Water(Landscape):
    """
    Water land type. Contains typically no fodder and is considered an illegal land type to stay in.
    """
    f_max = None
    legal_land_type = False

    def __init__(self, position=None):
        Landscape.__init__(self)
        self.position = position

        self.available_food = self.f_max
