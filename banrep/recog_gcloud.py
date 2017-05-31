# coding: utf-8
"""Modulo para transcribir archivo de audio usando Google Cloud Speech. """
import base64
import datetime
import json
import logging
import os
import sys
import time

from google.cloud import speech


def encode_audio(audiofile):
    """Codifica contenido de audiofile"""
    with open(audiofile, 'rb') as af:
        speech_content = base64.b64encode(af.read())

    return speech_content


def transcribe_gcs(urifile):
    """Transcribe gcs audio file asynchronously."""
    speech_client = speech.Client()

    audio_sample = speech_client.sample(
        source_uri=urifile,
        encoding='LINEAR16',
        sample_rate=16000)

    operation = audio_sample.async_recognize('es-CO')

    logging.info('Analizando: {}'.format(urifile))

    while not operation.complete:
        time.sleep(2)

        try:
            operation.poll()

        except ValueError:
            logging.info('No hay contenido en {}'.format(urifile))
            return
        except Exception as e:
            logging.info('Error inesperado en {}: {}'.format(urifile, e))
            return

    return operation


def main():
    """Unificar en main para poder ejecutar despues desde otro script."""
    inicio = time.time()
    dir_input = sys.argv[1]
    dir_output = 'transcriptions'
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

    dirstub = os.path.split(dir_input)[-1]
    bucket = 'gs://audio-banrep/{}'.format(dirstub)

    for filename in os.listdir(dir_input):
        if filename.endswith('.wav'):
            urifile = '{}/{}'.format(bucket, filename)
            filestub = filename.rsplit('.', maxsplit=1)[0]
            outpath = os.path.join(dir_output, dirstub)

            os.makedirs(outpath, exist_ok=True)

            outfile = os.path.join(outpath, '{}.json'.format(filestub))

            with open(outfile, 'w', encoding='utf-8') as fp:
                results = []

                operation = transcribe_gcs(urifile=urifile)

                if operation:
                    for alternative in operation.results:
                        transcript = alternative.transcript
                        confidence = alternative.confidence

                        results.append({'transcript': transcript,
                                        'confidence': confidence})

                    json.dump({'results': results}, fp, indent=2,
                              ensure_ascii=False)

    time_end = time.time()
    secs = time_end - inicio
    logging.info('{m:.2f} minutos'.format(m=secs / 60))


if __name__ == '__main__':
    main()
