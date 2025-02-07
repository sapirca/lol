` tags as requested:

<animation>
```typescript
const song_name = "sandstorm";
const bpm = 126;
const animationDuration = 304; // Duration for the whole song (from structure provided)

const createAnimationSequence = async () => {
  const testAnimation = new Animation(song_name, bpm, animationDuration);
  testAnimation.sync(async () => {
    // 16 Bars: Intro
    await beats(0, 16, () => {
      elements([2, 4], () => {
        constColor(0.0, 1.0, 0.3); // Vibrant colors for intro on elements 2 and 4
        cycleBeats(1, 0, 16, () => {
          blink({ low: 0.1, high: 0.3 }); // Keeping brightness safe
        });
      });
    });

    // 8 Bars: Bridge
    await beats(16, 24, () => {
      elements([4], () => {
        fadeIn({ start: 0.1, end: 0.3 }); // Brightness increase for element 4
      });
    });

    // 16 Bars: Verse 1
    await beats(24, 40, () => {
      elements([2], () => {
        constColor(0.4, 1.0, 0.5); // Fun colors for the verse on element 2
        cycleBeats(1, 0, 16, () => {
          fadeIn({ start: 0.2, end: 0.4 }); // Controlled intensity increase
        });
      });
    });

    // 16 Bars: Build Up 1
    await beats(40, 56, () => {
      elements([2, 4], () => {
        fadeIn({ start: 0.3, end: 0.5 }); // Joint animation for the build-up
      });
    });

    // 16 Bars: Build Up 2
    await beats(56, 72, () => {
      elements([2, 4], () => {
        fadeIn({ start: 0.3, end: 0.5 }); // Continued build-up for both elements
        blink({ low: 0.2, high: 0.4 });  // Maintain excitement
      });
    });

    // 24 Bars: Drop / Chorus
    await beats(72, 96, () => {
      elements([2, 4], () => {
        constColor(0.3, 1.0, 0.3); // Vibrant colors for the drop on both elements
        cycleBeats(0.5, 0, 24, () => {
          blink({ low: 0.2, high: 0.5 }); // Half-beat animations
        });
      });
    });
  });

  await sendSequence(song_name, testAnimation.getSequence());
  await trigger(song_name);
};

(async () => {
  await createAnimationSequence();
})();
```
