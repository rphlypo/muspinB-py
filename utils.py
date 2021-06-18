import os
import random
import math
import csv
import yaml
import re

import numpy as np

from pathlib import Path
from scipy.stats import lognorm
from psychopy import core
from psychopy.data import TrialHandler

def getModalities(expInfo):
    return ",".join([s for s in expInfo['metaData']['modalities']])


def get_sessionid(subject):
    return subject['study'] + subject['subject_id'] + '_' + '{:1d}'.format(subject['session'])


def register_subject(datapath=None, modalities=None):
    """ register a subject in the database

    if the subject is already registered, then increment the counter of the session number
    if not register the subject in its first session
    """
    def generate_id():
        return '{:05d}'.format(random.randint(0, 99999))

    # make the directory if not yet available, else use the existing directory
    datapath = Path(datapath).resolve()
    try:
        datapath.mkdir(parents=True)
        print('{} succesfully created!'.format(datapath))
    except FileExistsError:
        print('Using existing directory {}'.format(datapath))

    # probe for type of study in this session
    while True:
        study = input('Is your subject participating in a [P]ilot or in the main [[S]]tudy? ').upper()
        if study in {'P', 'S', ''}:
            study = 'S' if study=='' else study
            break
        else:
            print('Invalid answer, please specify P or S')

    participant_list = Path(datapath, 'participants.tsv')
    # create a participant list at the root of the data directory if it does not yet exist
    # else get the already registered subjects and their sessions
    # - a [P]ilot study corresponds to a session number of 0
    # - an inclusion in the main [S]tudy corresponds to a session number > 0
    if not participant_list.exists():
        print("Creating the file 'participants.tsv' in your data directory")
        with open(participant_list, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, delimiter='\t', fieldnames=['subject_id', 'study', 'session', 'modalities'])  # tab seperated file
            writer.writeheader()
            session = 1 if study=='S' else 0
            sid = generate_id()
    else:
        participants = []  # get the already registered patients
        with open(participant_list, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                participants.append(row)
        
        while True:
            registered_participants = set([p['subject_id'] for p in participants])
            if registered_participants:
                print(registered_participants)
                sid = input('give the subject id if the subject is already in the list of participants, if not press [ENTER]: ')
            if sid in registered_participants:
                session = max([int(p['session']) for p in participants if p['subject_id']==sid]) + 1
                if study == 'P':
                    main_study = input('It is not allowed to do more than one pilot session on the same subject, converting to main [[S]]tudy or [Q]uit!').upper()
                    if main_study in {'S', ''}:
                        study = 'S'  # not allowed to do twice a pilot on the same person
                    else:
                        core.quit()
                break
            elif sid == '':
                sid = generate_id()
                session = 1 if study=='S' else 0
                while sid in participants:  # must be a unique id
                    sid = generate_id()
                break

    # create a session dictionary with the unique id, study type, session number, and modalities used   
    subject = dict(subject_id=sid, study=study, session=session, modalities=','.join(modalities))

    # write the data of the newly created session in the participants.tsv file
    with open(participant_list, 'a+', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=['subject_id', 'study', 'session', 'modalities'])
        writer.writerow(subject) 
    
    # create some extra folders
    subject_path = Path(datapath, get_sessionid(subject)[:-2]).resolve()
    try:
        subject_path.mkdir()
    except FileExistsError:
        pass

    for m in subject['modalities'].split(','):
        try:
            Path(subject_path, m.upper()).mkdir()
        except FileExistsError:
            pass
               
    return get_sessionid(subject), subject_path


def load_init(f):
    if f is None:
        f = __get_init_file( Path.cwd())
    elif Path(f).is_dir():
        f = __get_init_file( f) 

    with open(f) as fh:
        d = yaml.load(fh, Loader=yaml.FullLoader)
    return d


def __get_init_file(search_path='.'):
    """ 
    """
    filelist = []
    for filenb, file in enumerate(Path(search_path).rglob('*.yaml')):
        filelist.append(file)
        print('{:>3d}. {:s}'.format(filenb+1, os.path.relpath(file, search_path)))

    while True:
        # present possible candidate .yaml files
        init_file = input('select number of init file to use, or specify path: ')
        # user answered with a correct number
        if re.match('[0-9]+', init_file) and 1 <= int(init_file) <= len(filelist):
            init_file = filelist[int(init_file)]
        # check if the specified path is truly a file
        if Path(init_file).is_file():
            break
    
    return init_file
        

def grating_to_vertical_velocity(v, theta, sf, units='rad'):
    """ convert grating velocity to vertical velocity
    """
    if units == 'deg':
        theta = theta * math.pi / 180
    return np.array([0, v / math.sin(theta) * sf])