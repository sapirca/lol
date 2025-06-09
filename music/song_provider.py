import os

SONGS_BASE_PATH = "/Users/sapir/repos/lol/music/song_structure"


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
        self.allowed_songs = ["aladdin", "nikki", "sandstorm"]
        self.song_name = None

    def _validate_song_name(self, song_name):
        """Validates that the song name is in the allowed list."""
        if song_name not in self.allowed_songs:
            raise ValueError(
                f"Logger: '{song_name}' is not a valid song name. Allowed songs are: {self.allowed_songs}"
            )

    def _read_file_content(self, file_path, section_title, description):
        """Helper method to read and format file content."""
        try:
            with open(file_path, 'r') as file:
                content = f"### {section_title}\n"
                content += f"{description}\n"
                content += file.read() + "\n\n"
                return content
        except FileNotFoundError:
            return f"### {section_title}\nFile not found: {file_path}\n\n"
        except Exception as e:
            return f"### {section_title}\nError reading file: {str(e)}\n\n"

    def get_lyrics(self, song_name=None):
        """Get the lyrics for a song.
        
        Args:
            song_name (str, optional): The name of the song. If None, uses the current song.
            
        Returns:
            str: Formatted lyrics content
        """
        song_name = song_name or self.song_name
        if not song_name:
            raise ValueError("No song name provided")

        self._validate_song_name(song_name)
        lyrics_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                        f"{song_name}_lyrics.txt")

        description = "The lyrics of the song, with the first number indicating the start time in seconds and the second number indicating the end time:\n"
        description += "Aligning animation changes to the lyrics beginning and ending can enhance the visual experience and create higher quality animations.\n"
        description += "Start Seconds | End Seconds | Label\n"

        return self._read_file_content(lyrics_file_path, "Lyrics", description)

    def get_key_points(self, song_name=None):
        """Get the key points for a song.
        
        Args:
            song_name (str, optional): The name of the song. If None, uses the current song.
            
        Returns:
            str: Formatted key points content
        """
        song_name = song_name or self.song_name
        if not song_name:
            raise ValueError("No song name provided")

        self._validate_song_name(song_name)
        key_points_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                            f"{song_name}_key_points.txt")

        description = f"A list of {song_name} key points and their corresponding start time in seconds:\n"
        description += "Aligning animation changes to the keypoints beginning and ending can enhance the visual experience and create higher quality animations.\n"
        description += "User the labels as a guide to create the animation.\n"
        description += "Start Seconds | End Seconds | Label\n"

        return self._read_file_content(key_points_file_path, "Key Points",
                                       description)

    def get_drum_pattern(self, song_name=None):
        """Get the drum pattern for a song.
        
        Args:
            song_name (str, optional): The name of the song. If None, uses the current song.
            
        Returns:
            str: Formatted drum pattern content
        """
        song_name = song_name or self.song_name
        if not song_name:
            raise ValueError("No song name provided")

        self._validate_song_name(song_name)
        drums_pattern_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                               f"{song_name}_pattern.txt")

        description = (
            "The drum pattern of the song repeats cyclically throughout its duration. "
            "It is represented using relative beats as labels, such as 0.5, 1.5, etc., "
            "which correspond to fractions of a beat based on the BPM (beats per minute). "
            "For instance, if a beat lasts 2 seconds, 0.25 beats would equal 0.5 seconds.\n"
            "The pattern spans 0 to 3.75 beats (4 beats in total) and aligns with every 4th beat. "
            "Two cycles of the pattern are provided as an example. "
            "Aligning animation changes to the drum pattern can enhance the visual experience and create higher quality animations.\n"
        )

        return self._read_file_content(drums_pattern_file_path,
                                       "Drums Pattern", description)

    def get_beats(self, song_name=None):
        """Get the beats for a song.
        
        Args:
            song_name (str, optional): The name of the song. If None, uses the current song.
            
        Returns:
            str: Formatted beats content
        """
        song_name = song_name or self.song_name
        if not song_name:
            raise ValueError("No song name provided")

        self._validate_song_name(song_name)
        beats_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                       f"{song_name}_beats.txt")

        description = f"A list of {song_name} beats and their corresponding start time in seconds:\n"
        description += "Label | Seconds\n"

        return self._read_file_content(beats_file_path, "Beats", description)

    def get_bars(self, song_name=None):
        """Get the bars for a song.
        
        Args:
            song_name (str, optional): The name of the song. If None, uses the current song.
            
        Returns:
            str: Formatted bars content
        """
        song_name = song_name or self.song_name
        if not song_name:
            raise ValueError("No song name provided")

        self._validate_song_name(song_name)
        bars_file_path = os.path.join(SONGS_BASE_PATH, song_name,
                                      f"{song_name}_bars.txt")

        description = f"A list of {song_name} bars and "
        description += "their corresponding start time in seconds:\n"
        description += "Label | Seconds\n"

        return self._read_file_content(bars_file_path, "Bars", description)

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
        self.song_name = song_name
        self._validate_song_name(song_name)

        try:
            content = f"## {song_name.capitalize()} Song\n"

            # Get all song components
            content += self.get_bars(song_name)
            content += self.get_beats(song_name)
            content += self.get_key_points(song_name)
            content += self.get_lyrics(song_name)
            content += self.get_drum_pattern(song_name)

            return content
        except Exception as e:
            raise IOError(
                f"Logger: An unexpected error occurred while reading song knowledge for '{song_name}': {e}"
            )
