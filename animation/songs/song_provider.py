import animation.songs.structures as song_structures


class SongProvider:

    def __init__(self):
        self.song_names = ["nikki", "sandstorm", "req", "overthinker"]

    def get_song_structure(self, song_name):
        match song_name.lower():
            case "nikki":
                return song_structures.nikki_song_prompt
            case "sandstorm":
                return song_structures.sandstorm_song_prompt
            case "req":
                return song_structures.requiem_song_prompt
            case "overthinker":
                return song_structures.overthinker_song_prompt
            case _:
                return "Song not found"

        # Implement the logic to retrieve other song structures
