import ctypes
import requests, ics, arrow, os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

# Variables
calendar_url = '' # Link to a calendar in .ics format
timezone = 'Asia/Manila'
img_path = '' # Path to wallpaper
font_path = 'C:\Windows\Fonts\Courier New\COURBD.TTF' # Path to font
font_size = 24

position = 'north' # Position of the calendar; any of center, north, south, east, west, northeast, northwest, southeast, southwest OR custom coordinates
max_length = 48 # Max length of characters for each event name
max_events = 16 # To display
border_v = '│'
border_h = '─'
corner_ne = '┌'
corner_nw = '┐'
corner_se = '┘'
corner_sw = '└'
split_n = '┬'
split_s = '┴'
pad = ' '

# Program
os.chdir(os.path.dirname(os.path.realpath(__file__)))
calendar = ics.Calendar(requests.get(calendar_url).text)

events = [((int(event.begin.strftime('%m')), int(event.begin.strftime('%d')), int(event.begin.strftime('%H')), int(event.begin.strftime('%M'))), event) for event in calendar.events if event.begin > arrow.now() or event.end > arrow.now()]
events = sorted(events, key=lambda x: x[0][0]*1000000 + x[0][1]*10000 + x[0][2]*100 + x[0][3])[:max_events]

output = []
for event_tuple in events:
    time = event_tuple[1].begin.astimezone(arrow.now(tz=timezone).tzinfo).strftime(f'%m/%d{pad}│{pad}%H:%M')
    event = event_tuple[1].name
    if len(event) > max_length:
        event = event[:max_length] + border_v
    else:
        event = event.ljust(max_length, pad) + border_v
    line = f'{border_v}{pad}{time}{pad}{border_v}{pad}{event}'
    output.append(line)

draw_text = f'{corner_ne}{border_h}Date{border_h*2}{split_n}{border_h}Time{border_h*2}{split_n}{border_h*1}Event' + border_h*(max_length-5) + corner_nw + '\n'
draw_text += '\n'.join(output)
draw_text += f'\n{corner_sw}{border_h*7}{split_s}{border_h*7}{split_s}' + border_h*(max_length+1) + corner_se 
print(draw_text)

img = Image.open(img_path)
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(font_path, font_size)

bbox = img.getbbox()
width_img = bbox[2]
height_img = bbox[3]
width_textbox, height_textbox = draw.textsize(draw_text, font=font)

match position:
    case 'center':
        x = width_img/2 - width_textbox/2
        y = height_img/2 - height_textbox/2
    case 'north':
        x = width_img/2 - width_textbox/2
        y = height_img/4 - height_textbox/2
    case 'south':
        x = width_img/2 - width_textbox/2
        y = height_img - height_img/4 - height_textbox/2
    case 'west':
        x = width_img/4 - width_textbox/2
        y = height_img/2 - height_textbox/2
    case 'east':
        x = width_img - width_img/4 - width_textbox/2
        y = height_img/2 - height_textbox/2
    case 'northwest':
        x = width_img/4 - width_textbox/2
        y = height_img/4 - height_textbox/2
    case 'northeast':
        x = width_img - width_img/4 - width_textbox/2
        y = height_img/4 - height_textbox/2
    case 'southwest':
        x = width_img/4 - width_textbox/2
        y = height_img - height_img/4 - height_textbox/2
    case 'southeast':
        x = width_img - width_img/4 - width_textbox/2
        y = height_img - height_img/4 - height_textbox/2
    case (x, y):
        x, y = x, y

draw.text((x, y), draw_text, (255, 255, 255), font=font)
img.save('wallpaper.jpg')
ctypes.windll.user32.SystemParametersInfoW(20, 0, working_directory+'\wallpaper.jpg', 3)
