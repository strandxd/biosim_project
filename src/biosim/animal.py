import math
import random


class Animal:
    """
    The animal class contains methods related to properties of animals. Specific class attributes
    are defined by the individual animals themselves, see ``Herbivore`` and ``Carnivore``.

    Note that methods that don't apply to both animals still occur in this class, e.g. hunt. Our
    reasoning is that new animals who also hunt carnivores in the same manner may use this.
    """

    # Defined in respective animal species classes.
    w_birth = None
    sigma_birth = None
    beta = None
    eta = None
    a_half = None
    phi_age = None
    w_half = None
    phi_weight = None
    mu = None
    gamma = None
    zeta = None
    xi = None
    omega = None
    F = None
    DeltaPhiMax = None
    species = None

    @classmethod
    def get_attributes(cls):
        """Gather class attributes in a dictionary."""
        attributes = {name: value for name, value in cls.__dict__.items() if
                      not (name.startswith('__'))
                      and not isinstance(cls.__dict__[name], classmethod)
                      and not callable(cls.__dict__[name])}
        return attributes

    @classmethod
    def update_attributes(cls, update_attributes_dict):
        """
        Update class attribute values from dictionary. Raise ValueError for mistakes in input.

        Note: Be aware that changes to class attributes will happen until failure. E.g. if key/value
        #5 in the update_attributes_dict raises a ValueError, all changes until that point will
        still be in place for the class.

        Parameters
        ----------
        update_attributes_dict : dict
            Dictionary with class attribute name and value.
        """
        attr = cls.get_attributes()

        for attribute_name, new_value in update_attributes_dict.items():
            if attribute_name not in list(attr.keys()):
                raise ValueError('Invalid attribute name.')

            if attribute_name == 'species':
                raise ValueError('Can not change type of species.')
            elif attribute_name == 'eta' and new_value > 1:
                raise ValueError('Attribute value for eta has to be 0 <= x <= 1.')
            elif attribute_name == 'DeltaPhiMax' and new_value <= 0:
                raise ValueError('Attribute value for DeltaPhiMax has to be >0.')
            elif new_value < 0:
                raise ValueError('Attribute values <0 are not allowed.')

            setattr(cls, attribute_name, new_value)

    def __init__(self, age, weight, position):
        if age < 0:
            raise ValueError('Invalid parameter input. Age can not be negative.')
        if weight <= 0:
            raise ValueError('Invalid parameter input. Weight must be strictly positive, i.e. >0.')
        if type(position) is not tuple or len(position) != 2:
            raise ValueError('Invalid parameter input. Position must be tuple with 2 entries. '
                             'E.g.: (2, 2).')

        self._age = age
        self._weight = weight
        self._position = position

        self._fitness = None
        self.fitness_update()

        self.given_birth = False
        self._given_birth_year = None
        self._death_status = False
        self._birth_weight_baby = None
        self._weight_loss_birth = None

        # Migration
        self._migration_map = {'Up': {'row': -1, 'col': 0},
                               'Right': {'row': 0, 'col': 1},
                               'Down': {'row': 1, 'col': 0},
                               'Left': {'row': 0, 'col': -1}}
        self.migration_status = False
        self._migration_moves = list(self._migration_map.keys())

    def __repr__(self):
        """Represent the given class. Example: Herbivore(5, 15, (3, 2))"""
        return f'{self.species}({self._age}, {self._weight}, {self._position})'

    def age_increase(self):
        """
        Annual increase of age. Fitness updates as age changes.

        Returns
        -------
        object
            Updated age and fitness of class instance
        """
        self._age += 1
        self.fitness_update()
        return self

    def yearly_weight_update(self):
        """
        Yearly weight update. Fitness updates as weight changes.
        Note: Sets weight to 0 if it becomes negative, because such a value is meaningless. Do not
        see how this could happen in the current code structure unless bugs appear.

        Returns
        -------
        object
            Updated weight and fitness of class instance
        """
        self._weight -= self.eta * self._weight
        self._weight = 0 if self._weight < 0 else self._weight
        # Update fitness after weight gain
        self.fitness_update()

        return self

    def update_death_status(self, eaten=False):
        """
        Updating the animal death status. Remains unchanged if no if-statements are passed.

        Parameters
        ----------
        eaten : bool
            True if status killed during hunt, else False.
        """
        if eaten or self._death_status:
            self._death_status = True
        else:
            prob_death = self.omega * (1 - self._fitness)
            rand_num = random.random()
            probability_condition = rand_num < prob_death

            if probability_condition or self._weight <= 0:
                self._death_status = True

    def update_position(self, pos):
        """Updates position to input"""
        if type(pos) is not tuple or len(pos) != 2:
            raise ValueError('Invalid position update. Position must be tuple with 2 entries. '
                             'E.g.: (2, 2).')

        self._position = pos

    def annual_migration_status_update(self):
        """Resets the migration status to False. Should happen at restart of new cycle, making sure
        they can migrate again."""
        self.migration_status = False

    def annual_given_birth_status_update(self):
        """Resets given birth status to False. Should happen at restart of new cycle, making sure
        they can give birth again."""
        self.given_birth = False

    def check_if_animal_migrates(self):
        r"""
        Checking if an animal should migrate. Every animal that hasn't yet migrated will have a
        chance of migration. Migration status is set to True as every animal only gets one chance
        to migrate per year. Probability of migration:

        .. math::
            \mu \times \Phi

        Returns
        -------
        bool
            False if animal already migrated this cycle or doesn't pass probability check. True
            otherwise.
        """
        # Prevents already migrated animals to migrate multiple times
        if self.migration_status:
            return False
        else:
            migrate_prob = self.mu * self._fitness
            rand_num = random.random()
            self.migration_status = True

            if rand_num < migrate_prob:
                return True
            else:
                return False

    def choose_migration_move(self):
        """
        Choose a migration move between "up", "right", "down", "left" (all equal probability).
        Update a potential position based on the given move. This new position has to be verified
        by the map (``Island class``) as a legal move. Return therefore both the current position
        and the potential position. Current position is then chosen if the potential position is an
        illegal move (goes off map (coord e.g.: (0, 1)) or goes into water).

        Returns
        -------
        tuple, tuple
            The current position and potential position
        """
        # Shuffle list containing "up", "right", "down", "left" and choose first element.
        # Do this to simulate random choice of 1/4.
        random.shuffle(self._migration_moves)
        move = self._migration_moves[0]

        # Update position based on rules from dictionary
        row, col = self._position
        row += self._migration_map[move]['row']
        col += self._migration_map[move]['col']
        potential_position = (row, col)

        # Self.position is the current position. Potential position needs to be checked if legal
        return self._position, potential_position

    def _calculate_birth_weight(self):
        """
        Calculates an estimation of the birth weight from a normal distribution.

        Returns
        -------
        int
            Birth weight of animal
        """
        self._birth_weight_baby = random.normalvariate(self.w_birth, self.sigma_birth)
        return self._birth_weight_baby

    def _already_given_birth_year(self, year):
        """
        Check if the animal has given birth in the current year.
        Note: In the current code structure this code does nothing as birth is only checked once
        a year. Convenient if yearly cycle happens multiple times in the future.

        Parameters
        ----------
        year : int
            Current year

        Returns
        -------
        bool
            True if the animal has already given birth this current year, else False.
        """
        if self._given_birth_year is not None and self._given_birth_year == year:
            return True

        return False

    def _check_birth_conditions(self, N, year):
        """
        Check various conditions for giving birth.

        Parameters
        ----------
        N : int
            Number of animals of the same species in a cell
        year : int
            Current year in the simulation

        Returns
        -------
        bool
            True if all conditions are fulfilled, else False.
        """
        birth_prob = min(1, self.gamma * (N - 1) * self._fitness)
        rand_num = random.random()

        scaled_birth_weight = self.zeta * (self.w_birth + self.sigma_birth)
        self.weight_loss = self.xi * self._calculate_birth_weight()

        # Check conditions
        condition_1 = rand_num < birth_prob
        condition_2 = self._weight >= scaled_birth_weight
        condition_3 = not (self._already_given_birth_year(year))
        condition_4 = self._weight >= self.weight_loss

        if condition_1 and condition_2 and condition_3 and condition_4:
            return True
        else:
            return False

    def give_birth(self, N, year):
        r"""
        Give birth to an animal of the same species if conditions are met.
        For birth conditions to be met:

        .. math::
            \begin{gather}
                \textit{random number} < \textit{min}(1, \gamma \times \Phi \times (N-1)) \\
                w \ge \zeta \times (w_{birth} + \sigma_{birth}) \\
                \textit{not (already given birth)} \\
                w \ge \xi \times w \sim \mathcal{N}(w_{birth}, \sigma_{birth})
            \end{gather}

        Parameters
        ----------
        N : int
            Number of animals of the same species in a cell
        year : int
            Current year

        Returns
        -------
        object, bool
            New class instance of species type if conditions are met, else False.
        """
        if self._check_birth_conditions(N, year):  # Calculates conditions
            self._weight -= self.weight_loss
            self.given_birth = True
            self._given_birth_year = year

            return type(self)(age=0, weight=self._birth_weight_baby, position=self._position)
        else:
            self.given_birth = False
            return None

    def fitness_update(self):
        r"""
        Updates fitness of the animal according to formula.

        .. math::
            \Phi =
            \begin{cases}
                0 & w < 0 \\
                q^+(a, a_\frac{1}{2}, \phi_{_age}) \times q^-(w, w_\frac{1}{2}, \phi_{weight})
                & else
            \end{cases}

        where

        .. math::
            q^\pm(x, x_\frac{1}{2}, \phi) = \frac{1}{1 + e^{\pm \phi(x-x_\frac{1}{2})}}
        """
        if self._weight > 0:
            q_plus = 1 / (1 + math.exp(self.phi_age * (self._age - self.a_half)))

            q_minus = 1 / (1 + math.exp(-self.phi_weight * (self._weight - self.w_half)))
            phi = q_plus * q_minus
            self._fitness = phi
        else:
            self._fitness = 0

    def update_weight_post_eat(self, food_eaten=None):
        r"""
        Updates the animal weight after feeding. Updated according to formula:

        .. math::
            \beta \times \textit{food}

        Parameters
        ----------
        food_eaten : int
            Amount of food eaten. Translates to weight gain
        """
        if food_eaten is None:
            self._weight += self.beta * self.F
        else:
            self._weight += self.beta * food_eaten

        # Update fitness after weight gain
        self.fitness_update()

    def check_excessive_eating(self, weight_prey, eaten_in_total):
        """
        Check to see if weight gain exceeds desired amount of food to be eaten in total (F).

        Parameters
        ----------
        weight_prey : int
            The weight of pray to be eaten
        eaten_in_total : int
            The total amount already eaten

        Returns
        -------
        int
            Weight of pray if the potential weight gain doesn't exceed F. Otherwise the remained
            to reach F.
        """
        potential_weight_gain = weight_prey + eaten_in_total

        # If the potential weight gain exceeds the desired amount it will return the amount it needs
        # to be full. The rest goes to waste
        if potential_weight_gain > self.F:
            return self.F - eaten_in_total
        else:
            return weight_prey

    def hunt(self, list_of_prey):
        r"""
        Loops through a list of prey sorted by ascending fitness. Hunter gains weight based on
        weight from prey. If the hunter eats more than it desires (F), it will only gain weight
        based on what's missing to be satisfied.

        Kill probability from hunt:

        .. math::
            p =
            \begin{cases}
                0 & \textit{if } \Phi_{carn} \le \Phi_{herb} \\
                \frac{\Phi_{carn} - \Phi_{herb}}{\Delta\Phi_{max}}
                & \textit{if } 0 < \Phi_{carn} - \Phi_{herb} < \Delta\Phi_{max} \\
                1 & \textit{otherwise}
            \end{cases}

        Parameters
        ----------
        list_of_prey : list
            A list containing prey to be hunted
        """
        eaten_in_total = 0
        herbivores_hunting_order = sorted(list_of_prey, key=lambda animal: animal.fitness,
                                          reverse=False)

        # Note: Important that eaten_in_total gets updated AFTER check_excessive_eating
        for prey in herbivores_hunting_order:
            if prey.death_status:
                continue
            elif self._fitness <= prey.fitness:
                continue
            elif 0 < self._fitness - prey.fitness < self.DeltaPhiMax:
                hunting_prob = (self._fitness - prey.fitness) / self.DeltaPhiMax
                rand_num = random.random()
                if rand_num < hunting_prob:
                    weight_gain = self.check_excessive_eating(prey.weight, eaten_in_total)
                    eaten_in_total += prey.weight
                    self.update_weight_post_eat(weight_gain)
                    prey.update_death_status(eaten=True)
            else:
                weight_gain = self.check_excessive_eating(prey.weight, eaten_in_total)
                eaten_in_total += prey.weight
                self.update_weight_post_eat(weight_gain)
                prey.update_death_status(eaten=True)

            if eaten_in_total >= self.F:
                break

    @property
    def age(self):
        return self._age

    @property
    def weight(self):
        return self._weight

    @property
    def position(self):
        return self._position

    @property
    def fitness(self):
        return self._fitness

    @property
    def death_status(self):
        return self._death_status


