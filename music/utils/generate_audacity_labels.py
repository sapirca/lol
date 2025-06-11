#!/usr/bin/env python3

import argparse
import math
import os

def calculate_beat_duration(bpm):
    """Calculate the duration of one beat in seconds."""
    return 60.0 / bpm

def generate_labels(bpm, duration, label_type, bars_per_phrase=8):
    """Generate labels based on BPM and duration."""
    beat_duration = calculate_beat_duration(bpm)
    labels = []
    offset = 10.2
    
    if label_type == "beats":
        # Generate beat labels
        for i in range(int(duration / beat_duration) + 1):
            start_time = offset + i * beat_duration
            end_time = start_time
            labels.append(f"{start_time:.6f}\t{end_time:.6f}\tb {i}")
            
    elif label_type == "bars":
        # Generate bar labels (4 beats per bar)
        bar_duration = beat_duration * 4
        for i in range(int(duration / bar_duration) + 1):
            start_time = offset + i * bar_duration
            end_time = start_time
            labels.append(f"{start_time:.6f}\t{end_time:.6f}\tbr {i}")
            
    elif label_type == "phrase":
        # Generate phrase labels (bars_per_phrase bars per phrase)
        phrase_duration = beat_duration * 4 * bars_per_phrase
        for i in range(int(duration / phrase_duration) + 1):
            start_time = offset + i * phrase_duration
            end_time = start_time
            labels.append(f"{start_time:.6f}\t{end_time:.6f}\tphrase {i}")
    
    return labels

def main():
    parser = argparse.ArgumentParser(description='Generate Audacity labels based on BPM')
    parser.add_argument('--bpm', type=float, required=True, help='Beats per minute')
    parser.add_argument('--duration', type=float, required=True, help='Duration in seconds')
    parser.add_argument('--type', type=str, required=True, choices=['beats', 'bars', 'phrase'],
                      help='Type of labels to generate (beats, bars, or phrase)')
    parser.add_argument('--song', type=str, required=True, help='Name of the song')
    parser.add_argument('--bars-per-phrase', type=int, default=8, choices=[8, 16],
                      help='Number of bars per phrase (default: 8, choices: 8 or 16)')
    parser.add_argument('--output', type=str, help='Output file name (default: {song_name}_{bpm}bpm_{type}_labels.txt)')
    
    args = parser.parse_args()
    
    # Generate labels
    labels = generate_labels(args.bpm, args.duration, args.type, args.bars_per_phrase)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Set default output filename if not provided
    if not args.output:
        if args.type == "phrase":
            args.output = f"{args.song}_{args.type}{args.bars_per_phrase}_labels.txt"
        else:
            args.output = f"{args.song}_{args.type}_labels.txt"
    
    # Write to file in the output directory
    output_path = os.path.join(output_dir, args.output)
    with open(output_path, 'w') as f:
        f.write('\n'.join(labels))
    
    print(f"Generated {len(labels)} {args.type} labels and saved to {output_path}")

if __name__ == "__main__":
    main() 