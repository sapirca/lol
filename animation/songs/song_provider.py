import animation.songs.structures as song_structures


class SongProvider:

    def __init__(self):
        pass

    def get_song_structure(self, song_name):
        match song_name.lower():
            case "nikki":
                return song_structures.nikki_song_prompt
            case "other_song":
                return song_structures.other_song_prompt
            case _:
                return "Song not found"

        # Implement the logic to retrieve other song structures