class Herbivore(Animal):
    """
    Herbivore animal class. Consists of specific class attributes related to the given species.
    """

    w_birth = 8.0
    sigma_birth = 1.5
    beta = 0.9
    eta = 0.05
    a_half = 40.0
    phi_age = 0.6
    w_half = 10
    phi_weight = 0.1
    mu = 0.25
    gamma = 0.2
    zeta = 3.5
    xi = 1.2
    omega = 0.4
    F = 10.0
    species = 'Herbivore'

    @classmethod
    def reset_default_attribute_values(cls):
        cls.w_birth = 8.0
        cls.sigma_birth = 1.5
        cls.beta = 0.9
        cls.eta = 0.05
        cls.a_half = 40.0
        cls.phi_age = 0.6
        cls.w_half = 10
        cls.phi_weight = 0.1
        cls.mu = 0.25
        cls.gamma = 0.2
        cls.zeta = 3.5
        cls.xi = 1.2
        cls.omega = 0.4
        cls.F = 10.0
        cls.species = 'Herbivore'

    def __init__(self, age, weight, position):
        Animal.__init__(self, age, weight, position)


class Carnivore(Animal):
    """
    Carnivore animal class. Consists of specific class attributes related to the given species.
    """

    w_birth = 6.0
    sigma_birth = 1.0
    beta = 0.75
    eta = 0.125
    a_half = 40.0
    phi_age = 0.3
    w_half = 4.0
    phi_weight = 0.4
    mu = 0.4
    gamma = 0.8
    zeta = 3.5
    xi = 1.1
    omega = 0.8
    F = 50.0
    DeltaPhiMax = 10.0
    species = 'Carnivore'

    @classmethod
    def reset_default_attribute_values(cls):
        cls.w_birth = 6.0
        cls.sigma_birth = 1.0
        cls.beta = 0.75
        cls.eta = 0.125
        cls.a_half = 40.0
        cls.phi_age = 0.3
        cls.w_half = 4.0
        cls.phi_weight = 0.4
        cls.mu = 0.4
        cls.gamma = 0.8
        cls.zeta = 3.5
        cls.xi = 1.1
        cls.omega = 0.8
        cls.F = 50.0
        cls.DeltaPhiMax = 10.0
        cls.species = 'Carnivore'

    def __init__(self, age, weight, position):
        Animal.__init__(self, age, weight, position)
