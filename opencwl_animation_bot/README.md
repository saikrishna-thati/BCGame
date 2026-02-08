# OpenClaw Autonomous Telegram Kids Video Bot

This project is an autonomous video generation agent that integrates with the OpenClaw framework. It generates 15+ minute cinematic animated videos for kids using open-source tools (Blender, Manim, FFmpeg).

## 🚀 Features

*   **Autonomous Operation**: Runs 24/7 generating content.
*   **OpenClaw Skill Integration**: Uses modular skills for tasks.
*   **Character Consistency**: Ensures characters look identical across scenes using seed management and style guides.
*   **Animation Pipeline**: Breaks down long scripts into parallel rendering tasks.
*   **Telegram Interface**: Allows users to start jobs and provide feedback.

## 📂 Project Structure

```
opencwl_animation_bot/
├── src/
│   ├── core/              # Main entry point & Skill Interface
│   ├── skills/            # Animation Skill Definition
│   ├── characters/        # Character Consistency Manager
│   ├── animation/         # Rendering Orchestrator & Engines
│   ├── telegram/          # Bot Interface (Future Phase)
│   └── memory/            # Self-learning Storage (Future Phase)
├── assets/
│   ├── characters/        # Character profiles (JSON)
│   ├── scenes/            # Scene templates
│   └── output/            # Generated videos
├── config/                # Configuration files
└── ARCHITECTURE.md        # System Architecture Document
```

## 🛠️ Setup

1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd opencwl_animation_bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    Edit `config/settings.yaml` to set your paths and Telegram token.

## ▶️ Running the Bot (Simulation)

Currently, you can run the core logic simulation:

```bash
python3 src/core/main.py
```

This will initialize the skill registry, configure the animation skill, and simulate a video generation request.

## 🏗️ Development Status

**Phase 1: Foundation (Current)**
-   [x] System Architecture
-   [x] Core Skill Interface
-   [x] Character Consistency Models
-   [x] Animation Orchestrator (Mock)

**Phase 2: Implementation (Next)**
-   [ ] Connect Telegram Bot API
-   [ ] Implement Real Blender Rendering Scripts
-   [ ] Integrate LLM for Script Generation
-   [ ] Add Self-Learning Feedback Loop

## 📝 License

MIT
