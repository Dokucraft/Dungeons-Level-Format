import os
import math
import time
import json
import anvil
from nbt.nbt import *
from pretty_compact_json import stringify
from JavaWorldReader import JavaWorldReader
from Tile import Tile, Boundary, Door, Region
from BlockMap import find_java_block, find_dungeons_block

"""A collection of tools that convert Dungeons tiles to other formats and vice versa."""

class JavaWorldToObjectGroup:
  """Converter that takes a Java Edition world and creates a Dungeons object group."""
  def __init__(self, world_dir):
    self.world_dir = world_dir
    self.air_block = 'minecraft:air'
    self.cave_air_block = 'minecraft:cave_air'
    self.boundary_block = 'minecraft:barrier'
    self.player_start_block = 'minecraft:player_head'

    # Creeper head, because it can float and it doesn't destroy path blocks or farmland
    self.door_block = 'minecraft:creeper_head'

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
      yi = range(min(256, tile.size[1]))

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
            if namespaced_id == self.air_block or namespaced_id == self.cave_air_block:
              continue

            # Handle blocks that are used for special things in this converter, like tile doors and boundaries
            if namespaced_id == self.player_start_block:
              tile_region = Region([tx, ty, tz]) # Note: This is a Tile.Region, not an anvil.Region
              tile_region.name = 'playerstart'
              tile_region.tags = 'playerstart'
              tile_region.type = 'trigger'
              tile.regions.append(tile_region)
              continue

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
              props = {}
              for prop in java_block.properties:
                props[prop] = java_block.properties[prop].value
              print(f'Warning: {java_block}{json.dumps(props)} is not mapped to anything. It will be replaced by air.')
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


