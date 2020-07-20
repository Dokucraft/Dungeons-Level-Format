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


### boundaries

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

A list of boundaries in the tile. A boundary is a vertical stack of invisible blocks that players and monsters can't get through. The top and bottom of a boundary are not solid, only the sides are, meaning it's not possible to walk on top of them.

Each boundary is represented by 8 bytes, which are 4 16-bit integers representing a point in space and a height. The point is the position of the bottom of the boundary and the height is how many blocks tall it should be.


### doors

- Type: `array` of `object`

A list of doors in the tile. A door can be a tile connection point or an object players can interact with to teleport somewhere else in the level. Tile connection points does not need to be the same size to be able to connect, however it is recommended that they are, to have full control over exactly how they connect.

For more information about doors, see [the page about them here.]()


### height-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

A heightmap of the tile. This is similar to the block IDs in the `blocks` property, except there is only one layer. The values represent the Y coordinate of the top non-air block.

This property is often a copy of the `region-y-plane` property.

What this property actually affects is currently unknown and requires more testing.

#### See also...
- [blocks](#blocks)
- [region-y-plane](#region-y-plane)


### id

- Type: `string`

A unique identifier/name for the tile. This is used to reference the tile in the level files.


### is-leaky

- Type: `boolean`

This property is currently a mystery. Changing it seems to have no visual effect on the tile.


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
2 | No  | No
3 | Yes | Yes
4 | No  | No

Unwalkable areas stop players from simply walking into them, but does not stop them from rolling or using artifacts that causes the player to move. The `region-plane` is what stops players from just walking off most cliffs.

Note that `0` and `3`, and `2` and `4` have the same properties. This could mean that the `region-plane` controls more than just thse two things, however what that could be is still unknown.

One difference between `0` and `3` is how they are used in the vanilla game. 0 is used for most areas where players can walk, while 3 is used for roofed areas, like tunnels or overhangs.

There are also some differences in how `2` and `4` are used. `2` is mostly used for big falls, while `4` is usually used for high walls.

#### See also...
- [blocks](#blocks)


### region-y-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

A heightmap of the tile. This is similar to the block IDs in the `blocks` property, except there is only one layer. The values represent the Y coordinate of the top non-air block.

This property is often a copy of the `height-plane` property.

What this property actually affects is currently unknown and requires more testing.

#### See also...
- [blocks](#blocks)
- [height-plane](#height-plane)


### regions

- Type: `array` of `object`

A list of regions in the tile. Regions are areas in a tile that can either trigger something, or be used to spawn objects or monsters, or set the spawn point for players.

For more information about regions, see [the page about them here.]()


### size

- Type: `array` of `number`

The size of the tile.


### tags

- Type: `string`

Currently unknown.


### walkable-plane

- Type: `string`
- Encoding/compression: Base64 encoded zlib compressed

Like the other `*-plane` properties, this is similar to the block IDs in the `blocks` property, except there is only one layer. What the values in this property actually represents and what changing them does is currently unknown. One pattern of this property that the vanilla files seems to follow is having the values be the Y coordinate of the top non-*solid* block + 1 in areas where the players can walk, and `0` for out-of-bounds areas.

#### See also...
- [blocks](#blocks)