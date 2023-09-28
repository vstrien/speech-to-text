import openai


with open("tracey-value-investor.mp3", "rb") as audio_file:
    with open("tracey-value-investor-output.txt", "w") as f:
        f.write(openai.Audio.transcribe("whisper-1", audio_file))