class ObjectGroupToJavaWorld:
  """Converter that takes a Dungeons object group and creates a Java Edition world."""
  def __init__(self, objectgroup, world_dir):
    self.objectgroup = objectgroup
    self.world_dir = world_dir
    self.level_name = 'Converted Object Group'
    self.boundary_block = anvil.Block('minecraft', 'barrier')
    self.door_block = anvil.Block('minecraft', 'creeper_head')
    self.player_start_block = anvil.Block('minecraft', 'player_head')

  def convert(self):
    # TODO: Converting to a Java world should be done one region or maybe even
    # one sub-region at a time. Right now, all regions are kept
    # in memory until the conversion process is done, which means the memory
    # usage can be massive for bigger object groups.

    # anvil-parser doesn't actually support loading a region from a file and
    # then editing it and writing it to a file again. Regions loaded from a
    # file are read-only, and the regions that can be edited start out empty.

    region_cache = {}
    block_cache = {}

    if isinstance(self.objectgroup, dict):
      og = self.objectgroup

    else: # If objectgroup is a file path, parse the json file
      with open(self.objectgroup) as json_file:
        og = json.load(json_file)

    for tile_dict in og['objects']:
      if isinstance(tile_dict, Tile):
        tile = tile_dict
      else:
        tile = Tile.from_dict(tile_dict)

      zi = range(tile.size[2])
      yi = range(min(256, tile.size[1]))

      # For each slice of the tile along the X axis...
      for tx in range(tile.size[0]):
        ax = tx + tile.pos[0]
        rx = math.floor(ax / 512)

        # For each column of the slice along the Z axis...
        for tz in zi:
          az = tz + tile.pos[2]
          rz = math.floor(az / 512)

          # Make sure the region is available
          if f'{rx}x{rz}' in region_cache:
            region = region_cache[f'{rx}x{rz}']
          else:
            region = anvil.EmptyRegion(rx, rz)
            region_cache[f'{rx}x{rz}'] = region

          # For each block in the column along the Y axis...
          for ty in yi:
            ay = ty + tile.pos[1]

            # Skip this block if it's outside of the world bounds
            if ay < 0 or ay >= 256:
              continue

            bidx = tile.get_block_index(tx, ty, tz)

            # If the block is just air, we don't need to do anything
            if tile.blocks[bidx] == 0:
              continue

            # Get the Java block from the cache if it's there
            bcid = tile.blocks[bidx] << 4 | tile.block_data[bidx]
            if bcid in block_cache:
              java_block = block_cache[bcid]

            else: # If not, find it and add it to the cache to speed things up later
              mapped_block = find_dungeons_block(tile.blocks[bidx], tile.block_data[bidx])

              if mapped_block is None:
                print(f'Warning: {tile.blocks[bidx]}:{tile.block_data[bidx]} is not mapped to anything. It will be replaced by air.')
                continue

              if len(mapped_block['java']) > 1:
                java_block = anvil.Block(*mapped_block['java'][0].split(':', 1), mapped_block['java'][1])
              else:
                java_block = anvil.Block(*mapped_block['java'][0].split(':', 1))

              block_cache[bcid] = java_block

            # Once we have the Java block, add it to the region
            region.set_block(java_block, ax, ay, az)

      # TODO: Block post-processing to fix fences, walls, stairs, and more

      # Add the tile doors to the world
      for door in tile.doors:
        zi = range(door.size[2])
        yi = range(door.size[1])

        for dx in range(door.size[0]):
          ax = tile.pos[0] + door.pos[0] + dx
          rx = math.floor(ax / 512)

          for dz in zi:
            az = tile.pos[2] + door.pos[2] + dz
            rz = math.floor(az / 512)

            # Make sure the region is available
            if f'{rx}x{rz}' in region_cache:
              region = region_cache[f'{rx}x{rz}']
            else:
              region = anvil.EmptyRegion(rx, rz)
              region_cache[f'{rx}x{rz}'] = region

            for dy in yi:
              ay = tile.pos[1] + door.pos[1] + dy

              region.set_block(self.door_block, ax, ay, az)

      # Add the tile boundaries to the world
      for boundary in tile.boundaries:
        ax = tile.pos[0] + boundary.x
        az = tile.pos[2] + boundary.z

        # Make sure the region is available
        rx = math.floor(ax / 512)
        rz = math.floor(az / 512)
        if f'{rx}x{rz}' in region_cache:
          region = region_cache[f'{rx}x{rz}']
        else:
          region = anvil.EmptyRegion(rx, rz)
          region_cache[f'{rx}x{rz}'] = region

        for by in range(boundary.h):
          ay = tile.pos[1] + boundary.y + by

          region.set_block(self.boundary_block, ax, ay, az)

      # Add the playerstart regions to the world
      for tile_region in tile.regions:
        if hasattr(tile_region, 'tags') and tile_region.tags == 'playerstart':
          ax = tile.pos[0] + tile_region.pos[0]
          ay = tile.pos[1] + tile_region.pos[1]
          az = tile.pos[2] + tile_region.pos[2]

          # Make sure the region is available
          rx = math.floor(ax / 512)
          rz = math.floor(az / 512)
          if f'{rx}x{rz}' in region_cache:
            region = region_cache[f'{rx}x{rz}']
          else:
            region = anvil.EmptyRegion(rx, rz)
            region_cache[f'{rx}x{rz}'] = region

          region.set_block(self.player_start_block, ax, ay, az)

    # Write regions to files
    os.makedirs(os.path.join(self.world_dir, 'region'), exist_ok=True)
    for k in region_cache:
      region_cache[k].save(os.path.join(self.world_dir, f'region/r.{region_cache[k].x}.{region_cache[k].z}.mca'))

    # For convenience, write the object group to objectgroup.json in the world
    # directory, so JavaWorldToObjectGroup can convert the world back to an
    # object group without any changes.
    og_copy = json.loads(json.dumps(og)) # faster than copy.deepcopy
    for tile in og_copy['objects']:
      tile.pop('blocks', None)
      tile.pop('boundaries', None)
      tile.pop('doors', None)
      tile.pop('height-plane', None)
    with open(os.path.join(self.world_dir, 'objectgroup.json'), 'w') as out_file:
      out_file.write(stringify(og_copy))

    # Create level.dat file
    level = NBTFile('level_template.dat', 'rb')
    level['Data']['LevelName'].value = self.level_name
    level['Data']['LastPlayed'].value = int(time.time()*1000)

    # Place the player spawn above the center of the first tile.
    # This could probably be made a bit smarter, since the center of the tile
    # might still be above the void. For now, this faster solution will have to do.
    level['Data']['SpawnX'].value = int(og['objects'][0]['pos'][0] + og['objects'][0]['size'][0] * 0.5)
    level['Data']['SpawnY'].value = min(255, og['objects'][0]['pos'][1] + og['objects'][0]['size'][1])
    level['Data']['SpawnZ'].value = int(og['objects'][0]['pos'][2] + og['objects'][0]['size'][2] * 0.5)

    level.write_file(os.path.join(self.world_dir, 'level.dat'))