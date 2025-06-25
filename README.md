# ShortsGenerator MVP

A Python application for automatically generating 12-second short videos with meditation quotes and AI-generated backgrounds.

## Description

ShortsGenerator creates professional-quality short videos by combining:
- Meditation quotes from a CSV database
- AI-generated backgrounds
- Beautiful typography and animations
- Social media ready format (9:16 aspect ratio)

## Requirements

- Python 3.13+
- FFmpeg installed on your system

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd shorts-generator
```

2. Install dependencies:
```bash
uv sync
```

## Usage

Launch the Gradio web interface:
```bash
python main.py
```

For development with hot reload:
```bash
gradio main.py
```

The app will start on `http://localhost:7860`

## Features

- **CSV Upload**: Upload quotes database in CSV format
- **Video Generation**: Generate videos with random unused quotes
- **Social Media Text**: Auto-generated posts for social platforms
- **Database Stats**: Track used and unused quotes

## CSV Format

Your quotes CSV should have the following columns:
- ID
- QUOTE
- AUTHOR
- REFLECTION
- SOCIAL_MEDIA_POST
- STATUS# Auto-deploy test Wed Jun 25 20:43:51 CEST 2025
# Workflow test Wed Jun 25 20:51:17 CEST 2025
# Workflow test Wed Jun 25 20:58:29 CEST 2025
# Fresh test Wed Jun 25 21:04:48 CEST 2025
# Fixed Portainer URL Wed Jun 25 21:12:36 CEST 2025
# Docker build test Wed Jun 25 21:27:35 CEST 2025
