 
```typescript
import { Effect } from "./effects/types";
import { sendSequence, SequencePerThing } from "./services/sequence";
import { trigger } from "./services/trigger";
import { Animation } from "./animation/animation";
import { beats, cycleBeats } from "./time/time";
import { constColor } from "./effects/coloring";
import { elements } from "./objects/elements";

const song_name = "sandstorm";

const testSequence = async () => {
    const testAnimation = new Animation(song_name, 128, 30);
    testAnimation.sync(() => {
        beats(0, 15, () => { // 15 because we only need to consider up to 16 bars
            elements([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], () => {
                const colors = [
                    { hue: 0.0, saturation: 1.0, brightness: 1.0 },   // Red
                    { hue: 0.3, saturation: 1.0, brightness: 1.0 },   // Green
                    { hue: 0.6, saturation: 1.0, brightness: 1.0 },   // Blue
                    { hue: 0.8, saturation: 1.0, brightness: 1.0 },   // Purple
                ];
                for (let i = 0; i < 16; i++) {
                    const currentColor = colors[i % colors.length];
                    constColor(currentColor.hue, currentColor.saturation, currentColor.brightness);
                    cycleBeats(1, i * 2, (i + 1) * 2, () => {}); // Change color every half beat
                }
            });
        });
    });

    await sendSequence(song_name, testAnimation.getSequence());
    await trigger(song_name);
};

(async () => {
    await testSequence();
})();
```
