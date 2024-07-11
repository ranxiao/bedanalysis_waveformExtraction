# Mapping the valid waveform time to the encounter by using the MRN-Mapping.csv file
# input: excel file with a list of encounter IDs
# output: excel file with the valid waveform time for each wave cycle for each encounter
# Logic befind: the valid waveform time is defined as the intersection of the waveform time and the bed transfer time
#               it also handles the case where the waveform end time is missing (assigned with a date in 1969) and set it to the bed transfer out time

# Author: Ran Xiao, Emory University, April, 2024

# import the necessary libraries
import pandas as pd
import paramiko
import os

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

# read the encounter list as input and the encounter date offset table
df_enc = pd.read_excel('sampleEncounterList.xlsx')
df_offset_table = pd.read_excel('encounter_date_offset_table_ver_Apr2024.xlsx')

# establish a connection to the server
transport = paramiko.Transport((host, 22))
transport.connect(username=usr, password=pwd)
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.chdir(dir_waveform)

# find encounters with mapped Wynton_folder
df_mapped = df_offset_table[df_offset_table['Encounter_ID'].isin(df_enc['Encounter_ID'])]

# loop through each row in df_mapped
ValidWaveTime_allEnc = pd.DataFrame()
for i in range(len(df_mapped)):
    # construct dir for MRN-Mapping.csv for each patient
    # e.g., /labs/hulab/UCSF/2013-03-deid/DE104397434432468/MRN-Mapping.csv
    dir_MappingFile = dir_waveform + df_mapped['Wynton_folder'].values[i] + '/DE' + str(df_mapped['Patient_ID_GE'].values[i]) + '/MRN-Mapping.csv'
    # read the MRN-Mapping.csv file on the server
    with sftp.open(dir_MappingFile) as f:
        MRN_Mapping = pd.read_csv(f)

    # convert BedTransfer_In','BedTransfer_Out', 'WaveStartTime' and 'WaveStopTime' to datetime
    # e.g. Wynton_folder    MRN_ADT	            UnitBed	BedTransfer_In	BedTransfer_Out  WaveCycleUID	WaveStartTime	WaveStopTime
    #     2018-08-deid      DE649769843712858	9ICU_6	10/2/17 14:41	10/2/17 23:59		44971	    1/11/17 23:31	2/17/69 0:00
    MRN_Mapping['BedTransfer_In'] = pd.to_datetime(MRN_Mapping['BedTransfer_In'])
    MRN_Mapping['BedTransfer_Out'] = pd.to_datetime(MRN_Mapping['BedTransfer_Out'])
    MRN_Mapping['WaveStartTime'] = pd.to_datetime(MRN_Mapping['WaveStartTime'])
    MRN_Mapping['WaveStopTime'] = pd.to_datetime(MRN_Mapping['WaveStopTime'])

    # for each unique 'WaveCycleUID' in MRN_Mapping, find time range for BedTransfer_In and BedTransfer_Out,
    # and for WaveStartTime and WaveStopTime, here are the logics behind it:
    # 1. get the smallest 'BedTransfer_In' and largest 'BedTransfer_Out',
    # 2. and get the smallest "WaveStartTime" and largest "WaveStopTime"
    MRN_Mapping_WaveCycles = MRN_Mapping.groupby('WaveCycleUID').agg(
        Patient_ID_GE=('MRN_ADT', 'first'),
        UnitBed=('UnitBed', 'first'),
        BedTransfer_In=('BedTransfer_In', 'min'),
        BedTransfer_Out=('BedTransfer_Out', 'max'),
        WaveStartTime=('WaveStartTime', 'min'),
        WaveStopTime=('WaveStopTime', 'max')
    ).reset_index()

    # if WaveStopTime is smaller than WaveStartTime, then set WaveStopTime to BedTransfer_Out
    MRN_Mapping_WaveCycles.loc[MRN_Mapping_WaveCycles['WaveStopTime'] < MRN_Mapping_WaveCycles['WaveStartTime'], 'WaveStopTime'] = MRN_Mapping_WaveCycles['BedTransfer_Out']

    # Logics for getting "ValidStartTime" and "ValidStopTime":
    # "ValidStartTime" is the larger one of "BedTransfer_In" and "WaveStartTime"
    # "ValidStopTime" is the smaller one of "BedTransfer_Out" and "WaveStopTime"
    MRN_Mapping_WaveCycles['ValidStartTime'] = MRN_Mapping_WaveCycles[['BedTransfer_In', 'WaveStartTime']].max(axis=1)
    MRN_Mapping_WaveCycles['ValidStopTime'] = MRN_Mapping_WaveCycles[['BedTransfer_Out', 'WaveStopTime']].min(axis=1)

    # add Wynton_folder to the MRN_Mapping_WaveCycles
    MRN_Mapping_WaveCycles.insert(0, 'Wynton_folder', df_mapped['Wynton_folder'].values[i])

    ValidWaveTime_allEnc = pd.concat([ValidWaveTime_allEnc, MRN_Mapping_WaveCycles], ignore_index=True)
    print(f'Progress: {i+1} out of {len(df_mapped)}')

ValidWaveTime_allEnc.to_excel(dir_output+ 'ValidWaveTime_allEnc.xlsx', index=False)
print('done')



