intro_prompt = """
### Light Sequence Design Prompt

#### **Your Task**
Design a synchronized light sequence for an EDM track, tailored for a physical art installation composed of interactive elements.

#### **Context**
- **Art Installation:** A "World" consists of multiple physical objects called **Elements**. Each Element has an LED controller. You will receive the Elements' names and spatial arrangement.
- **Music:** An EDM track breakdown will be provided, including musical phrases (e.g., Intro, Breakdown, Build, Drop, Outro) and their duration in bars.
- **Musical Intent:** Each phrase conveys a specific emotional intent:
  - **Intro:** Evoke intrigue.
  - **Breakdown:** Build tension.
  - **Build:** Increase anticipation.
  - **Drop:** Release explosive energy and excitement.
  - **Outro:** Provide a sense of closure.
- **Synchronization:** The light sequence must visually reflect the emotional intent of each phrase.
- **LED Control:** Each Element can be lit with a specific color and brightness. You can control entire Elements or specific LED segments within the strip.

#### **Desired Output**
1. **Design Rationale:** Briefly explain your design choices and any adjustments made based on user feedback.
2. **Light Sequence (DSL):** Provide a structured animation plan where:
   - Each time frame corresponds to a specific musical moment (bar and beat) in the track.
   - For each frame, specify:
     - Which Elements are active.
     - The coloring effect on each Element (e.g., solid color, rainbow).
     - Any relevant parameters (e.g., brightness, speed).
   - Wrap the full sequence within `<animation>` and `</animation>` tags.
   - The animation format must align with the following framework used for light show simulation:
"""
