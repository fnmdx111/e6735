from distutils.core import setup

import numpy
from Cython.Build import cythonize
from Cython.Distutils import Extension

# setup(ext_modules=[Extension('video_feat', ['video_feat.c'],
#                              include_dirs=[numpy.get_include()],
#                              )])
