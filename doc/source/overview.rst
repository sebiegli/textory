=========================
Overview
=========================

Textory can be used to calculate correlation statistics like variogram as an image texture.
Basically the statistic is calculated for a moving window over the whole array. Each pixel in
the resulting array is the statistical measure of the small window around the pixel.

These type of image textures are especially interessting for machine learning approaches on
spatial datasets like satellite data, since they are able to include spatial information of single
or between two datasets in the machine learning algorithm.

Features
========

Textory is able to calculate:

- Variogram: :math:`\gamma(h) = \frac{1}{2n(h)} \sum_{i=1}^{n(h)} (v(x_{i}) - v(x_{i}+h))^{2}`
- Madogram: :math:`\gamma(h) = \frac{1}{2n(h)} \sum_{i=1}^{n(h)} |v(x_{i}) - v(x_{i}+h)|`
- Rodogram: :math:`\gamma(h) = \frac{1}{2n(h)} \sum_{i=1}^{n(h)} \sqrt{|v(x_{i}) - v(x_{i}+h)|}`
- Cross Variogram: :math:`\gamma(h) = \frac{1}{2n(h)} \sum_{i=1}^{n(h)} (v(x_{i}) - v(x_{i}+h))*(w(x_{i}) - w(x_{i}+h))`
- Pseudo Cross Variogram: :math:`\gamma(h) = \frac{1}{2n(h)} \sum_{i=1}^{n(h)} (v(x_{i}) - w(x_{i}+h))^{2}`
- basic statistics (e.g. min, max, median, etc. (only for square windows))

for different lag distances and window sizes (round and square windows) for numpy and :class:`dask.array.Array` as
well as :class:`xarray.DataArray`. Furthermore conveniant functions to easily caluculate these statistics
for :class:`xarray.Dataset` and :class:`satpy.scene.Scene` are available.
