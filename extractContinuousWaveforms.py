# Extract waveforms from ADIBIN files for patient encounters with the validated waveform time (start and end time)
# Author: Ran Xiao, Emory University, April 2024
import os
import numpy as np
import pandas as pd
import paramiko
from binfilepy import BinFile
import stat
import posixpath

# connection string to the database from the config file
config = {}
with open('config.txt', 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        config[key] = value
usr = config['usr']
pwd = config['pwd']
host = config['host']
dir_waveform = config['dir_waveform']
dir_output = config['dir_output']
# create a directory for the output if it does not exist
if not os.path.exists(dir_output):
    os.makedirs(dir_output)

# load validated waveform time
ValidWaveTime_allEnc = pd.read_excel(dir_output+'ValidWaveTime_allEnc.xlsx')

# establish a connection to the server
transport = paramiko.Transport((host, 22))
transport.connect(username=usr, password=pwd)
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.chdir(dir_waveform)

# create a dataframe to store the meta data for whether the adibin file exists for each row in ValidWaveTime_allEnc
meta_data_Enc = ValidWaveTime_allEnc
meta_data_Enc['exist_adibin'] = 0
meta_data_Enc['total_dur_seconds'] = 0

# for each row in ValidWaveTime_allEnc, extract the waveform data
for i in range(5):#len(ValidWaveTime_allEnc)):
    # construct dir for each patient encounter which can have multiple wavecycles in each subdirectory and each wavecycle has multiple adibin files
    # e.g., /labs/hulab/UCSF/2013-08-deid/DE106215743039212/9ICU_13-DE106215743039212/DE106215743039212_20130512191301_6413.adibin
    dir_binFiles = dir_waveform + ValidWaveTime_allEnc['Wynton_folder'].values[i] + '/' + ValidWaveTime_allEnc['Patient_ID_GE'].values[i] + '/'
    # list all files in only the subdirectories
    def list_files_in_subdirectories(sftp, dir_path, is_subdirectory=False):
        files = []
        for item in sftp.listdir_attr(dir_path):
            # Use posixpath.join to ensure Unix-style paths
            item_path = posixpath.join(dir_path, item.filename)

            if stat.S_ISDIR(item.st_mode):  # Check if it is a directory
                files.extend(list_files_in_subdirectories(sftp, item_path, True))
            elif is_subdirectory:  # Add files only if it's from a subdirectory
                files.append(item_path)
        return files
    all_files = list_files_in_subdirectories(sftp, dir_binFiles)
    # Filtering for files ending with one wavecyle plus .adibin
    adibin_files = [file for file in all_files if file.endswith(str(ValidWaveTime_allEnc['WaveCycleUID'].values[i])+'.adibin')]
    # if there is no adibin file in the directory, skip to the next row
    if len(adibin_files) == 0:
        continue
    else:
        meta_data_Enc['exist_adibin'].values[i] = 1

    # sort by the file name
    adibin_files.sort()

    ValidStartTime = ValidWaveTime_allEnc['ValidStartTime'].values[i]
    ValidStopTime = ValidWaveTime_allEnc['ValidStopTime'].values[i]

    # create a folder in the output directory for row combining Wynton_doler, Patient_ID_GE and WaveCycleUID
    folder_name = ValidWaveTime_allEnc['Wynton_folder'].values[i] + '_' + ValidWaveTime_allEnc['Patient_ID_GE'].values[i] + '_' + str(ValidWaveTime_allEnc['WaveCycleUID'].values[i])
    dir_output_extractedWaveform = dir_output+folder_name+'/'
    if not os.path.exists(dir_output_extractedWaveform):
        os.makedirs(dir_output_extractedWaveform)

    # create an empty dataframe to store the meta data for each adibin file with row number of len(adibin_files)
    meta_data_adibin = pd.DataFrame(index=range(len(adibin_files)), columns=['file_ind','exist_valid_waveform', 'OutputFile_dir','channel_name', 'Binfile_ValidStartTime', 'Binfile_ValidEndTime', 'Binfile_duration_seconds', 'file_start_time', 'file_end_time', 'file_duration_seconds', 'Wavecycle_ValidStartTime', 'Wavecycle_ValidStopTime','Binfile_dir'])
    for j in range(len(adibin_files)):
        # download the file to a temporary directory
        sftp.get(adibin_files[j], 'temp.adibin')
        # for each adibin file, extract the waveform data with valid start and end time, adding time vector, and save it to a pickle file
        with BinFile('temp.adibin', "r") as f:
            # You must read header first before you can read channel data
            f.readHeader()
            # get channel names in each element of the list f.channels
            channel_name = []
            for c in f.channels:
                channel_name.append(c.Title)
            # if there is no channel name, use 'Unnamed_Channel_1', 'Unnamed_Channel_2', etc. There can be multiple unnamed channels
            channel_name = [name if name else f'Unnamed_Channel_{c + 1}' for c, name in enumerate(channel_name) if
                            name == '' or c == channel_name.index(name)]

            # calculate the sampling frequency
            fs = 1/ f.header.secsPerTick
            # get the starting and end time for the waveform file
            file_start_time = np.datetime64(
                f"{f.header.Year}-{f.header.Month:02}-{f.header.Day:02}T{f.header.Hour:02}:{f.header.Minute:02}:{f.header.Second:09.6f}")
            file_duration_seconds = f.header.SamplesPerChannel * f.header.secsPerTick
            file_end_time = file_start_time + np.timedelta64(int(file_duration_seconds * 1e6), 'us')

            meta_data_adibin['file_ind'].values[j] = j
            meta_data_adibin['channel_name'].values[j] = channel_name
            meta_data_adibin['file_start_time'].values[j] = file_start_time
            meta_data_adibin['file_end_time'].values[j] = file_end_time
            meta_data_adibin['file_duration_seconds'].values[j] = file_duration_seconds
            meta_data_adibin['Wavecycle_ValidStartTime'].values[j] = ValidStartTime
            meta_data_adibin['Wavecycle_ValidStopTime'].values[j] = ValidStopTime
            meta_data_adibin['Binfile_dir'].values[j] = adibin_files[j]

            if file_end_time < ValidStartTime or file_start_time > ValidStopTime:
                meta_data_adibin['exist_valid_waveform'].values[j] = 0
                meta_data_adibin['Binfile_duration_seconds'].values[j] = 0
                continue
            else:
                Binfile_ValidStartTime = max(file_start_time, ValidStartTime)
                Binfile_ValidEndTime = min(file_end_time, ValidStopTime)
                meta_data_adibin['exist_valid_waveform'].values[j] = 1
                meta_data_adibin['Binfile_ValidStartTime'].values[j] = Binfile_ValidStartTime
                meta_data_adibin['Binfile_ValidEndTime'].values[j] = Binfile_ValidEndTime
                Binfile_duration_seconds = ((Binfile_ValidEndTime - Binfile_ValidStartTime) / np.timedelta64(1, 's')).astype(float)
                meta_data_adibin['Binfile_duration_seconds'].values[j] = Binfile_duration_seconds

            # generate a time vector for the waveform data
            time_vector = np.arange(0, Binfile_duration_seconds, 1/fs)
            time_vector = Binfile_ValidStartTime + time_vector.astype('timedelta64[ms]')

            # readChannelData() supports reading in random location (Note: offset=0, length=0 indicate read the whole file)
            wave_data = f.readChannelData(offset=(Binfile_ValidStartTime-file_start_time).astype('timedelta64[s]').astype(float), length=meta_data_adibin['Binfile_duration_seconds'].values[j], useSecForOffset=True, useSecForLength=True)

            # combine the time vector and the waveform data with channel names
            dtype = [('time', 'datetime64[ms]')]  # start with the time column
            dtype += [(name, 'float64') for name in channel_name]  # add each ECG channel
            combined_data = np.empty(len(time_vector), dtype=dtype)
            # Fill the time column
            combined_data['time'] = time_vector
            # Fill each ECG channel
            for k, name in enumerate(channel_name):
                combined_data[name] = wave_data[k]
            combined_data = pd.DataFrame(combined_data)

            meta_data_adibin['OutputFile_dir'].values[j] = dir_output_extractedWaveform + str(j) + '.pkl'

            # save combined_data
            combined_data.to_pickle(meta_data_adibin['OutputFile_dir'].values[j])
            # combined_data.to_hdf(dir_output_extractedWaveform + '/' + adibin_files[j] + '.h5', key='df', mode='w')
            # np.save(dir_output_extractedWaveform + '/' + adibin_files[j] + '.npy', combined_data)

        # remove the temporary file
        os.remove('temp.adibin')
        # save meta_data_adibin to an excel file
        meta_data_adibin.to_excel(dir_output_extractedWaveform + 'meta_data_adibin.xlsx')

        # print progress
        print(f'Progress: {i+1} out of {len(ValidWaveTime_allEnc)} encounters, {j+1} out of {len(adibin_files)} adibin files')
    meta_data_Enc['total_dur_seconds'].values[i] = meta_data_adibin['Binfile_duration_seconds'].sum()
    # save meta_data_Enc to an excel file
    meta_data_Enc.to_excel(dir_output + 'meta_data_Enc.xlsx')