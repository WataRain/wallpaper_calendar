import ctypes
import requests, ics, arrow, os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

# Variables
calendar_urls = [
    'https://calendar.google.com/calendar/ical/en.philippines%23holiday%40group.v.calendar.google.com/public/basic.ics'
    ]
timezone = 'Asia/Manila'
img_path = r'D:\Path\To\Wallpaper.jpg' # Path to wallpaper
font_path = 'COURBD.TTF' # Path to font
font_size = 24
font_color = (255, 255, 255) # RGB
back_fill_color = (0, 0, 0, 128) # RGBA
position = 'center' # Position of the calendar; any of center, north, south, east, west, northeast, northwest, southeast, southwest OR custom coordinates
max_length = 50 # Max length of characters for each event name
max_events = 20 # To display
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
working_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(working_directory)

events = []
for calendar_url in calendar_urls:
    calendar = ics.Calendar(requests.get(calendar_url).text)
    events += [e for e in calendar.events if e.begin > arrow.now() or e.end > arrow.now()]
events = sorted(events, key=lambda x: x.begin.year*100000000 + x.begin.month*1000000 + x.begin.day*10000 + x.begin.hour*100 + x.begin.minute)[:max_events]

output = []
for event in events:
    monthday = event.begin.astimezone(arrow.now(tz=timezone).tzinfo).strftime('%m/%d')
    if monthday == arrow.now().strftime('%m/%d'):
        monthday = 'Today'
    hourminute = event.begin.astimezone(arrow.now(tz=timezone).tzinfo).strftime('%H:%M')
    time = f'{monthday}{pad}{border_v}{pad}{hourminute}'
    event_name_display = event.name
    if len(event_name_display) > max_length:
        event_name_display = event_name_display[:max_length] + border_v
    else:
        event_name_display = event_name_display.ljust(max_length, pad) + border_v
    line = f'{border_v}{pad}{time}{pad}{border_v}{pad}{event_name_display}'
    output.append(line)

draw_text = f'{corner_ne}{border_h}Date{border_h*2}{split_n}{border_h}Time{border_h*2}{split_n}{border_h*1}Event' + border_h*(max_length-5) + corner_nw + '\n'
draw_text += '\n'.join(output)
draw_text += f'\n{corner_sw}{border_h*7}{split_s}{border_h*7}{split_s}' + border_h*(max_length+1) + corner_se 
print(draw_text)

img = Image.open(img_path)
img.thumbnail((1920, 1080), Image.ANTIALIAS)
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

overlay = Image.new('RGBA', (width_img, height_img))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle((x, y, x+width_textbox, y+height_textbox), fill=back_fill_color)
img.paste(overlay, mask=overlay)
draw.text((x, y), draw_text, font_color, font=font)

img.save('wallpaper.jpg')
ctypes.windll.user32.SystemParametersInfoW(20, 0, working_directory+'\wallpaper.jpg', 3)
