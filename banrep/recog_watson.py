# coding: utf-8
"""Modulo para extraer texto de archivos binarios."""
import csv
import datetime
import json
import logging
import os
import sys
import time
import warnings

from watson_developer_cloud import SpeechToTextV1



def main():
    """Unificar en main para poder ejecutar despues desde otro script."""
    inicio = time.time()
    corrida = "{:%Y-%m-%d-%H%M%S}".format(datetime.datetime.now())

    dir_input = sys.argv[1]
    credfile = sys.argv[2]
    credkey = sys.argv[3]

    with open(credfile) as cf:
        credential = json.load(cf).get(credkey)

    username = credential.get('username')
    password = credential.get('password')

    stt = SpeechToTextV1(username=username, password=password)

    audiofile = os.path.join(dir_input, 'prueba.flac')

    with open(audiofile, 'rb') as af:
        result = stt.recognize(af, content_type="audio/x-flac",
                               timestamps=True, max_alternatives=1,
                               model='es-ES_BroadbandModel')

    with open('transcript_result.json', 'w', encoding='utf-8') as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
