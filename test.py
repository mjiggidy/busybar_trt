WIFI_ADDRESS = "172.16.173.39"
WIFI_KEY     = "1234"
APP_NAME     = "busytrt"

OFFSET_TEXT = (18, 1)

ICON = "icon.gif"

runtime_text = "03:00:16:01"

from busylib import BusyBar, types, converter

def normalize_bar(runtimes:list[int]):

	data = runtimes
	target_total = 53

	total = sum(data)
	raw_scaled = [x / total * target_total for x in data]

	# Take integer parts
	scaled = [int(x) for x in raw_scaled]

	# istribute remaining points to items with the largest fractional parts
	remainder = target_total - sum(scaled)
	remainders = [x - int(x) for x in raw_scaled]
	indices = sorted(range(len(data)), key=lambda i: remainders[i], reverse=True)

	for i in indices[:remainder]:
		scaled[i] += 1

	return scaled

def write_runtime_bar(runtimes:list[int]) -> bytes:
	
	from PIL import Image, ImageColor

	import random, io

	img = Image.new("RGB", (53, 2))

	offset = 0
	hue = int(random.randrange(0,360))

	for width in normalize_bar(runtimes):

		hue += 100
		
		color_main = ImageColor.getrgb(f"hsv({hue}, 100%, 100%)")
		color_shadow = ImageColor.getrgb(f"hsv({hue}, 100%, 25%)")
	
		for x in range(width):


			img.putpixel((offset + x,0), color_main)
			img.putpixel((offset + x,1), color_shadow)

		offset += width

	buffer = io.BytesIO()
	img.save(buffer, format="GIF")

	return buffer.getvalue()

runtime_bar_bytes = write_runtime_bar([
	28748,
	27937,
	23845,
	17526,
	24755,
	22821,
	22292,
	19877,
	25718,
	15154,
	13900,
	17012,
])

with open(ICON, "rb") as handle_icon:
	filename_icon, payload_icon = converter.convert_for_storage("icon.png", handle_icon.read())

filename_bar, payload_bar = converter.convert_for_storage("test_bar.png", runtime_bar_bytes)

with BusyBar(WIFI_ADDRESS, token=WIFI_KEY) as bb:

	bb.assets_upload(application_name=APP_NAME, filename=filename_icon, data=payload_icon)
	bb.assets_upload(application_name=APP_NAME, filename=filename_bar, data=payload_bar)

	runtime_text = types.TextElement(
		id = "runtime_text",
		type = "text",
		x = OFFSET_TEXT[0],
		y = OFFSET_TEXT[1],
		text=runtime_text,
		font="normal",
		color=[255,175,0],
		display=types.DisplayName.FRONT,
	)

	runtime_bar = types.ImageElement(
		id = "runtime_icon",
		type="image",
		x=OFFSET_TEXT[0],
		y=OFFSET_TEXT[1] + 9 + 2,
		path=filename_bar,
		display=types.DisplayName.FRONT,
	)

	runtime_icon = types.ImageElement(
		id = "runtime_bar",
		type="image",
		x=2,
		y=2,
		path=filename_icon,
		display=types.DisplayName.FRONT,
	)

	payload = types.DisplayElements(
		application_name=APP_NAME,
		elements=[runtime_icon, runtime_bar, runtime_text],
	)

	bb.display_draw(payload, clear_before_draw=True)