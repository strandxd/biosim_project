"""
Graphics used to visualize simulation of biosim project.

Code based on randvis project by Hans Ekkehard Plesser.

:mod:`randvis.graphics` provides graphics support for RandVis.

.. note::
   * This module requires the program ``ffmpeg`` or ``convert``
     available from `<https://ffmpeg.org>` and `<https://imagemagick.org>`.
   * You can also install ``ffmpeg`` using ``conda install ffmpeg``
   * You need to set the  :const:`_FFMPEG_BINARY` and :const:`_CONVERT_BINARY`
     constants below to the command required to invoke the programs
   * You need to set the :const:`_DEFAULT_FILEBASE` constant below to the
     directory and file-name start you want to use for the graphics output
     files.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as plt_patches
import numpy as np
import os
import subprocess


# Update these variables to point to your ffmpeg and convert binaries
# If you installed ffmpeg using conda or installed both softwares in
# standard ways on your computer, no changes should be required.
# _FFMPEG_BINARY = '\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\ffmpeg.exe'

_MAGICK_BINARY = '\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe'
_FFMPEG_BINARY = 'ffmpeg'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'   # alternatives: mp4, gif


class Graphics:
    """
    The Graphics class is where we create the setup for our simulations, the methods here
    are the values that are updated via the interactions in between the animals in individuals
    cells and throughout the whole island.
    """

    def __init__(self, hist_specs, pause_time, ymax_animals, cmax_animals, img_dir=None,
                 img_name=None, img_fmt=None):
        """
        Initialize graphics attributes.

        Parameters
        ----------
        hist_specs : dict
            A dictionary for the animal attributes that gives a bins width delta
            and the maximum value
        pause_time : int
            Pause time for drawing graphics. Default 1e-6
        ymax_animals : int
            Number specifying y-axis limit for graph showing animal numbers
        cmax_animals : dict
            Specifying color-code limits for animal densities
        img_dir : str
            String with path to directory for figures
        img_fmt : str
            String with file type for figures, e.g. 'png'
        img_name : str
            String with file name for figures
        """
        # Set default params.
        plt.rcParams['figure.figsize'] = (12, 6)
        self._herbivore_label = plt_patches.Patch(color='b', label='Herbivores')
        self._carnivore_label = plt_patches.Patch(color='r', label='Carnivores')

        # Define a default hist spec if None is given. If not overwrite the given values, keep
        # defaults for the rest.
        if hist_specs is None:
            self._hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                                'age': {'max': 60.0, 'delta': 2.0},
                                'weight': {'max': 60.0, 'delta': 2.0}}
        else:
            self._hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                                'age': {'max': 60.0, 'delta': 2.0},
                                'weight': {'max': 60.0, 'delta': 2.0}}
            for stat_name, value_dict in self._hist_specs.items():
                self._hist_specs[stat_name] = value_dict

        self._bins_fit = self._get_bins('fitness')
        self._bins_age = self._get_bins('age')
        self._bins_weight = self._get_bins('weight')
        self._pause_time = pause_time

        # Related to saving files (images/films)
        if img_name is None:
            img_name = _DEFAULT_GRAPHICS_NAME
        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None
        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT
        self._img_ctr = 0
        self._img_step = 1

        # Initialized by setup. Define axes to plot the different graphics
        self._fig = None
        self._island_map_ax = None
        self._year_count_ax = None
        self._year_text = None
        self._animal_count_ax = None
        self._total_herbivore_line = None
        self._total_carnivore_line = None
        self._herbivore_map_ax = None
        self._herbivore_img_ax = None
        self._carnivore_map_ax = None
        self._carnivore_img_ax = None
        self._fitness_ax = None
        self._age_ax = None
        self._weight_ax = None

        # Also initialized by setup, but not related to axes
        self._island_map_string = None
        self._final_step = None

        self._template = '{:5d}'
        self._ymax_animals = ymax_animals
        self._cmax_animals = cmax_animals

    def _get_bins(self, stat):
        """Calculate bin size of histogram plot."""
        return int(self._hist_specs[stat]['max']/self._hist_specs[stat]['delta'])

    def setup(self, final_step, island_map, img_step):
        """
        The setup for the graphics

        Parameters
        ----------
        final_step : int
            The last step n the graphics
        island_map : str
            String of letters, separated by line split.
        img_step : int
            The year step in the graphics
        """

        self._island_map_string = island_map
        self._final_step = final_step
        self._img_step = img_step

        if self._fig is None:
            self._fig = plt.figure()
            self._fig.legend(handles=[self._herbivore_label, self._carnivore_label],
                             bbox_to_anchor=(0.6, 0.8))
            self._fig.tight_layout()

        if self._island_map_ax is None:
            self._island_map_ax = self._fig.add_axes([0.07, 0.64, 0.3, 0.3])
            self._island_map_ax.set_title('Island')
            self._island_map_ax.axis('off')
            self._plot_island()

        if self._year_count_ax is None:
            self._year_count_ax = self._fig.add_axes([0.45, 0.85, 0.05, 0.05])
            self._year_count_ax.set_title('Year')
            self._year_count_ax.axis('off')
            self._year_text = self._year_count_ax.text(0.5, 0.5,
                                                       self._template.format(0),
                                                       fontsize=15,
                                                       horizontalalignment='center',
                                                       verticalalignment='center',
                                                       transform=self._year_count_ax.transAxes)

        if self._animal_count_ax is None:
            self._animal_count_ax = self._fig.add_axes([0.65, 0.64, 0.3, 0.3])
            self._animal_count_ax.set_title('Total animals')
            self._animal_count_ax.set_ylim(0, self._ymax_animals)
            self._animal_count_ax.set_xlim(0, final_step + 1)

        if self._herbivore_map_ax is None:
            self._herbivore_map_ax = self._fig.add_axes([0.18, 0.24, 0.3, 0.3])
            self._herbivore_map_ax.set_title('Herbivore distribution')
            self._herbivore_img_ax = None

        if self._carnivore_map_ax is None:
            self._carnivore_map_ax = self._fig.add_axes([0.57, 0.24, 0.3, 0.3])
            self._carnivore_map_ax.set_title('Carnivore distribution')
            self._herbivore_img_ax = None

        if self._fitness_ax is None:
            self._fitness_ax = self._fig.add_axes([0.05, 0.04, 0.26, 0.1])
            self._fitness_ax.set_title('Fitness')

        if self._age_ax is None:
            self._age_ax = self._fig.add_axes([0.38, 0.04, 0.26, 0.1])
            self._age_ax.set_title('Age')

        if self._weight_ax is None:
            self._weight_ax = self._fig.add_axes([0.7, 0.04, 0.26, 0.1])
            self._weight_ax.set_title('Weight')

        # Setup for herbivore line
        if self._total_herbivore_line is None:
            herbivore_line_plot = self._animal_count_ax.plot(np.arange(0, final_step + 1),
                                                             np.full(final_step + 1, np.nan), 'b-')
            self._total_herbivore_line = herbivore_line_plot[0]
        else:
            x_data_herb, y_data_herb = self._total_herbivore_line.get_data()
            x_new_herb = np.arange(x_data_herb[-1] + 1, final_step + 1)
            if len(x_new_herb) > 0:
                y_new_herb = np.full(x_new_herb.shape, np.nan)
                self._total_herbivore_line.set_data(np.hstack((x_data_herb, x_new_herb),
                                                              (y_data_herb, y_new_herb)))

        # Setup for carnivore line
        if self._total_carnivore_line is None:
            carnivore_line_plot = self._animal_count_ax.plot(np.arange(0, final_step + 1),
                                                             np.full(final_step + 1, np.nan), 'r-')
            self._total_carnivore_line = carnivore_line_plot[0]
        else:
            x_data_carn, y_data_carn = self._total_carnivore_line.get_data()
            x_new_carn = np.arange(x_data_carn[-1] + 1, final_step + 1)
            if len(x_new_carn) > 0:
                y_new_carn = np.full(x_new_carn.shape, np.nan)
                self._total_carnivore_line.set_data(np.hstack((x_data_carn, x_new_carn),
                                                              (y_data_carn, y_new_carn)))

    def update(self, step, total_herbivores, total_carnivores, herb_in_cell, carn_in_cell, herb_fit,
               carn_fit, herb_age, carn_age, herb_weight, carn_weight):
        """
        Updating the graphs for each year that passes.

        Parameters
        ----------
        step : int
            The year of the graphic
        total_herbivores : int
            The number of herbivores
        total_carnivores : int
            The number of carnivores
        herb_in_cell : int
            The number of herbivores in cell
        carn_in_cell : int
            The number of carnivores in cell
        herb_fit : float
            The fitness value of each herbivore
        carn_fit : float
            The fitness value of each carnivore
        herb_age : int
            The age of the herbivore
        carn_age : int
            The age of the carnivore
        herb_weight : int
            The weight of the herbivore
        carn_weight : int
            The weight of the carnivore
        """

        self._update_year_counter(step)
        self.update_total_animals(step, total_herbivores, total_carnivores)
        self._update_heatmaps(herb_in_cell, carn_in_cell)
        self._update_fitness_ax(herb_fit, carn_fit)
        self._update_age_ax(herb_age, carn_age)
        self._update_weight_ax(herb_weight, carn_weight)
        self._fig.canvas.flush_events()
        plt.pause(self._pause_time)

        self._save_graphics(step)

    def _update_fitness_ax(self, herb_fit, carn_fit):
        """Updating fitness for axes."""
        self._fitness_ax.clear()
        self._fitness_ax.set_title('Fitness')
        self._fitness_ax.hist((herb_fit, carn_fit), bins=self._bins_fit,
                              range=(0, self._hist_specs['fitness']['max']),
                              histtype='step',
                              color=('b', 'r'), lw=2)

    def _update_age_ax(self, herb_age, carn_age):
        """Updating age for axes."""
        self._age_ax.clear()
        self._age_ax.set_title('Age')
        self._age_ax.hist((herb_age, carn_age), bins=self._bins_age,
                          range=(0, self._hist_specs['age']['max']),
                          histtype='step', color=('b', 'r'), lw=2)

    def _update_weight_ax(self, herb_weight, carn_weight):
        """Updating weight for axes."""
        self._weight_ax.clear()
        self._weight_ax.set_title('Weight')
        self._weight_ax.hist((herb_weight, carn_weight), bins=self._bins_weight,
                             range=(0, self._hist_specs['weight']['max']),
                             histtype='step', color=('b', 'r'), lw=2)

    def _update_heatmaps(self, herb_in_cell, carn_in_cell):
        """Update the heatmaps."""
        if self._herbivore_img_ax is not None:
            self._herbivore_img_ax.set_data(herb_in_cell)
        else:
            self._herbivore_img_ax = \
                self._herbivore_map_ax.imshow(herb_in_cell,
                                              interpolation='nearest',
                                              vmin=0,
                                              vmax=self._cmax_animals['Herbivore'])
            plt.colorbar(self._herbivore_img_ax, ax=self._herbivore_map_ax, orientation='vertical')

        if self._carnivore_img_ax is not None:
            self._carnivore_img_ax.set_data(carn_in_cell)
        else:
            self._carnivore_img_ax = \
                self._carnivore_map_ax.imshow(carn_in_cell,
                                              interpolation='nearest',
                                              vmin=0,
                                              vmax=self._cmax_animals['Carnivore'])
            plt.colorbar(self._carnivore_img_ax, ax=self._carnivore_map_ax, orientation='vertical')

    def update_total_animals(self, step, herbivores, carnivores):
        """Updating the total animals."""
        tot_animals = herbivores + carnivores
        if tot_animals > self._ymax_animals:
            self._animal_count_ax.set_ylim(0, tot_animals*1.1)

        # Update Herbivores
        y_data_herb = self._total_herbivore_line.get_ydata()
        y_data_herb[step] = herbivores
        self._total_herbivore_line.set_ydata(y_data_herb)

        # Update Carnivores
        y_data_carn = self._total_carnivore_line.get_ydata()
        y_data_carn[step] = carnivores
        self._total_carnivore_line.set_ydata(y_data_carn)

    def _plot_island(self):
        """Plot the island."""
        #                   R    G    B
        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row] for row in
                   self._island_map_string.splitlines()]
        self._island_map_ax.imshow(map_rgb)

        # Add colormap to island
        island_colormap_ax = self._fig.add_axes([0.3, 0.7, 0.1, 0.3])
        island_colormap_ax.axis('off')

        for ix, name in enumerate(('Water', 'Lowland',
                                   'Highland', 'Desert')):
            island_colormap_ax.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                                       edgecolor='none',
                                                       facecolor=rgb_value[name[0]]))
            island_colormap_ax.text(0.35, ix * 0.2, name,
                                    transform=island_colormap_ax.transAxes)

    def _update_year_counter(self, step):
        """Updating the year counter within the graph."""
        self._year_text.set_text(self._template.format(step))

    def _save_graphics(self, step):
        """Saves graphics to file if file name given."""

        if self._img_base is None or step % self._img_step != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', './{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                print(err)
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)
