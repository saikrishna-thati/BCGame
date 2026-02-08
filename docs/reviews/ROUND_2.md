# Round 2: Consistency, Error Handling & Safety Review

This review round focuses on the robustness of the application, specifically for long-running video generation tasks and content safety for children.

## Reviewer 1: Character Consistency (Company A)
**Focus:** Visual Identity, Long-form Content
*   **Observation:** The `CharacterManager` gets a seed, but for a 15-minute video, simply reusing a seed with Stable Diffusion often isn't enough for perfect consistency.
*   **Problem:** As prompts change (different actions), the seed's influence on facial features might drift.
*   **Recommendation:** Implement a "Reference Anchor" system. The Manager should store a path to a "Reference Image" for each character. If using ControlNet (implied by "cinematic animation"), the pipeline should optionally use this reference image for IP-Adapter or similar consistency tools.
*   **Action:** Update `CharacterManager` to explicitly track `reference_image_path`.

## Reviewer 2: Error Recovery (Company B)
**Focus:** Resilience, Long-running processes
*   **Observation:** `asyncio.gather` is used for rendering scenes.
*   **Problem:** If Scene 29 of 30 fails (e.g., Blender crash), the entire `generate_video` call raises an exception, wasting 14 minutes of computing.
*   **Recommendation:** Use `return_exceptions=True` in `asyncio.gather`. Implement a "Retry" loop for failed scenes (max 3 retries). If it still fails, render a "Fallback/Error" slide (or just a black screen with text) so the video can still be assembled for review.
*   **Impact:** Critical for saving compute costs and user frustration.

## Reviewer 3: Pipeline Flow & Assembly (Company C)
**Focus:** FFmpeg robustness
*   **Observation:** The assembly step assumes all scene videos are perfect.
*   **Problem:** Different engines (Blender vs Manim) might output slightly different codecs or pixel formats, causing FFmpeg concat to fail or produce glitchy video.
*   **Recommendation:** Ensure the `RenderBackend` enforces a strict output format (e.g., `yuv420p`, specific bitrate). The Assembly step should ideally run a "conformance check" before concatenation.

## Reviewer 4: Content Safety (Company D)
**Focus:** Kids Safety, filtering
*   **Observation:** We are generating content for kids.
*   **Problem:** Relying solely on `negative_prompt` is insufficient. A stray "horror" style might slip through.
*   **Recommendation:** Add a `ContentSafety` class. Before dispatching a render, scan the *prompt* for banned keywords. After rendering, (in a real system) scan the image. For now, implement the Prompt Safety Check.
*   **Impact:** Mandatory for "Kids" product.

---

## Action Plan (Round 2)

1.  **Refine `CharacterManager`**: Add `reference_image_path` handling and ensure it's passed to the render context.
2.  **Robust Orchestration**: Update `AnimationOrchestrator` to handle render failures (Retries + Fallback).
3.  **Safety Layer**: Implement `src/core/safety.py` and integrate it into `AnimationSkill`.
