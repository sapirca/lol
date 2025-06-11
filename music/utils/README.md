# Audacity Label Generator

This utility generates Audacity label files for different musical elements based on BPM and duration. All output files are saved in the `music/utils/output` directory.

## Usage Examples

### Generate Beat Labels
Generate beat labels for a 120 BPM song that's 180 seconds long:
```bash
python music/utils/generate_audacity_labels.py --bpm 120 --duration 180 --type beats --song "song_name"
```
<!-- python music/utils/generate_audacity_labels.py --bpm 94 --duration 232 --type phrase --song "infrasound" -->

### Generate Bar Labels
Generate bar labels and save to a custom file:
```bash
python music/utils/generate_audacity_labels.py --bpm 120 --duration 180 --type bars --song "My Song" --output my_labels.txt
```

### Generate Phrase Labels
Generate phrase labels for a 120 BPM song (default 8 bars per phrase):
```bash
python music/utils/generate_audacity_labels.py --bpm 120 --duration 180 --type phrase --song "My Song"
```

Generate phrase labels with 16 bars per phrase:
```bash
python music/utils/generate_audacity_labels.py --bpm 120 --duration 180 --type phrase --song "My Song" --bars-per-phrase 16
```

## Parameters

- `--bpm`: Beats per minute (required)
- `--duration`: Duration in seconds (required)
- `--type`: Type of labels to generate (required, choices: beats, bars, phrase)
- `--song`: Name of the song (required)
- `--bars-per-phrase`: Number of bars per phrase (optional, default: 8, choices: 8 or 16)
- `--output`: Output file name (optional, default: {song_name}_{bpm}bpm_{type}_labels.txt)

## Output

All label files are saved in the `music/utils/output` directory. If no output filename is specified, the file will be named:
- For beats and bars: `{song_name}_{bpm}bpm_{type}_labels.txt` (e.g., `My Song_120bpm_beats_labels.txt`)
- For phrases: `{song_name}_{bpm}bpm_{type}{bars_per_phrase}_labels.txt` (e.g., `My Song_120bpm_phrase8_labels.txt` or `My Song_120bpm_phrase16_labels.txt`)