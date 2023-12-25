import azure.functions as func
import logging
from pydub import AudioSegment
import io
import json
import openai

app = func.FunctionApp()


def TranscribeAnything(myblob: func.InputStream) -> list:
    logging.info(f"Loading Audio {myblob.name}")
    total_audio = AudioSegment.from_file(io.BytesIO(myblob.read()))

    # Break the audio in 10 minute segments
    ten_min = 10 * 60 * 1000
    transcriptions = []
    for i in range(0, len(total_audio), ten_min):
        buffer = io.BytesIO()
        buffer.name = f"{i}-{myblob.name}"
        total_audio[i].export()
        # Transcribe this segment
        total_audio[i:i+ten_min].export(buffer, format=f"mp3")

        transcriptions.append(json.loads(str(openai.Audio.transcribe("whisper-1", buffer)))["text"])
    return transcriptions

@app.blob_trigger(arg_name="myblob", path="uploads/{uploaded_file}.mp3",
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", path="transcriptions/{uploaded_file}.txt", connection="AzureWebJobsStorage")
def TranscribeMp3(myblob: func.InputStream, outputblob: func.Out[func.InputStream]):
    logging.info(f"Loading MP3 {myblob.name}")
    total_audio = AudioSegment.from_mp3(io.BytesIO(myblob.read()))

    # Break the audio in 10 minute segments
    ten_min = 10 * 60 * 1000
    transcriptions = []
    for i in range(0, len(total_audio), ten_min):
        buffer = io.BytesIO()
        buffer.name = f"{i}-{myblob.name}"
        total_audio[i].export()
        # Transcribe this segment
        total_audio[i:i+ten_min].export(buffer, format=f"mp3")

        transcriptions.append(json.loads(str(openai.Audio.transcribe("whisper-1", buffer)))["text"])
    logging.info("Setting output blob")
    outputblob.set(' '.join(transcriptions))
    
@app.blob_trigger(arg_name="myblob", path="uploads/{uploaded_file}.m4a",
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", path="transcriptions/{uploaded_file}.txt", connection="AzureWebJobsStorage")
def TranscribeM4a(myblob: func.InputStream, outputblob: func.Out[func.InputStream]):
    transcriptions = TranscribeAnything(myblob)
    outputblob.set(' '.join(transcriptions))


# @app.blob_trigger(arg_name="myblob", path="uploads/{uploaded_file}.mp3",
#                   connection="AzureWebJobsStorage")
# def ConvertUploadedMp3(myblob: func.InputStream):
#     logging.info(f"Python blob trigger function processed blob"
#                 f"Name: {myblob.name} ({myblob.uploaded_file}) \n)"
#                 f"Blob Size: {myblob.length} bytes")