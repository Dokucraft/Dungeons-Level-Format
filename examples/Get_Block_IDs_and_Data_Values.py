import zlib
import base64
import math

# Function for getting the ID and data value of a block at x,y,z in the bytes
# object.
def get_block(bytes, tile_size, x, y, z):
  tile_volume = tile_size[0] * tile_size[1] * tile_size[2]
  block_id_index = (y * tile_size[2] + z) * tile_size[0] + x

  # To get the data value of the block, we need to check if the block index is
  # even or odd to know if we need to take the first or latter half of the
  # byte.
  if block_id_index % 2 == 0:
    return {
      'id': bytes[block_id_index],
      'data': bytes[math.floor(block_id_index / 2) + tile_volume] >> 4
    }
  else:
    return {
      'id': bytes[block_id_index],
      'data': bytes[math.floor(block_id_index / 2) + tile_volume] & 0xf
    }


# Example tile.
# It would be better to read this from an object group file, but it will do for
# this example script.
tile = {
  "id": "example_tile_01",
  "pos": [36, 12, 46],
  "size": [7, 3, 7],
  "blocks": "eNpTViYVMIAALan28vKO8vIKTIqBgaOBgYF4qgEAohseFg==",
  "region-plane": "eNpjYCARAAAAMQAB",
  "doors": [
    {"pos": [1, 1, 0], "size": [5, 1, 1]},
    {"pos": [1, 1, 6], "size": [5, 1, 1]}
  ]
}

# Decode and decompress the blocks property.
block_bytes = zlib.decompress(base64.b64decode(tile['blocks']))

# Using the function to get a block.
block = get_block(block_bytes, tile['size'], x = 0, y = 2, z = 4)

# Should be 35 and 8 for the example tile.
print('Block ID: ' + str(block['id']))
print('Block Data Value: ' + str(block['data']))