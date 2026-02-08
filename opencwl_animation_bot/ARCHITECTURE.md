# OpenClaw Autonomous Telegram Kids Video Bot - Architecture

## 1. System Overview

This system is designed to be an autonomous content creation agent that integrates with the OpenClaw framework. It operates 24/7, generating high-quality animated videos for kids based on self-generated or user-prompted ideas via Telegram.

### High-Level Components

1.  **OpenClaw Core**: The brain of the operation, managing skills, memory, and decision making.
2.  **Telegram Interface**: The communication layer for users to interact with the bot (start jobs, provide feedback).
3.  **Animation Engine**: A pipeline of open-source tools (Blender, Manim, FFmpeg) to produce content.
4.  **Character Consistency System**: A dedicated module to ensure visual identity is maintained across long videos.
5.  **Self-Learning Loop**: A feedback mechanism to improve prompt engineering and asset quality over time.

---

## 2. Architecture Diagram (Text Representation)

```mermaid
graph TD
    User[Telegram User] -->|Commands/Feedback| TG[Telegram Interface]
    TG -->|Events| OC[OpenClaw Agent Core]

    subgraph "OpenClaw Framework"
        OC -->|Selects| Skill[Animation Skill]
        OC -->|Reads/Writes| Mem[Memory/DB]
        OC -->|Learns| RL[Reinforcement Learning Module]
    end

    subgraph "Animation Pipeline"
        Skill -->|Job Request| Orch[Animation Orchestrator]
        Orch -->|1. Script & Storyboard| LLM[LLM/Script Gen]
        Orch -->|2. Asset Generation| Char[Character Manager]
        Orch -->|3. Scene Composition| Engine[Blender/Manim/Pencil2D]
        Orch -->|4. Assembly| FFmpeg[Video Processor]
    end

    Char -->|Enforce Style| SD[Stable Diffusion (Local)]
    Engine -->|Render Frames| GPU[Local GPU]
    FFmpeg -->|Final MP4| Storage[Local Storage]

    Storage -->|Upload| TG
    RL -->|Optimize Prompts| LLM
```

---

## 3. Component Details

### 3.1 OpenClaw Integration
The bot is implemented as a set of **Skills** within the OpenClaw framework.
-   **Skill Registration**: The `AnimationSkill` class registers itself with the OpenClaw core using a `skills.json` manifest.
-   **Agent Persona**: The "Director" agent utilizes these skills to orchestrate the video production process.
-   **Memory**: Uses a persistent store (SQLite/PostgreSQL) to keep track of:
    -   Character profiles (seeds, descriptors).
    -   Successful prompts vs. failed prompts.
    -   User feedback on specific scenes.

### 3.2 Telegram Interface (`src/telegram`)
-   Uses `python-telegram-bot` for asynchronous communication.
-   **Commands**:
    -   `/start`: Wake up the agent.
    -   `/generate <topic>`: Manually trigger a video generation.
    -   `/status`: Check current render progress.
    -   `/feedback <job_id> <rating>`: Provide input for the self-learning loop.

### 3.3 Character Consistency System (`src/characters`)
To maintain consistency across a 15-minute video:
-   **Profile Store**: A JSON/Database record for each character containing:
    -   Base Seed (for Stable Diffusion).
    -   Fixed Prompt Tags (e.g., "wearing red hoodie", "blue eyes").
    -   Negative Prompt Tags.
    -   3D Model Reference (if using Blender).
-   **Style Guide**: A global style vector or LoRA applied to all generations to ensure the "cinematic kids animation" look.
-   **Validation**: Before a frame is accepted, a visual similarity check (using CLIP or similar) compares it against the master character reference.

### 3.4 Animation Pipeline (`src/animation`)
The 15-minute video is broken down into segments:
1.  **Segmentation**: The script is divided into 30-second "Scenes".
2.  **Parallel Processing**: Scenes can be rendered in parallel if hardware allows.
3.  **Engine Selection**:
    -   **Blender**: For 3D character acting and complex environments.
    -   **Manim**: For educational overlays or 2D motion graphics.
    -   **Stable Diffusion + ControlNet**: For background generation and stylization.
4.  **Assembly**:
    -   **FFmpeg** concatenates scene segments.
    -   **MoviePy** adds transitions, background music, and voiceovers.

### 3.5 Self-Learning Mechanism (`src/memory`)
-   **Metric**: "Engagement Score" (simulated or real from Telegram feedback).
-   **Optimization**:
    -   The system logs the exact prompts used for every scene.
    -   If a scene receives positive feedback, its prompt structure is weighted higher for future generations.
    -   If a scene fails (e.g., character inconsistency detected), the seed/prompt combination is flagged as "avoid".

---

## 4. Directory Structure
See `README.md` for the concrete file layout.
