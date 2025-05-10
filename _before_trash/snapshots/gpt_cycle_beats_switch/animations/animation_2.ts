
    import { Effect } from "./effects/types";
    import { sendSequence, SequencePerThing } from "./services/sequence";
    import { startSong, trigger } from "./services/trigger";
    import { Animation } from "./animation/animation";
    import { NUMBER_OF_RINGS } from "./sys-config/sys-config";
    import { beats, cycleBeats } from "./time/time";
    import { constColor } from "./effects/coloring";
    import { elements } from "./objects/elements";
    import { all } from "./objects/ring-elements";

    const testSequence = async () => {
        const testAnimation = new Animation("ColorChangeSequence", 128, 32); // 8 bars * 4 beats/bar

        testAnimation.sync(() => {
            elements(all, () => {
                sineColorWaveEffect(0, 8);
                cycleBeats(32, 0, 32, (beat) => {
                    // Change colors every beat
                    switch (beat) {
                        case 0:
                            constColor(0.0, 1.0, 1.0); // Cyan
                            break;
                        case 1:
                            constColor(0.33, 1.0, 1.0); // Yellow
                            break;
                        case 2:
                            constColor(0.66, 1.0, 1.0); // Magenta
                            break;
                        case 3:
                            constColor(0.95, 1.0, 1.0); // Red
                            break;
                        case 4:
                            constColor(0.50, 1.0, 1.0); // Green
                            break;
                        case 5:
                            constColor(0.83, 1.0, 1.0); // Blue
                            break;
                        case 6:
                            constColor(0.16, 1.0, 1.0); // Orange
                            break;
                        case 7:
                            constColor(0.75, 1.0, 1.0); // Purple
                            break;
                    }
                });
            });
        });

        await sendSequence("sandstorm", testAnimation.getSequence());
        await startSong("sandstorm");
    };

    (async () => {
        await testSequence();
    })();
