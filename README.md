[![Build Status](https://travis-ci.org/ladybug-tools/dragonfly-grasshopper.svg?branch=master)](https://travis-ci.org/ladybug-tools/dragonfly-grasshopper)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# dragonfly-grasshopper

:dragon: :green_book: Dragonfly plugin for Grasshopper (aka. dragonfly[+]).

This repository contains all Grasshopper components for the dragonfly plugin.
The package includes both the userobjects (`.ghuser`) and the Python source (`.py`).
Note that this library only possesses the Grasshopper components and, in order to
run the plugin, the core libraries must be installed to the Rhino `scripts` folder
(see dependencies).

## Dependencies

The dragonfly-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-dotnet](https://github.com/ladybug-tools/ladybug-dotnet)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-energy](https://github.com/ladybug-tools/honeybee-energy)
* [honeybee-energy-standards](https://github.com/ladybug-tools/honeybee-energy-standards)
* [dragonfly-core](https://github.com/ladybug-tools/dragonfly-core)
* [dragonfly-energy](https://github.com/ladybug-tools/dragonfly-energy)

# Oher Required Components
The dragonfly-grasshopper plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)
* [honeybee-grasshopper-energy](https://github.com/ladybug-tools/honeybee-grasshopper-energy)

## Installation

To install the most recent version of the Grasshopper plugin, follow these steps:

1. Clone this repository to your machine.
2. Make sure you are connected to the internet and open the installer.gh file in Grasshopper.
3. Set the toggle inside the file to `True`.
4. Restart Rhino + Grasshopper.

Note that following these steps will install the absolute most recent version of
the plugin. To install the last stable release, download the components and Grasshopper
file installer from [food4rhino](https://www.food4rhino.com/app/ladybug-tools).
