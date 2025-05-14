import os

SONGS_BASE_PATH = "/Users/sapir/repos/lol/music/songs"


class SongProvider:
    """
    Provides access to song structures and details for multiple songs.
    Each song is expected to have its own directory within SONGS_BASE_PATH,
    containing files like '{song_name}_bars.txt', '{song_name}_beats.txt',
    and '{song_name}_info.txt'.
    """

    def __init__(self):
        """
        Initializes the SongProvider with a list of allowed songs.
        """
        # Updated to include 'nikki' and 'sandstorm'
        self.allowed_songs = ["aladdin", "nikki", "sandstorm"]
        # self.song_name is not used in this class, consider removing if not needed.
        self.song_name = None

    def get_song_structure(self, song_name):
        """
        Retrieves the detailed structure and information for a given song.

        Args:
            song_name (str): The name of the song to retrieve. This name
                             should correspond to a directory name and
                             file prefix within the SONGS_BASE_PATH.

        Returns:
            str: A formatted string containing the song's structure and details.

        Raises:
            ValueError: If the provided song_name is not in the allowed list.
            IOError: If there's an error reading any of the song-related files
                     (e.g., file not found, permission error).
        """
        if song_name not in self.allowed_songs:
            raise ValueError(
                f"Logger: '{song_name}' is not a valid song name. Allowed songs are: {self.allowed_songs}"
            )

        content = ""
        try:
            content += f"## {song_name.capitalize()} Song Details\n\n"  # Capitalize for better display

            # Construct paths dynamically for any allowed song
            bars_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                          f"{song_name}_bars.txt")
            beats_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                           f"{song_name}_beats.txt")
            info_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                          f"{song_name}_info.txt")

            # Read bars file
            with open(bars_file_path, 'r') as file:
                content += "### Bars\n"
                content += f"A list of {song_name} bars and their corresponding start time in milliseconds:\n"
                content += file.read() + "\n\n"

            # Read beats file
            with open(beats_file_path, 'r') as file:
                content += "### Beats\n"
                content += f"A list of {song_name} beats and their corresponding start time in milliseconds:\n"
                content += file.read() + "\n\n"

            # Read info file
            with open(info_file_path, 'r') as file:
                content += "### Important Song Parts\n"
                content += "These are important parts in the song where you should consider making animation changes:\n"
                content += file.read() + "\n"

            return content
        except FileNotFoundError as e:
            # Provide more specific error message if a file is missing
            raise IOError(
                f"Logger: Song file not found for '{song_name}'. Please ensure all required files "
                f"({song_name}_bars.txt, {song_name}_beats.txt, {song_name}_info.txt) "
                f"exist in '{os.path.join(SONGS_BASE_PATH, song_name)}': {e}")
        except Exception as e:
            # Catch any other potential errors during file reading
            raise IOError(
                f"Logger: An unexpected error occurred while reading song knowledge for '{song_name}': {e}"
            )
