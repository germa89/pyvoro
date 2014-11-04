# 
# setup.py : pyvoro python interface to voro++
# 
# this extension to voro++ is released under the original modified BSD license
# and constitutes an Extension to the original project.
#
# Copyright (c) Joe Jordan 2012
# contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
#

from distutils.core import setup, Extension
from Cython.Build import cythonize
import os.path

source_files = ['cell.cc', 'common.cc', 'container.cc', 'unitcell.cc', 
                'v_compute.cc', 'c_loops.cc', 'v_base.cc', 'wall.cc',
                'pre_container.cc', 'container_prd.cc']
source_files = [os.path.join('src', fname) for fname in source_files]

extensions = [
    Extension("pyvoro.voroplusplus", ["pyvoro/voroplusplus.pyx", "pyvoro/vpp.cpp"] + source_files,
        include_dirs = ["pyvoro", "src"])
]

setup(
    name="pyvoro",
    version="1.3.2",
    description="2D and 3D Voronoi tessellations: a python entry point for the voro++ library.",
    author="Joe Jordan",
    author_email="joe.jordan@imperial.ac.uk",
    url="https://github.com/joe-jordan/pyvoro",
    download_url="https://github.com/joe-jordan/pyvoro/tarball/v1.3.2",
    packages=["pyvoro",],
    package_dir={"pyvoro": "pyvoro"},
    ext_modules=cythonize(extensions),
    keywords=["geometry", "mathematics", "Voronoi"],
    classifiers=[],
)
