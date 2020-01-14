from setuptools import setup

from pyfiledir import py_cli
from pyfiledir.__version__ import __version__

setup(
    name='pyfiledir',
    version=__version__,
    packages=['pyfiledir'],
    entry_points={
        'console_scripts': [
            'pyfiledir = pyfiledir.__main__:main',
        ],
    },
    # metadata to display on PyPI
    author="SuJiKiNen",
    author_email="sujikinen@gmail.com",
    description=py_cli.__doc__,
    license="GPLv3+",
    keywords="bash completion directory pinyin",
    url="https://github.com/SuJiKiNen/pyfiledir",
    project_urls={
        "Bug Tracker": "https://github.com/SuJiKiNen/pyfiledir/issues",
        "Source Code": "https://github.com/SuJiKiNen/pyfiledir",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    python_requires='>=3.5',
)
