import math
import json
from JavaWorldReader import JavaWorldReader
from Tile import Tile, Boundary, Door
from BlockMap import find_java_block

"""A collection of tools that convert Dungeons tiles to other formats and vice versa."""

class JavaWorldToObjectGroup:
  """Converter that takes a Java Edition world and creates a Dungeons object group."""
  def __init__(self, world_dir):
    self.world_dir = world_dir
    self.air_block = 'minecraft:air'
    self.boundary_block = 'minecraft:barrier'

    # This one is pretty random. I just picked a block that definitely isn't used in Dungeons.
    self.door_block = 'minecraft:dead_tube_coral_block'

  def convert(self, dict_format=True):
    """Returns a Dungeons object group, or a list of tiles, based on the Java Edition world."""
    with open(self.world_dir + '/objectgroup.json') as json_file:
      tiles = [Tile.from_dict(t) for t in json.load(json_file)['objects']]

    world = JavaWorldReader(self.world_dir)

    # Apologies for the confusing variable names below. Let me explain what they mean:
    #   ax, ay, az are absolute coordinates. These are the world coordinates of the block in Java edition.
    #   tx, ty, tz are tile coordinates. These are relative to the tile's position.
    #   cx and cz are chunk coordinates. Chunks hold 16x256x16 blocks.
    #   yi and zi are iterable ranges for the Y and Z axes.

    for tile in tiles:
      # Creating these ranges here is faster than doing it for each slice/column of the tile
      zi = range(tile.size[2])
      yi = range(tile.size[1])

      doors = []

      # For each slice of the tile along the X axis...
      for tx in range(tile.size[0]):
        ax = tx + tile.pos[0]
        cx = math.floor(ax / 16)

        # For each column of the slice along the Z axis...
        for tz in zi:
          az = tz + tile.pos[2]
          cz = math.floor(az / 16)
          chunk = world.chunk(cx, cz)
          current_boundary = None

          # For each block in the column along the Y axis...
          for ty in yi:
            ay = ty + tile.pos[1]

            # Get the block from the Java world chunk
            java_block = chunk.get_block(ax % 16, ay, az % 16)
            namespaced_id = java_block.namespace + ':' + java_block.id

            # There's no reason to keep going if the block is just air
            if namespaced_id == self.air_block:
              continue

            # Handle blocks that are used for special things in this converter, like tile doors and boundaries
            if namespaced_id == self.boundary_block:
              # Check if this block is connected to the last boundary found in this column
              if current_boundary is None or current_boundary.y + current_boundary.h != ty:
                current_boundary = Boundary(tx, ty, tz, 1)
                tile.boundaries.append(current_boundary)
              else:
                current_boundary.h += 1
              continue

            if namespaced_id == self.door_block:
              # Check if this block has already been detected as part of a door
              is_already_part_of_door = False
              for door in doors:
                if (door['y1'] <= ay and door['y2'] >= ay
                    and door['z1'] <= az and door['z2'] >= az
                    and door['x1'] <= ax and door['x2'] >= ax):
                  is_already_part_of_door = True
                  break

              # Detect the size of the door and add it to the list
              # I think this could probably be done in a better way, but it will do for now.
              if not is_already_part_of_door:
                x2, y2, z2 = ax, ay, az
                for dx in range(ax + 1, tile.pos[0] + tile.size[0]):
                  b = world.chunk(math.floor(dx / 16), cz).get_block(dx % 16, ay, az % 16)
                  if f'{b.namespace}:{b.id}' != self.door_block:
                    x2 = dx - 1
                    break
                for dy in range(ay + 1, tile.pos[1] + tile.size[1]):
                  b = chunk.get_block(ax % 16, dy, az % 16)
                  if f'{b.namespace}:{b.id}' != self.door_block:
                    y2 = dy - 1
                    break
                for dz in range(az + 1, tile.pos[2] + tile.size[2]):
                  b = world.chunk(cx, math.floor(dz / 16)).get_block(ax % 16, ay, dz % 16)
                  if f'{b.namespace}:{b.id}' != self.door_block:
                    z2 = dz - 1
                    break
                doors.append({'x1':ax, 'x2':x2, 'y1':ay, 'y2':y2, 'z1':az, 'z2':z2})
              continue

            # Mapped blocks have both a Java namespaced ID + state and a Dungeons ID + data value
            mapped_block = find_java_block(java_block)

            if mapped_block is None:
              print(f'Warning: {java_block} is not mapped to anything. It will be replaced by air.')
              continue

            # Check if the block has a data value
            if len(mapped_block['dungeons']) > 1:
              tile.set_block(tx, ty, tz, block_id = mapped_block['dungeons'][0], block_data = mapped_block['dungeons'][1])
            else:
              tile.set_block(tx, ty, tz, block_id = mapped_block['dungeons'][0])

      # Add all of the detected doors to the tile, if any
      if len(doors) > 0:
        tile.doors += [
          Door(
            pos=[d['x1'] - tile.pos[0], d['y1'] - tile.pos[1], d['z1'] - tile.pos[2]],
            size=[d['x2'] - d['x1'] + 1, d['y2'] - d['y1'] + 1, d['z2'] - d['z1'] + 1])
          for d in doors]

    if dict_format:
      return {'objects':[t.dict() for t in tiles]}
    else:
      return {'objects':tiles}