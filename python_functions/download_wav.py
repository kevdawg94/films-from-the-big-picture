import ffmpeg

#optional step to convert to wav if still MP3
def convert_to_wav(audio_path):
    output_path = os.path.splitext(audio_path)[0] + ".wav"
    ffmpeg.input(audio_path).output(output_path).run(quiet=True, overwrite_output=True)
    return output_path