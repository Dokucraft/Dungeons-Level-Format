import math
import zlib
import base64

"""
This module contains useful classes for different tile-related objects.

The documentation here isn't great, but hopefully most of the function names
are self-explanatory.

There are still some parts that aren't implemented yet and parts that could be
optimized better.
"""

def decompress(s):
  return zlib.decompress(base64.b64decode(s))

def compress(b):
  return base64.b64encode(zlib.compress(b, 9)).decode('utf-8')


class Boundary:
  """
  Tile boundary, which is a column of invisible, solid blocks.
  Boundaries only have solid walls; the top and bottom are not solid.
  """
  def __init__(self, x, y, z, h):
    self.x = x
    self.y = y
    self.z = z
    self.h = h

  @staticmethod
  def from_bytes(bytes_):
    """Returns a Boundary object with properties from the given bytes."""
    return Boundary(
      x = bytes_[0] << 8 | bytes_[1],
      y = bytes_[2] << 8 | bytes_[3],
      z = bytes_[4] << 8 | bytes_[5],
      h = bytes_[6] << 8 | bytes_[7])

  def bytes(self):
    """Returns the boundary represented as bytes."""
    return bytes([
      self.x >> 8 & 0xff, self.x & 0xff,
      self.y >> 8 & 0xff, self.y & 0xff,
      self.z >> 8 & 0xff, self.z & 0xff,
      self.h >> 8 & 0xff, self.h & 0xff])


class Door:
  """
  Tile door, which is a tile connection or teleport point.
  """
  def __init__(self, pos = [0, 0, 0], size = [1, 1, 1]):
    self.pos = pos
    self.size = size

  @staticmethod
  def from_dict(dict_door):
    """Returns a Door object with properties from the given dict."""
    door = Door(dict_door['pos'], dict_door['size'])

    if 'name' in dict_door:
      door.name = dict_door['name']

    if 'tags' in dict_door:
      door.tags = dict_door['tags']

    return door

  def dict(self):
    """Returns the door represented as a dict."""
    dict = {}

    if hasattr(self, 'name'):
      dict['name'] = self.name

    if hasattr(self, 'tags'):
      dict['tags'] = self.tags

    dict['pos'] = self.pos
    dict['size'] = self.size

    return dict


class Region:
  """
  Tile region, which is an area marker that can be used set up triggers
  or place objects in the level.

  Not yet implemented:
  - 'locked' property
  """
  def __init__(self, pos = [0, 0, 0], size = [1, 1, 1]):
    self.pos = pos
    self.size = size

  @staticmethod
  def from_dict(dict_region):
    """Returns a Region object with properties from the given dict."""
    region = Region(dict_region['pos'], dict_region['size'])

    if 'name' in dict_region:
      region.name = dict_region['name']

    if 'tags' in dict_region:
      region.tags = dict_region['tags']

    if 'type' in dict_region:
      region.type = dict_region['type']

    return region

  def dict(self):
    """Returns the region represented as a dict."""
    dict = {}

    if hasattr(self, 'name'):
      dict['name'] = self.name

    if hasattr(self, 'tags'):
      dict['tags'] = self.tags

    if hasattr(self, 'type'):
      dict['type'] = self.type

    dict['pos'] = self.pos
    dict['size'] = self.size

    return dict


class Tile:
  """
  A tile is a cuboid chunk of blocks. They are pieced together to create
  the levels in Dungeons.

  Not yet implemented:
  - 'is-leaky' property
  - 'locked' property
  - 'pos' property
  - 'tags' property
  - 'walkable-plane' property
  """
  def __init__(self, name, size):
    self.id = name
    self.size = size
    self.volume = size[0] * size[1] * size[2]
    self.blocks = bytearray([0] * math.ceil(self.volume * 1.5))
    self.region_plane = bytearray([0] * (size[0] * size[2]))
    self.y = 0
    self.boundaries = []
    self.doors = []
    self.regions = []

  @staticmethod
  def from_dict(dict_tile):
    """Returns a Tile object with properties from the given dict."""
    tile = Tile(dict_tile['id'], dict_tile['size'])
    tile.blocks = decompress(dict_tile['blocks'])
    tile.region_plane = decompress(dict_tile['region-plane'])

    if 'y' in dict_tile:
      tile.y = dict_tile['y']

    if 'doors' in dict_tile:
      tile.doors = list(map(lambda d: Door.from_dict(d), dict_tile['doors']))

    if 'regions' in dict_tile:
      tile.regions = list(map(lambda r: Region.from_dict(r), dict_tile['regions']))

    boundaries_bytes = decompress(dict_tile['boundaries'])
    for i in range(0, len(boundaries_bytes), 8):
      tile.boundaries.append(Boundary.from_bytes(boundaries_bytes[i:i+8]))

    return tile

  def dict(self):
    """Returns the tile represented as a dict."""
    obj = {
      'id': self.id,
      'size': self.size,
      'blocks': compress(self.blocks),
      'region-plane': compress(self.region_plane)
    }

    height_map = [0] * (self.size[0] * self.size[2])
    for x in range(0, self.size[0]):
      for z in range(0, self.size[2]):
        for y in range(min(self.size[1] - 1, 255), -1, -1):
          if self.get_block(x, y, z)[0] != 0:
            height_map[z * self.size[0] + x] = y
            break
    obj['height-plane'] = compress(bytes(height_map))
    obj['region-y-plane'] = obj['height-plane']

    if len(self.boundaries) > 0:
      boundaries = bytearray()
      for boundary in self.boundaries:
        boundaries.extend(boundary.bytes())
      obj['boundaries'] = compress(boundaries)

    if self.y != 0:
      obj['y'] = self.y

    if len(self.doors) > 0:
      obj['doors'] = list(map(lambda d: d.dict(), self.doors))

    if len(self.regions) > 0:
      obj['regions'] = list(map(lambda r: r.dict(), self.regions))

    return obj

  def resize(self, x, y, z):
    """
    Resizes the tile to the given size.

    Anything that is dependant on the tile's size is reset.
    """
    self.size = [x, y, z]
    self.volume = x * y * z
    self.blocks = [0] * math.ceil(self.volume * 1.5)
    self.region_plane = [0] * (self.size[0] * self.size[2])

  def get_block(self, x, y, z):
    """Returns a tuple with the block ID and data value of the block at the given position."""

    block_id_index = (y * self.size[2] + z) * self.size[0] + x
    if block_id_index % 2 == 0:
      return (
        self.blocks[block_id_index],
        self.blocks[math.floor(block_id_index / 2) + self.volume] >> 4)
    else:
      return (
        self.blocks[block_id_index],
        self.blocks[math.floor(block_id_index / 2) + self.volume] & 0xf)

  def set_block(self, x, y, z, block_id, block_data):
    """Sets the block at the given position to the given block ID and data value."""

    block_id_index = (y * self.size[2] + z) * self.size[0] + x
    block_data_index = math.floor(block_id_index / 2) + self.volume

    self.blocks[block_id_index] = block_id

    if block_id_index % 2 == 0:
      self.blocks[block_data_index] = self.blocks[block_data_index] & 0x0f | block_data << 4
    else:
      self.blocks[block_data_index] = self.blocks[block_data_index] & 0xf0 | block_data

  def get_region_value(self, x, z):
    """Returns the value of the region plane at the given position."""

    return self.region_plane[z * self.size[0] + x]

  def set_region_value(self, x, z, value):
    """Sets the value of the region plane at the given position to the given value."""

    self.region_plane[z * self.size[0] + x] = value