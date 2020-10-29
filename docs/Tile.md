# Tile

A tile is essentially a chunk of Minecraft blocks. They can be pretty much any size, but they are always shaped like a cuboid. They are stored as JSON objects in object groups.

## Table of contents

- [blocks](#blocks)
- [boundaries](#boundaries)
- [doors](#doors)
- [height-plane](#height-plane)
- [id](#id)
- [is-leaky](#is-leaky)
- [locked](#locked)
- [pos](#pos)
- [region-plane](#region-plane)
- [region-y-plane](#region-y-plane)
- [regions](#regions)
- [size](#size)
- [tags](#tags)
- [walkable-plane](#walkable-plane)
- [y](#y)

## Properties

:warning: This section is still under construction!


### blocks

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

The blocks in the tile, stored as block IDs and data values. This is split into two parts:

#### Block IDs

The first part is the same size as the volume of the tile in bytes. Each byte in this section is a block ID. The order is YZX, meaning if you have a point `(x, y, z)` in a tile with a size `(w, h, d)`, the index of the block at that point is `(y * d + z) * w + x`.

#### Block data values

The second part is similar to the first one, but each data value is only 4 bits instead of a byte, meaning this part is half the size of the first.

The total size of the `blocks` property of a tile with a size `(w, h, d)` is `ceil(w * h * d * 1.5)` bytes.

#### See also...
- [List of block IDs](/docs/Block_IDs.md)
- [Example: How to get the ID and data value of a block in a tile](/examples/Get_Block_IDs_and_Data_Values.py)
- [Example: How to set the ID and data value of a block in a tile](/examples/Set_Block_IDs_and_Data_Values.py)


### boundaries

- Type: `string` **or** `array` of `array` of `number`
- Encoding/compression: If it is a `string`, base64 encoded zlib compressed

A list of boundaries in the tile. A boundary is a vertical stack of invisible blocks that players and monsters can't get through. The top and bottom of a boundary are not solid, only the sides are, meaning it's not possible to walk on top of them.

Each boundary is defined by 4 16-bit integers that represent a point in space and a height. The point is the position of the bottom of the boundary and the height is how many blocks tall it should be.

The order of the 4 integers is: x, y, z, height.

Most tiles in the game uses the more compact encoded string format for this property. In this format, each boundary is simply the 4 16-bit integers packed together into 8 bytes. The boundaries are then packed together without anything separating them to form the list, so that every 8 bytes is a boundary.

The array format is, as of version 1.3.2.0, only found in the `GenericCaves/objectgroup.json.oldold` file. In this format, each boundary is an array containing the 4 integers, and the list is simply an array of these boundary arrays. This format is much easier to understand for most people, but it is far less compact.


### doors

- Type: `array` of `object`

A list of doors in the tile. A door can be a tile connection point or an object players can interact with to teleport somewhere else in the level. Tile connection points does not need to be the same size to be able to connect, however it is recommended that they are, to have full control over exactly how they connect.

~~For more information about doors, see [the page about them here.]()~~


### height-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

A heightmap of the tile. This is similar to the block IDs in the `blocks` property, except there is only one layer. The values represent the Y coordinate of the top non-air block.

This property is often a copy of the `region-y-plane` property, but not always, and they function differently.

What this property actually affects is currently unknown and requires more testing.

#### See also...
- [blocks](#blocks)
- [region-y-plane](#region-y-plane)


### id

- Type: `string`

A unique identifier/name for the tile. This is used to reference the tile in the level files.


### is-leaky

- Type: `boolean`

["It's an internal thing to determine if you can escape tiles."](/docs/is-leaky.png)

Possibly just something Mojang's editor uses to show if a tile needs more boundaries. After a lot of testing, it doesn't seem to affect anything in-game.


### locked

- Type: `boolean`

What this does is currently unknown. The property first appreared in version 1.2.1.0, and as of 1.3.2.0, no tiles have it set to `true`.


### pos

- Type: `array` of `number`

This is not actually the position of the tile in the level and changing it has seemingly no effect. It is most likely the position of the tile in the world where it was built in Minecraft, before importing the tile to Dungeons.


### region-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

Information about how the tile should be displayed on the minimap and what areas of the tile players can walk through. It is very similar to the block IDs in the `blocks` property, except there is only one layer and the values range from 0 to 4, each with a different meaning:

Value | Walkable | Minimap
----- | -------- | -------
0 | Yes | Yes
1 | Yes | No
2 | Only if below `region-y-plane` | No
3 | Yes | Yes
4 | Only if below `region-y-plane` | No

Unwalkable areas stop players from simply walking into them, but does not stop them from rolling or using artifacts that causes the player to move. The `region-plane` is what stops players from just walking off most cliffs.

Note that `0` and `3`, and `2` and `4` have the same properties. This could mean that the `region-plane` controls more than just thse two things, however what that could be is still unknown.

One difference between `0` and `3` is how they are used in the vanilla game. `0` is used for most areas where players can walk, while `3` is used for roofed areas, like tunnels or overhangs.

There are also some differences in how `2` and `4` are used. `2` is mostly used for big falls, while `4` is usually used for high walls.

Values greater than 4 work just like `0`.

#### See also...
- [blocks](#blocks)
- [region-y-plane](#region-y-plane)


### region-y-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

This is similar to the `height-plane` property and, for a lot of the tiles in the game, these two properties are identical. However, they don't function the same way. The values here represent the Y coordinate of where some `region-plane` values change properties:

`region-plane` Value | Effect
-------------------- | ------
0 | None?
1 | None?
2 | If the player is below the `region-y-plane`, they can move through the area freely. If they are above, they can not walk into the area, but can still roll/jump into it.
3 | None?
4 | If the player is below the `region-y-plane`, they can move through the area freely. If they are above, they can not walk into the area, but can still roll/jump into it.

More testing is required to find out more about this property. It might be related to what separates the `0` and `3`, and/or the `2` and `4` values of the `region-plane`, but that is just speculation for now.

#### See also...
- [height-plane](#height-plane)
- [region-plane](#region-plane)


### regions

- Type: `array` of `object`

A list of regions in the tile. Regions are areas in a tile that can either trigger something, or be used to spawn objects or monsters, or set the spawn point for players.

~~For more information about regions, see [the page about them here.]()~~


### size

- Type: `array` of `number`

The size of the tile.


### tags

- Type: `string`

Currently unknown.

Possibly used by level files to reference multiple tiles at once, for example `"*.*.tile_tag_goes_here"`, but this hasn't been tested yet.


### walkable-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

Like the other `*-plane` properties, this is similar to the block IDs in the `blocks` property, except there is only one layer. What the values in this property actually represents and what changing them does is currently unknown. One pattern of this property that the vanilla files seems to follow is having the values be the Y coordinate of the top *solid* block + 1 in areas where the players can walk, and `0` for out-of-bounds areas.

#### See also...
- [blocks](#blocks)


### y

- Type: `number`

This seems to have something to do with height and the level "fill", but it is not fully understood yet.

![y property affecting the level fill](/docs/y.gif)

#### See also...
- [Level "fill" property](/docs/Level.md#fill)