# OpenClaw Autonomous Telegram Kids Video Bot

This project is an autonomous video generation agent that integrates with the OpenClaw framework. It generates 15+ minute cinematic animated videos for kids using open-source tools (Blender, Manim, FFmpeg).

**Current Status:** Phase 1 Foundation (Architecture, Core Skills, Consistency System, Orchestrator).

---

## 🚀 Features

*   **Autonomous Operation**: Runs 24/7 generating content.
*   **OpenClaw Skill Integration**: Uses modular skills for tasks.
*   **Character Consistency**: Ensures characters look identical across scenes using seed management and style guides.
*   **Kids Content Safety**: Built-in prompt filtering and safety checks.
*   **Hybrid Rendering**: Run locally on a laptop or scale to cloud GPUs via Modal.com.
*   **Fault Tolerance**: Automatic retries for failed renders and fallback generation.

---

## 📂 Project Structure

```
opencwl_animation_bot/
├── src/
│   ├── core/              # Main entry point, Skill Interface, Config Loader
│   ├── skills/            # Animation Skill Definition
│   ├── characters/        # Character Consistency Manager
│   ├── animation/         # Rendering Orchestrator & Backends (Local/Modal)
│   ├── telegram/          # Bot Interface (Future Phase)
│   └── memory/            # Self-learning Storage (Future Phase)
├── assets/
│   ├── characters/        # Character profiles (JSON)
│   ├── scenes/            # Scene templates
│   └── output/            # Generated videos
├── config/                # Configuration files
├── docs/                  # Architecture & Review Logs
└── ARCHITECTURE.md        # System Architecture Document
```

---

## 🛠️ Setup & Usage

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone <repo_url>
cd opencwl_animation_bot
pip install -r requirements.txt
```

### 2. Configuration

Edit `config/settings.yaml` to configure the bot.

**Key Settings:**
*   `render_backend`: Set to `"local"` (for laptop) or `"modal"` (for cloud).
*   `backend_config.max_concurrent_renders`: Set based on your hardware (e.g., `1` for laptop, `10` for cloud).

**Environment Variables:**
You can use environment variables in the config (e.g., `${TELEGRAM_TOKEN}`).

### 3. Running the Bot (Simulation)

Run the core logic simulation:

```bash
python3 src/core/main.py
```

This will:
1.  Initialize the skill registry.
2.  Configure the animation skill with `settings.yaml` defaults.
3.  Simulate a video generation request ("The Solar System for Kids").
4.  Dispatch render jobs (locally or remotely).
5.  Assemble the final video.

---

## ☁️ Deployment: Laptop vs. Cloud

### Option A: Laptop (Local Mode)
Best for development and testing.

1.  Set `render_backend: "local"` in `settings.yaml`.
2.  Set `max_concurrent_renders: 1` or `2` to avoid freezing your machine.
3.  Ensure Blender and FFmpeg are installed locally.

### Option B: Cloud (Modal.com)
Best for production and high-quality rendering.

1.  Install Modal: `pip install modal`.
2.  Set up your Modal account: `modal token new`.
3.  Deploy the remote function (template in `src/animation/modal_stub_example.py`).
4.  Set `render_backend: "modal"` in `settings.yaml`.

---

## 🛡️ Safety & Consistency

*   **Content Safety**: The `ContentSafety` class filters prompts for unsafe keywords before generation.
*   **Character Consistency**: The `CharacterManager` uses `reference_image_path` and consistent seeds to maintain character identity across scenes.

## 📝 License

MIT
