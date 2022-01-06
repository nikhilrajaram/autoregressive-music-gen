from MidiTokenizer import MidiTokenizer
from MidiGenerator import MidiGenerator
import midi

if __name__ == '__main__':
    mid = MidiTokenizer.load_midi('../data/AllFallsDown.mid')
    gen = MidiGenerator(mid.event_data.values)

    print(gen.train())
    df = pd.DataFrame(gen.babl(10000), columns=['channel', 'start', 'duration', 'pitch', 'velocity'])
    df.to_csv('../data/BigPoppaBabl.csv')

    # mid_deserialized = MidiTokenizer.deserialize(mid.event_data)
    # midi.write_midifile("../data/BigPoppaDeserialized.mid", mid_deserialized)
    print(gen)
