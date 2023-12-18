import os
from cat.mad_hatter.decorators import hook
import subprocess
from datetime import datetime

try:
    import mycroft_mimic3_tts
except ImportError as err:
    print(f"Error importing Mycroft Mimic3 TTS: {err}")
    print("Attempting to install Mycroft Mimic3 TTS...")

    try:
        subprocess.run(['pip', 'install', 'mycroft-mimic3-tts'], check=True)
        print("Mycroft Mimic3 TTS has been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Mycroft Mimic3 TTS: {e}")


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
    voice = "en_US/ljspeech_low"
    command = ["mimic3", "--cuda", "--voice", voice, message + "."]

    # Open the file for writing in binary mode
    with open(output_filename, "wb") as output_file:
        # Run the subprocess and redirect the standard output to the file
        mimic3_process = subprocess.run(command, stderr=subprocess.DEVNULL, stdout=output_file.fileno())

    mycroft_audio_player = "<audio controls autoplay><source src='" + output_filename + "' type='audio/wav'>Your browser does not support the audio tag.</audio>"

    # Send mycroft_audio_player to the user
    cat.send_ws_message(content=mycroft_audio_player, msg_type='chat')

    return final_output
