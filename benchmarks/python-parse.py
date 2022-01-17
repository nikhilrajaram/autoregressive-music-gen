import glob
import numpy as np
import midi
import mido
from music21 import converter
import sys
import time


def timeit(f, args):
    times = []
    for arg in args:
        st = time.time()*1000
        if type(arg) == str:
            with open(arg, 'r') as file:
                f(file)
        times.append(time.time()*1000-st)
    return times


if __name__ == '__main__':
    n = int(sys.argv[1])
    files = np.random.choice(glob.glob('../data/lmd_full/**/*.mid'), n)
    print(f'[vishnubob] mean read+parse time (n={n}): {np.mean(timeit(midi.read_midifile, files))}')
    print(f'[music21] mean read+parse time (n={n}): {np.mean(timeit(converter.parse, files))}')
    print(f'[mido] mean read+parse time (n={n}): {np.mean(timeit(mido.MidiFile, files))}')
