# coding: utf-8
"""Modulo para speech-2-text a un archivo de audio usando IBM Watson. """
from mimetypes import MimeTypes
import datetime
import json
import logging
import os
import sys
import time

from watson_developer_cloud import SpeechToTextV1


def guess_mime_type(audio_path, forced_mime=None):
    mime = MimeTypes()
    mime_type = forced_mime or mime.guess_type(audio_path)[0]
    logstr = 'MimeType de archivo {}: {}'.format(audio_path, mime_type)
    logging.info(logstr)

    return mime_type


def chunked_upload(audio_path, buffer_size):
    total_size = os.path.getsize(audio_path)
    progress = 0

    with open(audio_path, 'rb') as audio_file:
        while True:
            data = audio_file.read(buffer_size)
            progress += len(data or [])
            logstr = 'Leidos {} bytes de {}'.format(progress, total_size)
            logging.info(logstr)

            if not data:
                break
            yield data


def recognize_speech(username, password, audio_path,
                     buffer_size=4096, **kwargs):
    stt = SpeechToTextV1(username=username, password=password)

    return stt.recognize(
        chunked_upload(audio_path, buffer_size), **kwargs)


def main():
    """Unificar en main para poder ejecutar despues desde otro script."""
    inicio = time.time()

    dir_logs = 'logs'
    os.makedirs(dir_logs, exist_ok=True)

    ahora = datetime.datetime.now()
    corrida = "{:%Y-%m-%d-%H%M%S}-watson".format(ahora)
    logfile = os.path.join(dir_logs, '{}.log'.format(corrida))
    log_format = '%(asctime)s : %(levelname)s : %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format,
                        datefmt=log_datefmt,
                        level=logging.INFO,
                        filename=logfile,
                        filemode='w')

    dir_input = sys.argv[1]
    credfile = sys.argv[2]
    credkey = sys.argv[3]

    with open(credfile) as cf:
        credential = json.load(cf).get(credkey)

    username = credential.get('username')
    password = credential.get('password')

    audiofile = os.path.join(dir_input, 'prueba.flac')

    specifics = {
        'content_type': guess_mime_type(audiofile, 'audio/x-flac'),
        'timestamps': True,
        'speaker_labels': True,
        'max_alternatives': 1,
        'model': 'es-ES_BroadbandModel'
    }

    with open('transcript_result.json', 'w', encoding='utf-8') as fp:
        result = recognize_speech(username=username, password=password,
                                  audio_path=audiofile, **specifics)

        json.dump(result, fp, indent=2, ensure_ascii=False)

    time_end = time.time()
    secs = time_end - inicio
    logging.info('{m:.2f} minutos'.format(m=secs / 60))


if __name__ == '__main__':
    main()
