import animation.songs.structures as song_structures


class SongProvider:

    def __init__(self):
        pass

    def get_song_structure(self, song_name):
        song_names = ["nikki", "sandstorm", "req", "overthinker", "aladdin"]
        match song_name.lower():
            case "nikki":
                return song_structures.nikki_song_prompt
            case "sandstorm":
                return song_structures.sandstorm_song_prompt
            case "req":
                return song_structures.requiem_song_prompt
            case "overthinker":
                return song_structures.overthinker_song_prompt
            case "aladdin":
                return song_structures.aladdin_song_prompt
            case _:
                raise ValueError(
                    f"Invalid song name '{song_name}'. Available songs: {song_names}"
                )
