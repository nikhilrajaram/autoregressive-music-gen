import midi
import numpy as np
import pandas as pd


def insert_events(tracks, event):
    if event['velocity'] != 0:
        tracks[event['channel']].append(
            midi.NoteOnEvent(tick=int(event['tick']), velocity=int(event['velocity']), pitch=int(event['pitch']))
        )
    else:
        tracks[event['channel']].append(
            midi.NoteOnEvent(tick=int(event['tick']), velocity=0, pitch=int(event['pitch']))
        )


class MidiTokenizer:
    DEFAULT_BPM = 120

    def __init__(self, event_data=None, mid=None):
        if event_data is not None:
            self.event_data = event_data
            if len(set(self.event_data['channel'])) == 1:
                self.format = 0
            else:
                self.format = 1

            self.tick_relative = False
            if mid is not None:
                self.mid = mid
            else:
                self.mid = self.deserialize(self.event_data)

            return

        if mid is not None:
            self.mid = mid
            if type(mid) == midi.Track:
                self.format = 0
            else:
                self.format = 1

            self.tick_relative = False

            if event_data is not None:
                self.event_data = event_data
            else:
                self.event_data = self.serialize(mid, self.tick_relative)

            return

    @classmethod
    def load_midi(cls, file_path):
        mid = midi.read_midifile(file_path)
        mid_format = mid.format
        tick_relative = mid.tick_relative
        event_data = []

        if mid_format == 0:
            event_data = cls.serialize([mid], tick_relative)
        elif mid_format == 1:
            event_data = cls.serialize(mid, tick_relative)

        return cls(event_data, mid)

    @classmethod
    def serialize(cls, tracks, tick_relative=True):
        pitch_data, data, event_data = {}, {i: [] for i in range(17)}, []

        if type(tracks) == list:
            tracks = tracks[0]

        for i, track in enumerate(tracks):
            tick = 0

            for event in track:
                if type(event) == midi.SetTempoEvent:
                    bpm = event.get_bpm()

                if type(event) != midi.NoteOnEvent and type(event) != midi.NoteOffEvent:
                    continue

                tick = (tick + event.tick) if tick_relative else event.tick

                if event.velocity != 0 and type(event) != midi.NoteOffEvent:
                    datum = [tick, None, event.pitch, event.velocity]
                    data[event.channel].append(datum)
                    try:
                        if pitch_data[event.pitch][-1][1] is None:
                            pitch_data[event.pitch][-1][1] = tick

                        pitch_data[event.pitch].append(datum)
                    except KeyError:
                        pitch_data[event.pitch] = [datum]
                else:
                    pitch_data[event.pitch][-1][1] = tick - data[event.channel][-1][0]

        for channel, events in data.items():
            event_data.extend([[channel] + event for event in events])

        event_data = pd.DataFrame(
            event_data, columns=['channel', 'start', 'duration', 'pitch', 'velocity'], dtype=int
        ).sort_values(by=['start'])

        return event_data

    @classmethod
    def deserialize(cls, event_data):
        assert type(event_data) == pd.DataFrame, "event_data must be of type pd.DataFrame"
        assert event_data.applymap(lambda x: type(x) in [int, np.int64, np.int32]).all().all(), 'event data is invalid'

        event_data = event_data.applymap(lambda x: int(x))

        pattern = midi.Pattern()
        tracks = {i: midi.Track() for i in range(17)}

        event_data_rel = pd.DataFrame(dtype=np.int64)
        event_data_rel[['channel', 'tick', 'pitch', 'velocity']] = \
            event_data[['channel', 'start', 'pitch', 'velocity']].astype(np.int64)

        off_events = pd.DataFrame(dtype=np.int64)
        off_events[['channel', 'pitch']] = event_data[['channel', 'pitch']]
        off_events['tick'] = event_data['start'] + event_data['duration']
        off_events['velocity'] = 0
        event_data_rel = event_data_rel.append(off_events)

        event_data_rel = event_data_rel.sort_values(['tick'])

        for i in tracks.keys():
            track_event_data = event_data_rel.loc[event_data_rel['channel'] == i]
            track_event_data['tick'].iloc[1:] = track_event_data['tick'].values[1:] - track_event_data['tick'].values[:-1]
            track_event_data.apply(lambda x: insert_events(tracks, x), axis=1)

        for i, track in tracks.items():
            if len(track) > 0:
                max_ticks_data = event_data.loc[
                    event_data['start'] == event_data.loc[
                        event_data['channel'] == i
                    ]['start'].max()
                ]

                max_start_tick = max_ticks_data['start'].head(1).values[0]
                max_tick = int(max_start_tick + max_ticks_data['duration'].max())

                track.append(midi.EndOfTrackEvent(tick=max_tick + 1))
                pattern.append(track)

        return pattern
