"""
This converts the Children's University program to an executable.

Note: need to follow the solution here for this to work:
https://github.com/anthony-tuininga/cx_Freeze/issues/205
(copying _method from numpy/core)
"""


import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = r'C:\Users\djoll\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\djoll\Anaconda3\tcl\tk8.6'

# and another error.
os.environ['QT_PLUGIN_PATH'] = r'C:\Users\djoll\Anaconda3\Library\plugins'

data_file_path = 'data/'
includefiles = [os.path.join(data_file_path, i) for i in os.listdir(data_file_path)]

# Dependencies are automatically detected, but it might need fine tuning.
options = {
    'build_exe': {
        'packages': [
                    'ctypes',
                    'ctypes.util',
                    'fiona',
                    'gdal',
                    'geos',
                    'shapely',
                    'shapely.geometry',
                    'pyproj',
                    'rtree',
                    'geopandas.datasets',
                    'pytest',
                    'pandas._libs.tslibs.timedeltas',
                     "os",
                     "tkinter",
                     "matplotlib",
                     'scipy.sparse.csgraph._validation',
                     'pysal'
                     ],
        'include_files': includefiles,
        'excludes': 'scipy.spatial.cKDTree' # caused errors
    }
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(
    name = "CU GUI",
    version = "1.0",
    description = "GUI for Children's University",
    options = options,
    executables = [Executable("launch.py", base=base)])