# Level

Level files use [tiles](/docs/Tile.md) from object groups to create the worlds you can play in. They also store information about the mission objectives, what types of mobs can spawn, what props are used, and more.

Levels are stored as JSON files in the `Dungeons/Content/data/lovika/levels` directory.

## Table of contents

- [death-outside](#death-outside)
- [fill](#fill)
- [id](#id)
- [play-intro](#play-intro)

## Properties

:warning: This section is still under construction! More properties and information will be added over time.


### death-outside

- Type: `boolean`

By default, if the player walks off the edge of the level, they will respawn at their last checkpoint. Setting this property to `false` will create a "soft" barrier around the level that players can't walk through. It is still possible to roll through this barrier, however. It works just like the `2` and `4` values of the `region-plane` in tiles.

If this property is set to `false` and the level has "fill", rolling through the barrier will allow you to walk around on the fill freely.

#### See also...
- [Tile "region-plane" property](/docs/Tile.md#region-plane)
- [fill](#fill)


### fill

- Type: `object`

This property controls the level "fill", which is a layer of blocks automatically placed by the game around the outside of tiles. The fill is made up of up to 17 bands of "gradient" blocks.

It can have a `world` property, which can have a `gradient` property, which is an array numbers. The first number controls the average width of the first band of blocks. The second number controls the width of the second band, and so on. Because there are only 16 different gradient blocks in the game, all bands beyond 16 will use the first gradient block, creating a 17th band with an average width equal to the sum of all numbers in the array after the 16th.

The `y` tile property has some sort of effect on the level fill, but it is not fully understood yet.

#### See also...
- [Tile "y" property](/docs/Tile.md#y)


### id

- Type: `string`

The ID of the level. This is used to set the environment of the level. For example, setting it to `creeperwoods` will make it night-time.

It also controls what into sequence is played at the start of the level.

It might control more than just these two things, more testing is required.


### play-intro

- Type: `boolean`

By default, levels that have an intro sequence will play it after loading into the level. This property can be set to `false` to disable the intro.