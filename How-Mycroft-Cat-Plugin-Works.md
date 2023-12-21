# How Mycroft Cat Plugin Works

## Introduction

The Mycroft Cat plugin, designed for the Cheshire Cat platform, integrates the Mycroft Mimic3 Text-to-Speech (TTS) engine. This plugin allows users to convert text messages into spoken audio using various voices. The following guide provides a detailed explanation of the code and functionality of the Mycroft Cat plugin.

## Prerequisites

Before using the Mycroft Cat plugin, ensure that the Cheshire Cat platform is set up. The plugin automatically handles the installation of the required dependencies, including the Mycroft Mimic3 TTS engine. Users do not need to manually install `mycroft-mimic3-tts[all]`.

## Overview

### Importing Modules

The plugin begins by importing necessary modules:

- `os`: Operating system functionality.
- `cat.mad_hatter.decorators`: Decorators for Cat plugins.
- `pydantic.BaseModel`: A base class for creating Pydantic models.
- `enum.Enum`: A standard enumeration class.
- `subprocess`: For subprocess management.
- `datetime.datetime`: For working with date and time.
- `threading.Thread`: For running processes in the background.

### Importing Mycroft Mimic3 TTS

The plugin attempts to import the Mycroft Mimic3 TTS module. If the import fails, the plugin automatically installs it.

### Settings

The plugin defines a selection of voices using an enumeration (`VoiceSelect`). The settings for the plugin are stored in the `MycroftCatSettings` class, which extends `BaseModel`.

### Plugin Registration

The `@plugin` decorator registers the plugin and provides a function (`settings_schema`) to define the settings schema.

### Mimic3 Process Functions

#### 1. `run_mimic3_process`

This function runs the Mimic3 process in the background. It takes a command, output filename, and the Cat instance as parameters. The Mimic3 process is started, and the audio file is generated. The HTML code for an audio player is then sent as a chat message.

#### 2. `build_mimic_command`

This function builds the Mimic3 command based on the selected voice. It uses a mapping dictionary (`voice_mapping`) to determine the voice-specific parameters.

### Cat Hooks

#### 1. `before_cat_sends_message`

This hook function runs before sending a message. It performs the following steps:

- Gets the current date and time.
- Creates a folder for storing audio files if it doesn't exist.
- Constructs the output filename with a timestamp.
- Gets the message sent by the Language Model (LLM).
- Builds the Mimic3 command using the `build_mimic_command` function.
- Runs the Mimic3 process in a separate thread using `run_mimic3_process`.
- Returns the final output text, allowing Mimic3 to build the audio file in the background.

## Conclusion

The Mycroft Cat plugin seamlessly integrates the Mycroft Mimic3 TTS engine into the Cheshire Cat platform. Users can select different voices and generate spoken audio from text messages. The plugin automatically handles the installation of dependencies, ensuring a smooth user experience. Background threads are employed to prevent blocking the main thread during audio file generation.
