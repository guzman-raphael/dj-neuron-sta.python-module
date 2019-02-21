
import datajoint as dj
import numpy as np
import os, json

dir_path = os.path.dirname(os.path.realpath(__file__))
with open('/data/config/instance.json'.format(dir_path)) as f:
    jsonData = json.load(f)

dj.config['database.host'] = jsonData['host']
dj.config['database.user'] = jsonData['username']
dj.config['database.password'] = jsonData['password']
dj.config['safemode'] = False
# dj.set_password(new_password="newTomorrow", update_config=True)
# dj.config.save_local()

Schema = dj.schema(jsonData['schema'])

@Schema
class Samples(dj.Manual):
    definition = """
    # Sample Pool
    sample_number : int                 # unique id for mouse
    ---
    """

@Schema
class Subjects(dj.Manual):
    definition = """
    # Subject Pool
    -> Samples                          # relation to Sample
    subject_name : varchar(40)          # unique name for retina subject
    ---
    """

@Schema
class MovieFiles(dj.Manual):
    definition = """
    # MovieFile Pool
    file_name : varchar(100)            # unique id for MovieFile
    ---
    """

@Schema
class Movies(dj.Imported):
    definition = """
    # Movie Pool
    -> MovieFiles
    ---
    fps : double                        # freq, frames per second
    movie : longblob                    # movie blob
    n_frames : int                      # number of frames
    stim_width : int                    # total width
    stim_height : int                   # total height
    x_block_size : int                  # each horizontal block width
    y_block_size : int                  # each vertical block height
    """

    def make(self, key):
        data = np.load(key['file_name'])
        # print(str(data.shape))
        props = key['file_name'].split('/')[-1].split('.npy')[0].split('_')

        key['fps'] = props[1]
        key['movie'] = data
        key['n_frames'] = data.shape[2]
        key['stim_width'] = data.shape[0]*int(props[2])
        key['stim_height'] = data.shape[1]*int(props[3])
        key['x_block_size'] = props[2]
        key['y_block_size'] = props[3]

        self.insert1(key)
        print('Movie added. FileName: {}'.format(key['file_name']))

@Schema
class Sessions(dj.Manual):
    definition = """
    # Session Pool
    -> Subjects                         # relation to Subject
    session_date : date                 # session date
    ---
    """

@Schema
class Stimuli(dj.Manual):
    definition = """
    # Stimulus Pool
    -> Sessions                         # relation to Session
    -> Movies                           # relation to Movies
    ---
    stimulus_onset : double             # delay until stimulus
    pixel_size : double                 # pixel size on the retina
    """

@Schema
class Neurons(dj.Imported):
    definition = """
    # Neuron Pool
    -> Stimuli                          # relation to Stimulus
    neuron_id : int                     # unique id for neuron
    ---
    spikes : longblob                   # spike detection for neuron data
    """

    def make(self, key):
        dir = os.path.dirname(key['file_name'])
        props = key['file_name'].split('/')[-1].split('.npy')[0].split('_')
        file = dir + '/../neuron-data/' + 'NEURONS_{}_{}_{}_{}.npy'.format(props[1],props[2],props[3],props[4])

        data = np.load(file)
        for i,d in enumerate(data):
            key['neuron_id'] = i
            key['spikes'] = d
            self.insert1(key)
        # key['neuron_id'] = 0
        # key['spikes'] = data[0]
        # self.insert1(key)

        print('Neuron added. FileName: {}, Neuron: {}'.format(key['file_name'],key['neuron_id']))

@Schema
class STRFParams(dj.Lookup):
    definition = """
    # Parameters for STRF Computation
    strf_id : int                       # unique id for strf params
    ---
    delay : float                       # configurable delay
    """

@Schema
class STRFCalcs(dj.Computed):
    definition = """
    # STRFCalc Pool
    -> Neurons                          # relation to Neuron
    -> STRFParams                       # relation to STRFParam
    ---
    sta : longblob                      # calculated result of STRF
    mov_shape : varchar(30)                      # calculated result of STRF
    """

    def make(self, key):
        delay = (STRFParams() & key).fetch1('delay')

        mov = (Movies() & key).fetch1('movie')
        neu = (Neurons() & key).fetch1('spikes')
        fps = (Movies() & key).fetch1('fps')
        frm = mov.shape[2]
        onset = (Stimuli() & key).fetch1('stimulus_onset')

        # remove onset and delay from spikes
        neu = neu - onset - delay

        # convert from duration to frame index
        neu = neu * fps

        # identify appropriate index value and convert
        neu = np.round(neu,0)
        neu = neu.astype(int)

        # reduce to only in bound of frames
        idx = ( neu >= 0 )*( neu <= frm-1 )
        neu = neu[idx]

        # extract stimulus STA slices
        mov = mov[:,:,neu]

        # calc average across z dimension
        key['mov_shape'] = str(mov.shape)
        mov = mov.mean(2)

        key['sta'] = mov
        self.insert1(key)

        mov_file = (Movies() & key).fetch1('file_name')
        smp = (Samples() & key).fetch1('sample_number')
        sub = (Subjects() & key).fetch1('subject_name')
        ses = (Sessions() & key).fetch1('session_date')

        print('STA added. MovieFileName: {}, Sample: {}, Subject: {}, SessionDate: {}'.format(mov_file,smp,sub,ses))
