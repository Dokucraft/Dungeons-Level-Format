import zlib
import base64
import math

# Function for setting the ID and data value for a block.
def set_block(blocks, tile_size, x, y, z, block_id, block_data):
  tile_volume = tile_size[0] * tile_size[1] * tile_size[2]
  block_id_index = (y * tile_size[2] + z) * tile_size[0] + x
  block_data_index = math.floor(block_id_index / 2) + tile_volume

  blocks[block_id_index] = block_id

  # To set the data value of the block, we need to check if the block index is
  # even or odd to know if we need to change the first or latter half of the byte.
  if block_id_index % 2 == 0:
    blocks[block_data_index] = blocks[block_data_index] & 0b00001111 | block_data << 4
  else:
    blocks[block_data_index] = blocks[block_data_index] & 0b11110000 | block_data


# In this example, we're starting from scratch without a tile, so we need to create one
# and create a blocks array to modify.
tile = {
  'id': 'my_custom_tile',
  'size': [7, 3, 7]
}
blocks_array = [0] * math.ceil(tile['size'][0] * tile['size'][1] * tile['size'][2] * 1.5)

# Using the function to change a block to light gray wool.
set_block(blocks_array, tile['size'], x = 0, y = 2, z = 4, block_id = 35, block_data = 8)

# Compress and encode the blocks and add them to the tile.
tile['blocks'] = base64.b64encode(zlib.compress(bytes(blocks_array), 9)).decode('utf-8')

print(tile)