import json
from animation.frameworks.kivsee.renderer.render import Render
from configs.config_kivsee import config


def main():
    render = Render()
    # render.load_from_snapshot(snapshot_dir="try_me", animation_name=config["song_name"])
    
    animation_file_path = f"animation/frameworks/kivsee/tmp_animation/aladdin.json"
    with open(animation_file_path, 'r') as file:
        animation_data = json.load(file)

    print("****************run_renderer*****************")
    render.render(animation_data, animation_name="aladdin", playback_offest=0, store_animation=True)

    render.trigger_song("aladdin", 0)

if __name__ == "__main__":

    
    main()

# Speaker
# 1. Understand song notes
# 2. synchronize with the right miliseconds
# 3. beats - millis
# 4. add offset

# Proto not readable?
# Make animation beautiful
# Surpises - in the right part of song
# what is the line that connects the story
# Either have the same color between the two parts or have a line that connects them
# Need to have animation of the song
