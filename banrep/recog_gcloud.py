# coding: utf-8
"""Modulo para transcribir archivo de audio usando Google Cloud Speech. """
import datetime
import io
import json
import logging
import os
import sys
import time

from google.cloud import speech
import speech_recognition as sr


def transcribe_file(speech_file):
    """Transcribe the given audio file asynchronously."""
    speech_client = speech.Client()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
        audio_sample = speech_client.sample(
            content, encoding='LINEAR16', sample_rate=16000)

    operation = audio_sample.async_recognize('es-CO',)

    retry_count = 100
    while retry_count > 0 and not operation.complete:
        retry_count -= 1
        time.sleep(2)
        operation.poll()

    if not operation.complete:
        print('Operation not complete and retry limit reached.')
        return

    alternatives = operation.results
    for alternative in alternatives:
        print('Transcript: {}'.format(alternative.transcript))
        print('Confidence: {}'.format(alternative.confidence))

    return alternatives


def audio_transcribe(audio_file, credentials):
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    try:
        transcript = r.recognize_google_cloud(audio,
                                              credentials_json=credentials)
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
        transcript = ''
    except sr.RequestError as e:
        print("Could not request results from Google; {}".format(e))
        transcript = ''

    return transcript


def main():
    """Unificar en main para poder ejecutar despues desde otro script."""
    inicio = time.time()
    dir_input = sys.argv[1]
    credfile = sys.argv[2]

    dir_logs = 'logs'
    os.makedirs(dir_logs, exist_ok=True)

    ahora = datetime.datetime.now()
    corrida = "{:%Y-%m-%d-%H%M%S}-gcloud".format(ahora)
    logfile = os.path.join(dir_logs, '{}.log'.format(corrida))
    log_format = '%(asctime)s : %(levelname)s : %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format,
                        datefmt=log_datefmt,
                        level=logging.INFO,
                        filename=logfile,
                        filemode='w')

    audiofile = os.path.join(dir_input, 'corto.flac')

    # with open('gcloud_result.json', 'w', encoding='utf-8') as fp:
    #     results = transcribe_file(audiofile)
    #
    #     json.dump(results, fp, indent=2, ensure_ascii=False)

    with open(credfile) as cf:
        credentials = json.load(cf)
        credentials = json.dumps(credentials, ensure_ascii=False)

    transcript = audio_transcribe(audiofile, credentials)
    print(transcript)

    time_end = time.time()
    secs = time_end - inicio
    logging.info('{m:.2f} minutos'.format(m=secs / 60))


if __name__ == '__main__':
    main()
