import os.path
import json
import re
import PySimpleGUI as sg
import numpy as np
from PIL import Image, ImageTk
from Tile import Tile

# PySimpleGUI window layout

tile_list_column = [
  [
    sg.Text('Object Group'),
    sg.In(size=(25, 1), enable_events=True, key='-OBJECTGROUP-'),
    sg.FileBrowse(),
  ],
  [
    sg.Listbox(
      values=[], enable_events=True, size=(40, 20), key='-TILE LIST-'
    )
  ],
  [sg.Text('0 / Green: Walkable')],
  [sg.Text('1 / Yellow: Walkable, no minimap')],
  [sg.Text('2 / Gray: Not walkable, no minimap')],
  [sg.Text('3 / Blue: Walkable')],
  [sg.Text('4 / Red: Not walkable, no minimap')],
  [sg.Text('Boundary / Magenta: Invisible wall')]
]

tile_viewer_column = [
  [ sg.Text('Select a tile to view', size=(40, 1), key='-TOUT-'),
    sg.Text('Scale:'),
    sg.Slider(range=(1, 8), orientation='h', size=(34, 20), default_value=4, key='-SCALE-', enable_events=True)],
  [ sg.Checkbox('Show boundaries', default=True, key='-BOUNDARIES-', enable_events=True),
    sg.Checkbox('Show height as shade', default=True, key='-HEIGHTMAP-', enable_events=True)
  ],
  [sg.Image(key='-IMAGE-')],
]

layout = [
  [
    sg.Column(tile_list_column),
    sg.VSeperator(),
    sg.Column(tile_viewer_column),
  ]
]

window = sg.Window('Simple Dungeons Tile Viewer', layout)

# Tile image colors
boundaries_color = (0xff, 0x00, 0xc0) # Magenta
region_plane_colors = [
  (0x1c, 0xbf, 0x18), # 0: Green
  (0xed, 0xb2, 0x00), # 1: Yellow/Orange
  (0x36, 0x36, 0x36), # 2: Dark Gray
  (0x00, 0x90, 0xff), # 3: Blue
  (0xb5, 0x11, 0x10)  # 4: Red
]

def update_tile_viewer(values):
  try:
    # Getting the tile from the object group based on the text in the selected list item
    tile_index = int(re.search('^(\d+):', values['-TILE LIST-'][0]).group(1))
    tile_dict = objectgroup['objects'][tile_index]
    t = Tile.from_dict(tile_dict)

    img_data = np.array_split([region_plane_colors[v] for v in t.region_plane], t.size[2])

    # Get / generate and cache tile height map, and apply shading to the image
    if values['-HEIGHTMAP-']:
      if not '_height' in tile_dict:
        tile_dict['_height'] = t.get_height_map()
      zr = range(0, t.size[2])
      for x in range(0, t.size[0]):
        for z in zr:
          img_data[z][x] = [min(255, v * (0.25 + 1.25 * tile_dict['_height'][z * t.size[0] + x] / t.size[1])) for v in img_data[z][x]]

    # Draw boundaries
    if values['-BOUNDARIES-']:
      for b in t.boundaries:
        img_data[b.z][b.x] = boundaries_color

    # Convert array to Pillow image
    img = Image.fromarray(np.array(img_data, dtype=np.uint8), 'RGB')

    # Get image scale from slider
    scale = values['-SCALE-']
    scaled_size = (int(t.size[0] * scale), int(t.size[2] * scale))

    # Update UI with text and image
    window['-TOUT-'].update(values['-TILE LIST-'][0])
    window['-IMAGE-'].update(data=ImageTk.PhotoImage(img.resize(scaled_size, Image.NEAREST)))

  except:
    if values['-TILE LIST-'][0]:
      window['-TOUT-'].update('ERROR while loading tile!')
    else:
      pass

# Run the Event Loop
while True:
  event, values = window.read()
  if event == 'Exit' or event == sg.WIN_CLOSED:
    break

  # Object group file selected
  if event == '-OBJECTGROUP-':
    objectgroupPath = values['-OBJECTGROUP-']
    try:
      with open(objectgroupPath) as json_file:
        objectgroup = json.load(json_file)
        tile_list = objectgroup['objects']
    except:
      objectgroup = None
      tile_list = []

    # Add the index of the tile in front of the ID for the list in the UI, since the ID is sometimes blank
    tids = [str(i) + ': "' + f['id'] + '"' for i, f in zip(range(len(tile_list)), tile_list)]
    window['-TILE LIST-'].update(tids)

  # Tile was selected, or checkbox was (un)checked, or slider was moved
  else:
    update_tile_viewer(values)

window.close()