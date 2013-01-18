# Copyright 2011-2013, Vinothan N. Manoharan, Thomas G. Dimiduk,
# Rebecca W. Perry, Jerome Fung, and Ryan McGorty, Anna Wang
#
# This file is part of HoloPy.
#
# HoloPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HoloPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HoloPy.  If not, see <http://www.gnu.org/licenses/>.
"""
Routine for fitting a time series of holograms to an exact solution

.. moduleauthor:: Thomas G. Dimiduk <tdimiduk@physics.harvard.edu>
.. moduleauthor:: Rebecca W. Perry <rperry@seas.harvard.edu>

"""
from __future__ import division

import warnings

from ..core.process import normalize
from ..core import Image
from ..core.io import load, save
from . import fit

#default preprocessing function
def div_normalize(holo, bg):
    if bg is not None:
        imagetofit = normalize(holo/bg)
    else:
        imagetofit = normalize(holo)
    return imagetofit

#default updating function
def update_all(model, fitted_result):
    for p in model.parameters:
        name = p.name
        p.guess = fitted_result.parameters[name]
    return model

def fit_series(model, data, data_optics=None, data_spacing=None, bg=None,
    outfilenames=None, preprocess_func=div_normalize,
    update_func=update_all):
    """
    fit a model to each frame of data in a time series

    Parameters
    ----------
    model : :class:`.Model` object
        A model describing the scattering system which leads
        to your data and the parameters to vary to fit it
        to the data
    data : list(filenames) or list(:class:`.Image`)
        List of Image objects to fit, or full paths of images to load
    data_optics : :class:`.Optics` (optional)
        Optics information (only required if loading image files without
        optical information)
    data_spacing : float or np.array
        Pixel spacing for data. (Only required if loading image files without
        spacing information)
    bg : :class:`.Image` object or path
        Optional background image to be used for cleaning up
        the raw data images
    outfilenames : list
        Full paths to save output for each image, if not
        included, nothing saved
    preprocess_func : function
        Handles pre-processing images before fitting the model
        to them
    update_func : function
        Updates the model (typically just the paramter guess)
        for the next frame

    Returns
    -------
    allresults : :list:`
        List of all the result objects (one per frame)
    """

    allresults = []

    if isinstance(bg, basestring):
        bg = load(bg, spacing=data_spacing, optics=data_optics)

    #to allow running without saving output
    if outfilenames is None:
        outfilenames = ['']*len(data)

    for frame, outpath in zip(data, outfilenames):
        if not isinstance(frame, Image):
            frame = load(frame, spacing = data_spacing, optics = data_optics)
        imagetofit = preprocess_func(frame, bg)

        result = fit(model, imagetofit)
        allresults.append(result)
        if outpath!='':
            save(outpath, result)

        model = update_all(model, result)

    return allresults
