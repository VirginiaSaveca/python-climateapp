import pyttsx3

engine = pyttsx3.init()

def notificar_audio(texto):
    try:
        engine.say(texto)
        engine.runAndWait()
    except RuntimeError:
        print("Loop já em execução. Ignorando chamada adicional.")

