# Using the [ConversionTools module](/examples/ConversionTools.py)

:warning: The ConversionTools module and this guide are still under construction! More tools and information will be added over time.

This module requires [anvil-parser](https://github.com/matcool/anvil-parser):

```pip install anvil-parser```

## JavaWorldToObjectGroup

This converter turns Minecraft Java Edition worlds into Minecraft Dungeons object groups.

To use it, you will first need a Java world with the tiles you want to convert. Since Java Edition has a lot of blocks that Dungeons doesn't have and vice versa, we need to pick some blocks to map the ones that are missing to. This repo already has [a pretty good block map](/examples/BlockMap.py), but you can edit it if you want to change things around or add to it. There are also some blocks that are treated differently by the converter. By default, these are `minecraft:air`, `minecraft:barrier`, and `minecraft:dead_tube_coral_block`, but they can be changed to other blocks after you have created a converter instance, which we will go over a bit later.

- Air blocks will simply not be processed, to speed up the conversion.
- Barrier blocks will be converted to tile [boundaries](/docs/Tile.md#boundaries).
- Dead Tube Coral blocks will be converted to [doors](/docs/Tile.md#doors).

Once you have a world that you want to convert, you need to create a file called `objectgroup.json` in the world directory. This file should be set up just like a real object group file from Dungeons, except the only properties you need to add to each tile are `id`, `pos`, `size`, and any other properties that won't be handled by the converter, i.e. `regions`, `region-plane`, `y`, and so on. The properties the converter does handle are: `blocks`, `height-plane`, `doors`, `boundaries` (You can still add extra doors or boundaries to the JSON file, if you want to)

The `pos` property tells the converter where the tile starts, and the `size` property tells it how many blocks it needs to go in each direction.

Here is an example for the `objectgroup.json` file in the world directory:

```json
{ "objects": [

    { "id": "example_tile_with_spawn_and_zombie",
      "pos": [ -58, 0, -8 ],
      "size": [ 83, 5, 33 ],
      "regions": [
        { "name": "playerstart",
          "pos": [66, 5, 16],
          "size": [1, 1, 1],
          "tags": "playerstart",
          "type": "trigger"
        },
        { "name": "kg_zombie",
          "pos": [11, 5, 16],
          "size": [1, 1, 1],
          "tags": "",
          "type": "spawn"
        }
      ]
    },

    { "id": "example_tile_with_player_spawn",
      "pos": [ 35, 12, 34 ],
      "size": [ 9, 3, 9 ],
      "regions": [
        { "name": "playerstart",
          "pos": [4, 1, 4],
          "size": [1, 1, 1],
          "tags": "playerstart",
          "type": "trigger"
        }
      ]
    },

    { "id": "small_example_tile01",
      "pos": [ 36, 12, 46 ],
      "size": [ 7, 3, 7 ]
    },

    { "id": "small_example_tile02",
      "pos": [ 36, 12, 56 ],
      "size": [ 7, 3, 7 ]
    },

    { "id": "small_example_tile03",
      "pos": [ 36, 12, 66 ],
      "size": [ 7, 3, 7 ]
    }

  ]
}
```

Once that is set up, the world is ready for the converter. To convert the world, first create an instance of the converter with the world directory path, like this:

```py
from ConversionTools import JavaWorldToObjectGroup
converter = JavaWorldToObjectGroup(r'C:\my\java\saves\ExampleWorld')
```

You can then change the settings for it if you want something other than the default:

```py
converter.door_block = 'minecraft:stone'
converter.boundary_block = 'minecraft:grass_block'
```

Once your converter instance is configured, you can use it to turn the world into an object group:

```py
objectgroup = converter.convert()
```

To save the object group to a file, I recommend using the [pretty_compact_json module](/examples/pretty_compact_json.py).

```py
from pretty_compact_json import stringify

with open('objectgroup.json', 'w') as out_file:
  out_file.write(stringify(objectgroup))
```

Of course, you can also just use the Python json module, but the output file will not be nearly as pretty.

```py
import json

with open('objectgroup.json', 'w') as out_file:
  json.dump(objectgroup, out_file, indent=2)
```

Here is a full code example:

```py
from ConversionTools import JavaWorldToObjectGroup
from pretty_compact_json import stringify

world_dir = r'C:\MC Java\saves\ExampleWorld'
output_path = r'C:\MCD Mod\Dungeons\Content\data\lovika\objectgroups\my_example\objectgroup.json'

# Just using the default settings this time
objectgroup = JavaWorldToObjectGroup(world_dir).convert()

with open(output_path, 'w') as out_file:
  out_file.write(stringify(objectgroup))
```