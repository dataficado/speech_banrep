# coding: utf-8
"""Modulo para preproceso de un archivo de audio. """
import datetime
import logging
import os
import sys
import time

from pydub import AudioSegment
from pydub.silence import split_on_silence


def split_audiofile(audiofile):
    """Separa audio de audiofile en archivos"""
    inputdir = os.path.dirname(audiofile)
    subdir = os.path.basename(audiofile).rsplit('.', maxsplit=1)[0]
    outdir = os.path.join(inputdir, 'chunked_audio', subdir)
    os.makedirs(outdir, exist_ok=True)

    soundfile = AudioSegment.from_mp3(audiofile)
    audiochunks = split_on_silence(soundfile,
                                   min_silence_len=1000,
                                   silence_thresh=-16)

    for i, chunk in enumerate(audiochunks):
        outfile = os.path.join(outdir, 'chunk{:0>3}.wav'.format(i))
        chunk.export(outfile, format='wav')


def main():
    """Unificar en main para poder ejecutar despues desde otro script."""
    inicio = time.time()

    dir_logs = 'logs'
    os.makedirs(dir_logs, exist_ok=True)

    ahora = datetime.datetime.now()
    corrida = "{:%Y-%m-%d-%H%M%S}-preprocess".format(ahora)
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

    split_audiofile(audiofile=audiofile)

    time_end = time.time()
    secs = time_end - inicio
    logging.info('{m:.2f} minutos'.format(m=secs / 60))


if __name__ == '__main__':
    main()
