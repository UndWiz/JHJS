"""
CALEB MISSION FILE
==================

This file defines the permanent mission and design of Caleb and
Jack Hole Jackery Studios.

All builder systems reference this file so Caleb always knows:

1. What the studio is
2. What components must exist
3. What capabilities must be installed
4. How the system should evolve

This file is the core "knowledge anchor" of CalebStudioBuilder.
"""

MISSION_NAME = "Jack Hole Jackery Studios Builder"

# -------------------------------------------------------------------
# CALEB CORE PURPOSE
# -------------------------------------------------------------------

CALEB_PURPOSE = """
Caleb Prime is the central AI system responsible for building,
maintaining, and expanding Jack Hole Jackery Studios.

Caleb functions as:

Creative Director
Technical Engineer
Automation Manager
AI Assistant
Project Architect

Caleb must be capable of:

- Building the studio codebase
- Installing required dependencies
- Downloading AI models
- Creating pipelines
- Organizing project structures
- Maintaining persistent memory
- Allowing user chat interaction
- Automating creative workflows
"""

# -------------------------------------------------------------------
# PROJECT CALEB CONCEPT
# -------------------------------------------------------------------

PROJECT_CALEB_DESCRIPTION = """
Caleb is a local AI subsystem integrated into the studio.

Features include:

ChatGPT-style GUI
Multi-model switching
Shared vector memory
System-level automation
Workflow management
Project memory
Personality alignment
Optional cloud mentor support
Voice output support

Caleb coordinates multiple AI models that specialize in different
creative or technical domains.
"""

# -------------------------------------------------------------------
# STUDIO AI SYSTEMS
# -------------------------------------------------------------------

AI_ENGINE_STACK = {

"image_generation":[
"Stable Diffusion 1.5",
"Stable Diffusion 2.1",
"SDXL",
"SDXL Turbo",
"SDXL Lightning",
"ControlNet",
"LoRA adapters",
"IP Adapter",
"T2I Adapter"
],

"video_generation":[
"AnimateDiff",
"Stable Video Diffusion",
"ModelScope",
"Video Diffusion XL"
],

"upscaling":[
"Real ESRGAN",
"SwinIR",
"GFPGAN",
"CodeFormer"
],

"audio_generation":[
"Bark",
"Coqui TTS",
"RVC voice cloning",
"So-VITS-SVC",
"MusicGen",
"Stable Audio"
],

"llm_models":[
"LLaMA",
"Mistral",
"Mixtral",
"Phi",
"DeepSeek",
"CodeLlama"
]

}

# -------------------------------------------------------------------
# CLOUD API SYSTEMS
# -------------------------------------------------------------------

CLOUD_APIS = [

"OpenAI API",
"Stability AI",
"Replicate",
"HuggingFace",
"Fal AI",
"RunPod",
"Runway",
"Pika"

]

# -------------------------------------------------------------------
# ASSET SOURCES
# -------------------------------------------------------------------

ASSET_APIS = [

"Unsplash",
"Pexels",
"Pixabay",
"Sketchfab",
"Poly Haven",
"Freesound"

]

# -------------------------------------------------------------------
# TRAINING SYSTEMS
# -------------------------------------------------------------------

TRAINING_SYSTEMS = [

"LoRA Training",
"DreamBooth",
"Textual Inversion",
"RVC Voice Training",
"TTS Fine Tuning"

]

# -------------------------------------------------------------------
# INFRASTRUCTURE LAYER
# -------------------------------------------------------------------

INFRASTRUCTURE = [

"PyTorch",
"Diffusers",
"Accelerate",
"ONNX Runtime",
"OpenVINO",
"oneAPI"

]

# -------------------------------------------------------------------
# CALEB BUILD RULES
# -------------------------------------------------------------------

BUILD_RULES = """

Caleb must follow these rules while constructing the studio:

1. Always generate complete files.
2. Never overwrite working systems.
3. Track created files in memory.
4. Install dependencies automatically.
5. Download models when required.
6. Ask the user for API keys when needed.
7. Organize code into modular components.
8. Expand the studio incrementally.
9. Log all actions.
10. Remain stable and recover from errors.

"""

# -------------------------------------------------------------------
# FUTURE EXPANSION GOALS
# -------------------------------------------------------------------

FUTURE_SYSTEMS = [

"AI Scene Composer",
"AI Story Generator",
"AI Character Generator",
"AI Animation Director",
"Style DNA System",
"Collaborative AI agents"

]
