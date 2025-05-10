import { Effect } from "./effects/types";
import { sendSequence, SequencePerThing } from "./services/sequence";
import { trigger } from "./services/trigger";
import { Animation } from "./animation/animation";
import { beats, cycleBeats } from "./time/time";
import { constColor } from "./effects/coloring";
import { elements, segment } from "./objects/elements";
import { all, segment_arc, segment_b1, segment_b2 } from "./objects/ring-elements";
import { fadeIn, fadeOut } from "./effects/brightness";
import { snake } from "./effects/motion";

const song_name = "sandstorm";

const testSequence = async () => {
    const testAnimation = new Animation(song_name, 128, 30); // 30 seconds duration for 16 bars
    testAnimation.sync(() => {
        const colors = [
            { hue: 0.0, saturation: 1.0, brightness: 0.3 },  // Red
            { hue: 0.3, saturation: 1.0, brightness: 0.3 },  // Green
            { hue: 0.6, saturation: 1.0, brightness: 0.3 },  // Blue
            { hue: 0.8, saturation: 1.0, brightness: 0.3 },  // Purple
        ];

        // Beats 0-16
        for (let i = 0; i < 16; i++) {
            // For the first 16 beats
            beats(i, i + 1, () => {
                // For all elements
                elements([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], () => {
                    const modulo_index = i % colors.length;
                    // change the color
                    constColor(colors[modulo_index].hue, colors[modulo_index].saturation, colors[modulo_index].brightness);
                });
            });
        }

        // Beats 16-32
        beats(16, 32, () => {
            elements(all, () => {
                // A cycle of 4 beats: in beats 0-1 within this cycle
                cycleBeats(4, 0, 1, () => {
                    constColor(colors[0].hue, colors[0].saturation, colors[0].brightness);
                });
                // A cycle of 4 beats: in beats 1-2 within this cycle
                cycleBeats(4, 1, 2, () => {
                    constColor(colors[1].hue, colors[1].saturation, colors[1].brightness);
                });
                // A cycle of 4 beats: in beats 2-3 within this cycle
                cycleBeats(4, 2, 3, () => {
                    constColor(colors[0].hue, colors[0].saturation, colors[0].brightness);
                });
                // A cycle of 4 beats: in beats 3-4 within this cycle
                cycleBeats(4, 3, 4, () => {
                    constColor(colors[1].hue, colors[1].saturation, colors[1].brightness);
                });
                // A cycle of 8 beats, this cycle overlaps the previos cycle, it's an addition above what already
                // defined. So within a cycle of 8 beats, we will have 2 cycles of 4 beats that were defined before.
                // Of a cycle of 8 beays, put an effect on the first 0-4 beats
                cycleBeats(8, 0, 4, () => {
                    // Put the snake effect of an arc arragment/segment  
                    segment(segment_arc, () => {
                        snake();
                    });
                });
                // Within a cycle of 8 beats, the scond part of it from 4-8 beats, 
                cycleBeats(8, 4, 8, () => {
                    // Put the snake effect of the segment_b1
                    segment(segment_b1, () => {
                        snake();
                    });
                });
            });
        });

        // Beats 32-64
        beats(32, 64, () => {
            elements(all, () => {
                // First beat 0-1 in a cycle of 4
                cycleBeats(4, 0, 1, () => {
                    // On all LEDs put const color
                    constColor(colors[0].hue, colors[0].saturation, colors[0].brightness);
                    // On the LEDs only in segment_b1, put const color
                    segment(segment_b1, () => {
                        constColor(colors[1].hue, colors[1].saturation, colors[1].brightness);
                    });
                });
                // Second beat, 1-2, in a cycle of 4
                cycleBeats(4, 1, 2, () => {
                    // On all LEDs put const color
                    constColor(colors[1].hue, colors[1].saturation, colors[1].brightness);
                    // On the LEDs only in segment_b1, put const color
                    segment(segment_b1, () => {
                        constColor(colors[2].hue, colors[2].saturation, colors[2].brightness);
                    });
                });

                // Third beat, 2-3, in a cycle of 4
                cycleBeats(4, 2, 3, () => {
                    constColor(colors[0].hue, colors[0].saturation, colors[0].brightness);
                    segment(segment_b1, () => {
                        constColor(colors[2].hue, colors[2].saturation, colors[2].brightness);
                    });
                });

                // Fourth beat, 3-4, in a cycle of 4
                cycleBeats(4, 3, 4, () => {
                    constColor(colors[1].hue, colors[1].saturation, colors[1].brightness);
                    segment(segment_b1, () => {
                        constColor(colors[3].hue, colors[3].saturation, colors[3].brightness);
                    });
                });

            });
        });

    });

    // Send and trigger the animation sequence
    await sendSequence(song_name, testAnimation.getSequence());
    await trigger(song_name);
};

(async () => {
    await testSequence();
})();