import argparse
from pathlib import Path
import subprocess
p=argparse.ArgumentParser()
p.add_argument("--engine", choices=["chatterbox","piper"], required=True)
a=p.parse_args()
out=Path("output"); out.mkdir(exist_ok=True)
text="Zbliżasz się do przejścia dla pieszych. Zachowaj szczególną ostrożność i zmniejsz prędkość, aby nie narazić na niebezpieczeństwo pieszego. Ustąp pierwszeństwa pieszemu znajdującemu się na przejściu albo wchodzącemu na nie. Gdy pieszy bezpiecznie opuści twój tor jazdy, upewnij się, że możesz ruszyć. Pamiętaj, bezpieczeństwo jest ważniejsze niż pośpiech."
wav=out/(a.engine+".wav")
if a.engine=="chatterbox":
    import torch
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    torch.set_num_threads(4)
    model=ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    audio=model.generate(text,language_id="pl")
    torchaudio.save(str(wav),audio.cpu(),model.sr)
else:
    from piper import PiperVoice
    import wave
    voice=PiperVoice.load("pl_PL-darkman-medium.onnx")
    with wave.open(str(wav),"wb") as f:
        voice.synthesize_wav(text,f)
subprocess.run(["ffmpeg","-y","-i",str(wav),"-af","loudnorm=I=-16:TP=-1.5:LRA=11","-codec:a","libmp3lame","-b:a","192k",str(out/(a.engine+".mp3"))],check=True)
