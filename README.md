[![Build Status](https://github.com/ladybug-tools/dragonfly-grasshopper/workflows/CI/badge.svg)](https://github.com/ladybug-tools/dragonfly-grasshopper/actions)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# dragonfly-grasshopper

:dragon: :green_book: Dragonfly plugin for Grasshopper (aka. dragonfly[+]).

This repository contains all Grasshopper components for the dragonfly plugin.
The package includes both the userobjects (`.ghuser`) and the Python source (`.py`).
Note that this library only possesses the Grasshopper components and, in order to
run the plugin, the core libraries must be installed in a way that they can be
discovered by Rhino (see dependencies).

## Dependencies

The dragonfly-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-energy](https://github.com/ladybug-tools/honeybee-energy)
* [honeybee-energy-standards](https://github.com/ladybug-tools/honeybee-energy-standards)
* [dragonfly-core](https://github.com/ladybug-tools/dragonfly-core)
* [dragonfly-energy](https://github.com/ladybug-tools/dragonfly-energy)

## Other Required Components

The dragonfly-grasshopper plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)
* [honeybee-grasshopper-energy](https://github.com/ladybug-tools/honeybee-grasshopper-energy)
* [honeybee-grasshopper-radiance](https://github.com/ladybug-tools/honeybee-grasshopper-radiance)

## Installation

See the [Wiki of the lbt-grasshopper repository](https://github.com/ladybug-tools/lbt-grasshopper/wiki)
for the installation instructions for the entire Ladybug Tools Grasshopper plugin
(including this repository).
