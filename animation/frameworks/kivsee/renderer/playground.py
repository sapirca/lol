import render
from render import get_url_content, GET_ANIMATION_URL, GET_OBJECT_URL

# print(get_url_content(GET_ANIMATION_URL.format(animation_name="aladdin", thing_name="spiral_small")))
# print("****************!*****************")
# print(get_url_content(GET_ANIMATION_URL.format(animation_name="aladdin", thing_name="spiral_big")))

# print("****************!*****************")
# print("****************!*****************")
# print(get_url_content(GET_OBJECT_URL.format(thing_name="spiral_small")))
# print("****************!*****************")
# print(get_url_content(GET_OBJECT_URL.format(thing_name="spiral_big")))
# print("****************!*****************")
# print("stats")
# print("****************!*****************")

render_obj = render.Render()
render_obj.trigger_song("aladdin", 0)