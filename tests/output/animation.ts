
import { Effect } from "./effects/types";
import { sendSequence, SequencePerThing } from "./services/sequence";
import { startSong, trigger } from "./services/trigger";
import { Animation } from "./animation/animation";
import { NUMBER_OF_RINGS } from "./sys-config/sys-config";
import { beats, cycleBeats } from "./time/time";
import { constColor, rainbow } from "./effects/coloring";
import { blink, fadeIn, fadeInOut, fadeOutIn } from "./effects/brightness";
import { elements, segment } from "./objects/elements";
import {
    all,
    segment_arc,
    segment_b1,
    segment_b2,
    segment_centric,
    segment_ind,
} from "./objects/ring-elements";
import { snake, snakeInOut } from "./effects/motion";
import { phase } from "./phase/phase";

const animationSequence = async () => {

    const animation = new Animation("sandstorm", 180, 126); // Assuming 50 is a default phase value
    animation.sync(() => {
        beats(0, 10, () => {
            elements(all, () => {
                constColor({ h: 0.9 });
                fadeIn({ start: 0, end: 1 });
                snake();
            elements(even, () => {
                rainbow();
                blink({ low: 0.5, high: 1 });
                snakeInOut({ start: 0.2, end: 0.8 });
            });
        });
    });
    await sendSequence("sandstorm", animation.getSequence());
    await startSong("sandstorm");

    await trigger();
};


(async () => {{
    await animationSequence();
}})();
