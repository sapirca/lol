// /Users/sapir/repos/led-rings/src/animation/animation.ts
import { als } from "../async-local-storage";
import { Effect, EffectConfig, Sequence } from "../effects/types";
import { SequencePerThing } from "../services/sequence";

interface EffectWithElements {
  effect: Effect;
  elements: number[];
}

export class Animation {

  private effects: EffectWithElements[] = [];

  constructor(
    public name: string,
    public bpm: number,
    public totalTimeSeconds: number,
    public startOffsetSeconds: number = 0
  ) { }

  public sync(cb: Function) {
    const emptyEffectConfig: Partial<EffectConfig> = {
      segments: "all",
    };
    als.run({ animation: this, effectConfig: emptyEffectConfig }, cb);
  }

  public addEffect(effect: Effect) {
    const store = als.getStore();
    this.effects.push({
      effect,
      elements: store.elements,
    });
  }

  public getSequence(): SequencePerThing {
    const seqPerThing: SequencePerThing = {};
    this.effects.forEach(effectWithElements => {
      effectWithElements.elements.forEach((element: number) => {
        const thingName = `ring${element}`;
        if (!seqPerThing[thingName]) {
          seqPerThing[thingName] = {
            effects: [],
            duration_ms: this.totalTimeSeconds * 1000,
            num_repeats: 0,
          };
        }
        seqPerThing[thingName].effects.push(effectWithElements.effect);
      });
    });
    return seqPerThing;
  }

}

// /Users/sapir/repos/led-rings/src/effects/coloring.ts
import { als } from "../async-local-storage";
import { Effect } from "./types";

export const constColor = (hue: number, sat: number, val: number) => {
  const store = als.getStore();

  const constColorEffect: Effect = {
    effect_config: store.effectConfig,
    const_color: {
      color: {
        hue: hue,
        sat: sat,
        val: val
      }
    }
  };

  const { animation } = store;
  animation.addEffect(constColorEffect);
}
// /Users/sapir/repos/led-rings/src/effects/brightness.ts
import { als } from "../async-local-storage";
import { Effect } from "./types";

const addEffect = (specificEffectConfig: any) => {
  const store = als.getStore();
  const { animation } = store;
  const effect = {
    effect_config: store.effectConfig,
    ...specificEffectConfig,
  };
  animation.addEffect(effect);
};

export const fadeIn = (opt?: { start: number; end: number }) => {
  addEffect({
    brightness: {
      mult_factor: {
        linear: {
          start: opt?.start ?? 0.0,
          end: opt?.end ?? 1.0,
        },
      },
    },
  });
};

export const fadeOut = (opts?: { start: number; end: number }) => {
  addEffect({
    brightness: {
      mult_factor: {
        linear: {
          start: opts?.start ?? 1.0,
          end: opts?.end ?? 0.0,
        },
      },
    },
  });
};

export const fadeInOut = (opts?: { min: number; max: number }) => {
  const min = opts?.min ?? 0.0;
  const max = opts?.max ?? 1.0;
  addEffect({
    brightness: {
      mult_factor: {
        half: {
          f1: {
            linear: {
              start: min,
              end: max,
            },
          },
          f2: {
            linear: {
              start: max,
              end: min,
            },
          },
        },
      },
    },
  });
};

export const fadeOutIn = (opts?: { min?: number; max?: number }) => {
  const min = opts?.min ?? 0.0;
  const max = opts?.max ?? 1.0;
  addEffect({
    brightness: {
      mult_factor: {
        half: {
          f1: {
            linear: {
              start: max,
              end: min,
            },
          },
          f2: {
            linear: {
              start: min,
              end: max,
            },
          },
        },
      },
    },
  });
};

export const blink = (opts?: { low: number; high: number }) => {
  addEffect({
    brightness: {
      mult_factor: {
        half: {
          f1: {
            const_value: {
              value: opts?.low ?? 0.0,
            },
          },
          f2: {
            const_value: {
              value: opts?.high ?? 1.0,
            },
          },
        },
      },
    },
  });
};

// /Users/sapir/repos/led-rings/src/effects/types.ts
import { SegmentName } from "../objects/types";
import { FloatFunction } from "./functions";

export type EffectConfig = {
  start_time: number;
  end_time: number;
  segments: SegmentName;

  repeat_num?: number;
  repeat_start?: number;
  repeat_end?: number;
}

export type ConstColor = {
  color: {
    hue: number;
    sat: number;
    val: number;
  }
}

export type Rainbow = {
  hue_start: FloatFunction;
  hue_end: FloatFunction;
};

export type Brightness = {
  mult_factor: FloatFunction;
};

export type Hue = {
  offset_factor: FloatFunction;
};

export type Saturation = {
  mult_factor: FloatFunction;
};

export type Snake = {
  head: FloatFunction;
  tail_length: FloatFunction;
  cyclic: boolean;
};

export type Segment = {
  start: FloatFunction;
  end: FloatFunction;
};

export type Glitter = {
  intensity: FloatFunction;
  sat_mult_factor: FloatFunction;
};

export type Alternate = {
  numberOfPixels: number;
  hue_offset: FloatFunction;
  sat_mult: FloatFunction;
  brightness_mult: FloatFunction;
};

export type Effect = {
  effect_config: EffectConfig;
  const_color?: ConstColor;
  rainbow?: Rainbow;
  brightness?: Brightness;
  hue?: Hue;
  saturation?: Saturation;
  snake?: Snake;
  segment?: Segment;
  glitter?: Glitter;
  alternate?: Alternate;
};

export type Sequence = {
  effects: Effect[];
  duration_ms: number;
  num_repeats: number;
}
// /Users/sapir/repos/led-rings/src/time/time.ts
import { als } from "../async-local-storage";

const beatToMs = (beat: number, bpm: number) => {
  return beat * 60 / bpm * 1000;
}

export const beats = (startBeat: number, endBeat: number, cb: Function) => {
  const store = als.getStore();
  const { bpm } = store.animation;
  const startTime = beatToMs(startBeat, bpm);
  const endTime = beatToMs(endBeat, bpm);
  const newStore = {
    ...store,
    effectConfig: {
      ...store.effectConfig,
      start_time: startTime,
      end_time: endTime,
    }
  }
  als.run(newStore, cb);
}

export const cycleBeats = (beatsInCycle: number, startBeat: number, endBeat: number, cb: Function) => {
  const store = als.getStore();
  const { bpm } = store.animation;
  const totalBeats = (store.effectConfig.end_time - store.effectConfig.start_time) / 1000 / 60 * bpm;
  const repeatNum = totalBeats / beatsInCycle;

  const newStore = {
    ...store,
    effectConfig: {
      ...store.effectConfig,
      repeat_num: repeatNum,
      repeat_start: startBeat / beatsInCycle,
      repeat_end: endBeat / beatsInCycle,
    }
  }
  als.run(newStore, cb);
}
