# coding: utf-8
"""Modulo para preproceso de un archivo de audio. """
import datetime
import logging
import os
import sys
import time

from pydub import AudioSegment
from pydub.silence import split_on_silence


def main():
    """Unificar en main para poder ejecutar despues desde otro script."""
    inicio = time.time()

    dir_logs = 'logs'
    os.makedirs(dir_logs, exist_ok=True)

    ahora = datetime.datetime.now()
    corrida = "{:%Y-%m-%d-%H%M%S}".format(ahora)
    logfile = os.path.join(dir_logs, '{}.log'.format(corrida))
    log_format = '%(asctime)s : %(levelname)s : %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format,
                        datefmt=log_datefmt,
                        level=logging.INFO,
                        filename=logfile,
                        filemode='w')

    dir_input = sys.argv[1]
    audiofile = os.path.join(dir_input, 'rpef-30-11-2016.mp3')

    soundfile = AudioSegment.from_mp3(audiofile)

    audiochunks = split_on_silence(soundfile,
                                   min_silence_len=500,
                                   silence_thresh=-16)

    for i, chunk in enumerate(audiochunks):
        outfile = os.path.join(dir_input, 'chunk{}.wav'.format(i))
        chunk.export(outfile, format='wav')

    time_end = time.time()
    secs = time_end - inicio
    logging.info('{m:.2f} minutos'.format(m=secs / 60))


if __name__ == '__main__':
    main()
