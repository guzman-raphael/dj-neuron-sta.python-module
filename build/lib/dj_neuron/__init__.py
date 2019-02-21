from . import create
import datajoint as dj, numpy as np
import os, json
from importlib import reload
from .create import Schema,Samples,Subjects,MovieFiles,Movies,Sessions,Stimuli,Neurons,STRFParams,STRFCalcs


def main():
    import time
    start_time = time.time()

    main = '/data'
    # main = '/home/rguzman/Documents/dev/dj-docker/client'

    # createSchemaScratch(main,0.2)     # takes ~9[m]
    # updateSchemaComputationOnly(0.3)  # takes ~7.5[m]
    # convertTaskDataToJSON(main)

    neuros_interest = [
        {'sample_number' : 3,'subject_name' : 'KO (chx10)','session_date' : '2008-06-06','neuron_id' : 0},
        {'sample_number' : 2,'subject_name' : 'KO (chx10)','session_date' : '2008-06-24','neuron_id' : 0},
        {'sample_number' : 1,'subject_name' : 'KO (pax6)','session_date' : '2008-05-16','neuron_id' : 0}
    ]

    saveVisualizations(neuros_interest,[1,3],main)  # takes ~8[s]

    print("-----Final Time: {}[s]-----".format(time.time() - start_time))

def convertTaskDataToJSON(mainDir):
    print('-----{}-----'.format('Export JSON Ref of Shape'))

    data = prepareTaskData(mainDir)

    file_path = '{}/log/taskData.json'.format(mainDir)
    with open(file_path, 'w') as fjson:
        for i in range(len(data)):
            curr_stim = data[i]['stimulations']
            for j in range(len(curr_stim)):
                data[i]['stimulations'][j]['movie'] = [data[i]['stimulations'][j]['movie'].shape]
                curr_neuron = data[i]['stimulations'][j]['spikes']
                for k in range(len(curr_neuron)):
                    data[i]['stimulations'][j]['spikes'][k] = [data[i]['stimulations'][j]['spikes'][k].shape]


        json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)

def prepareTaskData(mainDir):
    import shutil,pickle

    print('-----{}-----'.format('Task Data into Import Data'))

    # load files
    if os.path.isdir(mainDir + '/config/movie-data'): shutil.rmtree(mainDir + '/config/movie-data')
    if os.path.isdir(mainDir + '/config/neuron-data'): shutil.rmtree(mainDir + '/config/neuron-data')
    os.mkdir(mainDir + '/config/movie-data')
    os.mkdir(mainDir + '/config/neuron-data')

    with open(mainDir + '/config/task-details/ret1_data.pkl', 'rb') as f:
        data = pickle.load(f)

    for i in range(len(data)):
        for j in range(len(data[i]['stimulations'])):
            FPS = data[i]['stimulations'][j]['fps']
            XBLOCK = data[i]['stimulations'][j]['x_block_size']
            YBLOCK = data[i]['stimulations'][j]['y_block_size']
            FRAMES = data[i]['stimulations'][j]['n_frames']

            np.save(mainDir + '/config/movie-data/MOVIE_{}_{}_{}_{}'.format(FPS,XBLOCK,YBLOCK,FRAMES) , data[i]['stimulations'][j]['movie'])
            np.save(mainDir + '/config/neuron-data/NEURONS_{}_{}_{}_{}'.format(FPS,XBLOCK,YBLOCK,FRAMES) , data[i]['stimulations'][j]['spikes'])

            print('Saved session: {}, Simulation: {}'.format(i,j))
    return data

def createSchemaScratch(mainDir,delay):

    data = prepareTaskData(mainDir)
    print('-----{}-----'.format('Populate Schema from Scratch (Manual,Import,Compute)'))

    with open('{}/config/instance.json'.format(mainDir)) as f:
        jsonData = json.load(f)

    dj.schema(jsonData['schema']).drop()
    reload(create)

    # start
    data_ins = [
        {'file_name' : mainDir + "/config/movie-data/MOVIE_29.9908_8_8_3854.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9815_1_480_3823.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9815_10_10_4125.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9815_10_10_4241.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9815_640_1_4377.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9815_640_2_3938.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9816_1_480_4331.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9816_5_480_4348.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_59.9816_10_10_4325.npy"},
        {'file_name' : mainDir + "/config/movie-data/MOVIE_60.005_2_480_4156.npy"}
    ]

    MovieFiles().insert(data_ins,skip_duplicates=True)
    Movies.populate()


    for i in range(len(data)):

        data_ins = {
            'sample_number' : data[i]['sample_number']
        }
        Samples().insert1(data_ins,skip_duplicates=True)

        data_ins = {
            'sample_number' : data[i]['sample_number'],
            'subject_name' : data[i]['subject_name']
        }
        Subjects().insert1(data_ins,skip_duplicates=True)

        data_ins = {
            'sample_number' : data[i]['sample_number'],
            'subject_name' : data[i]['subject_name'],
            'session_date' : data[i]['session_date']
        }
        Sessions().insert1(data_ins,skip_duplicates=True)

        for j in range(len(data[i]['stimulations'])):
            FPS = data[i]['stimulations'][j]['fps']
            XBLOCK = data[i]['stimulations'][j]['x_block_size']
            YBLOCK = data[i]['stimulations'][j]['y_block_size']
            FRAMES = data[i]['stimulations'][j]['n_frames']

            data_ins = {
                'sample_number' : data[i]['sample_number'],
                'subject_name' : data[i]['subject_name'],
                'session_date' : data[i]['session_date'],
                'file_name' : mainDir + '/config/movie-data/MOVIE_{}_{}_{}_{}.npy'.format(FPS,XBLOCK,YBLOCK,FRAMES),
                'stimulus_onset' : data[i]['stimulations'][j]['stimulus_onset'],
                'pixel_size' : data[i]['stimulations'][j]['pixel_size']

            }
            Stimuli().insert1(data_ins,skip_duplicates=True)

    Neurons.populate()

    data_ins = {
        'strf_id' : 0,
        'delay' : delay
    }
    STRFParams().insert1(data_ins,skip_duplicates=True)

    STRFCalcs.populate()

