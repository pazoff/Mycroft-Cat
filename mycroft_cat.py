import os
from cat.mad_hatter.decorators import hook, plugin
from pydantic import BaseModel
from enum import Enum
import subprocess
from datetime import datetime
from threading import Thread

try:
    import mycroft_mimic3_tts
except ImportError as err:
    print(f"Error importing Mycroft Mimic3 TTS: {err}")
    print("Attempting to install Mycroft Mimic3 TTS...")

    try:
        subprocess.run(['pip', 'install', 'mycroft-mimic3-tts[all]'], check=True)
        print("Mycroft Mimic3 TTS has been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Mycroft Mimic3 TTS: {e}")


# Settings

# Select box
class VoiceSelect(Enum):
    Alice: str = 'Alice'
    Eve: str = 'Eve'
    Emily: str = 'Emily'
    Daniel: str = 'Daniel'
    Dave: str = 'Dave'
    Angelina: str = 'Angelina'
    Riccardo: str = 'Riccardo'
    Nikolaev: str = 'Nikolaev'


class MycroftCatSettings(BaseModel):
    # Select
    Voice: VoiceSelect = VoiceSelect.Alice


# Give your settings schema to the Cat.
@plugin
def settings_schema():
    return MycroftCatSettings.schema()


# Function to run Mimic3 process in the background
def run_mimic3_process(command, output_filename, cat):
    # Open the output file for writing in binary mode
    with open(output_filename, "wb") as output_file:
        # Start the Mimic3 process in the background
        mimic3_process = subprocess.Popen(command, stderr=subprocess.DEVNULL, stdout=output_file.fileno())
        # Wait for the Mimic3 process to finish
        mimic3_process.wait()

    # Generate the audio player HTML and send it as a chat message
    mycroft_audio_player = "<audio controls autoplay><source src='" + output_filename + "' type='audio/wav'>Your browser does not support the audio tag.</audio>"
    cat.send_ws_message(content=mycroft_audio_player, msg_type='chat')


# Build Mimic3 command based on selected voice
def build_mimic_command(llm_message: str, cat):
    mimic_cmd = ["mimic3", "--cuda"]

    # Load the settings
    settings = cat.mad_hatter.get_plugin().load_settings()
    selected_voice = settings.get("Voice")

    # Check if selected_voice is None or not in the specified list
    if selected_voice not in ["Alice", "Nikolaev", "Daniel", "Angelina", "Emily", "Dave", "Eve", "Riccardo"]:
        selected_voice = "Alice"

    # Voice mapping dictionary
    voice_mapping = {
        "Alice": ("en_US/vctk_low", "p303"),
        "Eve": ("en_US/ljspeech_low", None),
        "Daniel": ("en_US/hifi-tts_low", "6097"),
        "Emily": ("en_US/hifi-tts_low", "92"),
        "Angelina": ("it_IT/mls_low", "8384"),
        "Dave": ("en_US/cmu-arctic_low", "aew"),
        "Nikolaev": ("ru_RU/multi_low", "nikolaev"),
        "Riccardo": ("it_IT/riccardo-fasol_low", None),
    }

    # Set default values if selected_voice is not in the mapping
    voice_cmd, speaker_cmd = voice_mapping.get(selected_voice, ("en_US/vctk_low", "p303"))

    mimic_cmd.extend(["--voice", voice_cmd])

    # Add speaker command if available
    if speaker_cmd is not None:
        mimic_cmd.extend(["--speaker", speaker_cmd])

    mimic_cmd.append(llm_message)

    return mimic_cmd


# Hook function that runs before sending a message
@hook
def before_cat_sends_message(final_output, cat):
    # Get the current date and time
    current_datetime = datetime.now()
    # Format the date and time to use as part of the filename
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    # Specify the folder path
    folder_path = "/admin/assets/voice"

    # Check if the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Construct the output file name with the formatted date and time
    output_filename = os.path.join(folder_path, f"voice_{formatted_datetime}.wav")

    # Get the message sent by LLM
    message = final_output["content"]

    # Specify the Mimic3 command
    command = build_mimic_command(message, cat)

    # Run the run_mimic3_process function in a separate thread
    mimic3_thread = Thread(target=run_mimic3_process, args=(command, output_filename, cat))
    mimic3_thread.start()

    # Return the final output text, leaving Mimic3 to build the audio file in the background
    return final_output
