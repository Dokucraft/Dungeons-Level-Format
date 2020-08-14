# Using the [ConversionTools module](/examples/ConversionTools.py)

:warning: The ConversionTools module and this guide are still under construction! More tools and information will be added over time.

This module requires [anvil-parser](https://github.com/matcool/anvil-parser):

```pip install anvil-parser```

## JavaWorldToObjectGroup

This converter turns Minecraft Java Edition worlds into Minecraft Dungeons object groups.

To use it, you will first need a Java world with the tiles you want to convert. Since Java Edition has a lot of blocks that Dungeons doesn't have and vice versa, we need to pick some blocks to map the ones that are missing to. This repo already has [a pretty good block map](/examples/BlockMap.py), but you can edit it if you want to change things around or add to it. There are also some blocks that are treated differently by the converter. By default, these are `minecraft:air`, `minecraft:barrier`, and `minecraft:creeper_head`, but they can be changed to other blocks after you have created a converter instance, which we will go over a bit later.

- Air blocks will simply not be processed, to speed up the conversion.
- Barrier blocks will be converted to tile [boundaries](/docs/Tile.md#boundaries).
- Creeper heads will be converted to [doors](/docs/Tile.md#doors).

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
converter.door_block = 'minecraft:stone' # Default is 'minecraft:creeper_head'
converter.boundary_block = 'minecraft:grass_block' # Default is 'minecraft:barrier'
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


## ObjectGroupToJavaWorld

This converter turns Minecraft Dungeons object groups into Minecraft Java Edition worlds.

:warning: Some blocks will not appear correctly in Java Edition due to not having their block states set up properly. I have plans for fixing this issue, but that will come later.

It is similar to JavaWorldToObjectGroup, but doesn't require any setup other than having an object group to convert and a folder to put the world files into:

```py
from ConversionTools import ObjectGroupToJavaWorld

objectgroup_path = r'C:\my\dungeons\objectgroups\example\objectgroup.json'
output_world_path = r'C:\my\java\saves\ExampleWorld'

converter = ObjectGroupToJavaWorld(objectgroup_path, output_world_path)
```

After you have created the converter, you can edit the settings for it if you want to before starting the conversion process:

```py
# The blocks need to be anvil-parser blocks, so we need to import that
import anvil

converter.level_name = 'My Example World' # Default is 'Converted Object Group'
converter.boundary_block = anvil.Block('minecraft', 'glass') # Default is anvil.Block('minecraft', 'barrier')
converter.door_block = anvil.Block('minecraft', 'end_stone') # Default is anvil.Block('minecraft', 'creeper_head')
```

Once your converter instance is configured, you can use it to turn the object group into a Java world:

```py
converter.convert()
```

And that's it! The world should be in the folder you set at the start, ready to be explored in Java Edition 1.16.2.

Here's a full code example:

```py
from ConversionTools import ObjectGroupToJavaWorld

objectgroup_path = r'C:\my\dungeons\objectgroups\example\objectgroup.json'
output_world_path = r'C:\MC Java\saves\ExampleWorld'

# Just using the default settings this time
ObjectGroupToJavaWorld(objectgroup_path, output_world_path).convert()
```