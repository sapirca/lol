// /Users/sapir/repos/led-rings/src/animation/animation.ts
export class Animation {
  constructor(
    public name: string,
    public bpm: number,
    public totalTimeSeconds: number,
    public startOffsetSeconds: number = 0
  ) { }

  public sync(cb: Function): void;
  public addEffect(effect: Effect | Function): void;
  public getSequence(): SequencePerThing;
}

// /Users/sapir/repos/led-rings/src/effects/coloring.ts
export const constColor = (hue: number, sat: number, val: number): void;
export const rainbow = (): void;

// /Users/sapir/repos/led-rings/src/effects/brightness.ts
export const fadeIn = (opt?: { start: number; end: number }): void;
export const fadeOut = (opts?: { start: number; end: number }): void;
export const fadeInOut = (opts?: { min: number; max: number }): void;
export const fadeOutIn = (opts?: { min?: number; max?: number }): void;
export const blink = (opts?: { low: number; high: number }): void;

// /Users/sapir/repos/led-rings/src/effects/motion.ts
export const snake = (): void;
export const snakeInOut = (opt?: { start: number; end: number }): void;

// /Users/sapir/repos/led-rings/src/effects/types.ts
export type EffectConfig = {
  start_time: number;
  end_time: number;
  segments: SegmentName;
  repeat_num?: number;
  repeat_start?: number;
  repeat_end?: number;
};

export type ConstColor = {
  color: {
    hue: number;
    sat: number;
    val: number;
  };
};

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
};

// /Users/sapir/repos/led-rings/src/time/time.ts
export const beats = (startBeat: number, endBeat: number, cb: Function): void;
export const cycleBeats = (
  beatsInCycle: number,
  startBeat: number,
  endBeat: number,
  cb: Function
): void;