def updateSchemaComputationOnly(delay):

    print('-----{}-----'.format('Populate Schema for Compute Only w/ new Delay'))
    STRFParams.delete()
    STRFCalcs().drop()
    reload(create)

    data_ins = {
        'strf_id' : 0,
        'delay' : delay
    }
    STRFParams().insert1(data_ins,skip_duplicates=True)

    STRFCalcs.populate()

def addComputationComparison(delay):

    print('-----{}-----'.format('Add Computation for Delay Param Comparison'))

    data_ins = {
        'strf_id' : len(STRFParams()),
        'delay' : delay
    }
    STRFParams().insert1(data_ins,skip_duplicates=True)

    STRFCalcs.populate()

def saveVisualizations(neu_arr,shp,mainDir):
    from matplotlib import pyplot as plt

    print('-----{}-----'.format('Saving Visualizations'))

    savePath = mainDir + '/log'

    # Table output
    print(MovieFiles())
    print(Movies())
    print(STRFParams())
    print(Samples())
    print(Subjects())
    print(Sessions())
    print(Stimuli())
    print(Neurons())
    print(STRFCalcs())

    # # View mov shape before mean
    # test = STRFCalcs().fetch('mov_shape')
    # test = test.reshape((len(test),1))
    # print(test)

    # Entity Relationship Diagram
    # dj.ERD(Schema).draw()
    plt.imsave('{}/ERD.png'.format(savePath), dj.ERD(Schema).make_image())

    # plot STA's
    delay = STRFParams.fetch1('delay')
    final = STRFCalcs & neu_arr
    final = final.fetch('sta')
    # print(final.shape)
    fig=plt.figure(figsize=(8, 8))
    columns = shp[1]
    rows = shp[0]
    for i in range(1, len(final) +1):
        fig.add_subplot(rows, columns, i)
        plt.title('STA id: {}, Delay: {}'.format(i,delay))
        plt.imshow(final[i-1], cmap='gray', interpolation='nearest')
    plt.savefig('{}/STA.png'.format(savePath))

    # plot spikes scatter
    final = Neurons & neu_arr
    final = final.fetch()
    # print(final.shape)
    w = 4*4.5
    h = 3*4.5
    d = 70
    plt.figure(figsize=(w, h), dpi=d)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.65, box.height])
    for i in range(len(final)):
        ax.scatter(final[i]['spikes'], np.zeros_like(final[i]['spikes']) + -i, s=10, marker=".", label="SmpNo: {}, SubName: {}, Session: {}, Neu_id: {}, Spike Count: {}".format(final[i]['sample_number'],final[i]['subject_name'],final[i]['session_date'],final[i]['neuron_id'],len(final[i]['spikes'])))

    plt.title("Spike Detection Output")
    plt.xlabel("Spike Times[s]")

    legend_x = 1
    legend_y = 0.5
    plt.legend(loc='center left', bbox_to_anchor=(legend_x, legend_y))
    plt.savefig('{}/Spikes.png'.format(savePath))


    # Sample Image
    path = mainDir + '/config/movie-data'
    data = (Movies & 'file_name = "{}/MOVIE_59.9815_10_10_4125.npy"'.format(path)).fetch1('movie')
    # print(data.shape)
    fig=plt.figure(figsize=(8, 8))
    columns = shp[1]
    rows = shp[0]
    for i in range(1, columns*rows +1):
        fig.add_subplot(rows, columns, i)
        plt.imshow(data[:,:,i-1], cmap='gray', interpolation='nearest')
    plt.savefig('{}/SampleImages.png'.format(savePath))

    # Show All
    # plt.show()
