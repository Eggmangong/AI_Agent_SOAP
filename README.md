# Medical SOAP Note Generation Workflow

An automated medical documentation system that converts audio recordings of patient consultations into structured SOAP (Subjective, Objective, Assessment, Plan) notes using AI-powered speech recognition and natural language processing.

## Overview

This project provides an end-to-end workflow for healthcare professionals to automatically generate SOAP notes from recorded patient consultations. The system combines:

- **Speech-to-Text**: Audio transcription using Google Cloud Speech API
- **AI-Powered Structuring**: Symptom extraction and organization using OpenAI GPT-4
- **SOAP Note Generation**: Automated creation of formatted medical documentation
- **Multiple Output Formats**: Both text and HTML formats for enhanced readability

## Key Features

- 🎵 **Audio Processing**: Converts MP3 recordings to WAV format for optimal transcription
- 🗣️ **Speech Recognition**: High-accuracy transcription using Google Cloud Speech API
- 🤖 **AI Symptom Analysis**: Intelligent extraction and structuring of patient symptoms
- 📝 **SOAP Note Generation**: Automated creation of professional medical documentation
- 🌐 **HTML Output**: Responsive, color-coded HTML format for easy reading
- ⚡ **Workflow Automation**: Complete end-to-end processing with single command execution

## Quick Start

1. Install dependencies:
```bash
pip install google-cloud-speech openai pydub python-dotenv termcolor
```

2. Configure environment variables:
```bash
export OPENAI_API_KEY=your_openai_api_key
export GOOGLE_APPLICATION_CREDENTIALS=./your-service-account.json
```

3. Run the workflow:
```bash
python run_soap_workflow.py
```

## Output

The system generates two formats:
- **Text Format**: `soap_note.txt` - Standard medical documentation
- **HTML Format**: `soap_note.html` - Color-coded, responsive web format

## Requirements

- Python 3.12+
- FFmpeg (for audio conversion)
- Google Cloud Speech API credentials
- OpenAI API key with GPT-4 access

## Disclaimer

This tool is intended for healthcare professionals and should be used as an aid in medical documentation. Always review and validate AI-generated content before using it in clinical settings.
