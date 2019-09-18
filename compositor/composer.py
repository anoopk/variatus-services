from pydub import AudioSegment

sound1 = AudioSegment.from_file("C:\\Users\\admin\\Desktop\\Transitional\\Kinder\\kinder variations\\bass and piano.wav")
sound2 = AudioSegment.from_file("C:\\Users\\admin\\Desktop\\Transitional\\Kinder\\kinder variations\\bass and piano.wav")

combined = sound1.overlay(sound2)

combined.export(""C:\\Users\\admin\\Desktop\\Transitional\\Kinder\\kinder variations\\bass and piano.wav"", format='wav')