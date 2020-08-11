# Minecraft Dungeons Level Format

The goal of this repo is to document the Minecraft Dungeons level and tile formats and to give examples of how to manipulate them.

## Overview

To get an idea of how levels and tiles work, here is a brief summary:

*Levels* in Dungeons are stored as [JSON](https://www.json.org/json-en.html) files that tell the game how to put the world together from *tiles*. They also have information about what types of monsters should spawn, what mission objectives and challenges players need to get through, what resource packs should be enabled, and more.

Tiles are stored as JSON objects in *object groups*, and are cuboid shapes made up of blocks. Tiles also store information about things like invisible barriers, the minimap, what areas of the tile players can walk through, how they can be connected to other tiles, and more.

Object groups are simply collections of tiles, stored as JSON files. Levels needs to specify which object groups they need tiles from, so a good way to group your tiles is by putting tiles that are used in the same level in the same group.

These JSON files are *not* Unreal assets, and does not need to be cooked before being packaged.

## Documentation

:warning: This section is still under construction!

Note that this documentation is not official in any way and has been put together by doing a lot of tests, so it can contain errors or be missing some information.

- [Level](/docs/Level.md)
- [List of block IDs](/docs/Block_IDs.md)
- [Tile](/docs/Tile.md)

## Examples

:warning: This section is still under construction!

The examples in this repo are written in Python. Some are not necessarily the most optimized way to do things, they are just examples.

- [Converting a Java world to a Dungeons object group](/examples/docs/Using_ConvsersionTools.md)
- [How to get the ID and data value of a block in a tile](/examples/Get_Block_IDs_and_Data_Values.py)
- [How to set the ID and data value of a block in a tile](/examples/Set_Block_IDs_and_Data_Values.py)
- [Simple Tile Viewer](/examples/SimpleTileViewer.py) using the Tile module, NumPy, Pillow, and PySimpleGUI
- [Tile module](/examples/Tile.py)