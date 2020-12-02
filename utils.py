from scipy.stats import lognorm
import numpy as np
import os
from pathlib import Path
import random
import csv
from psychopy import core
from psychopy.data import TrialHandler


def wait_keypress( kb, wait):
    timer = core.CountdownTimer( wait)
    while timer.getTime() > 0 :
        keys = kb.getKeys( [ 'quit', 'space'], clear=True)
        if 'space' in keys:
            break
        elif 'quit' in keys:
            ans = input( 'Do you really want to quit the experiment? [y/n] ')
            if ans.lower() == 'y':
                core.quit()
            

def loglikelihood_lognormal( waiting_times):
    """ compute the most likely parameters for the log-normal law, given waiting times
    Arguments
    waiting_times   : array of waiting times in the process

    Returns
    mu      : mean of the lognormal variable
    sigma   : standard deviation of the lognormal variable
    """
    sigma, _, scale = lognorm.fit(waiting_times, loc=0)
    mu = np.log(scale)
    return mu, sigma


def draw_next_waiting_time(mu, sigma):
    """ compute the waiting time until the next event, given lognormal distribution
    Arguments
    mu      : mean of the lognormal variable
    sigma   : standard deviation of the lognormal variable

    Returns
    t       : a single sample, specifying waiting time until the next event (flip)
    """

    X = lognorm(s=sigma, loc=0, scale=np.exp(mu))
    return X.rvs()


def getModalities(expInfo):
    return ",".join([s for s in expInfo['metaData']['modalities']])


def get_subjectid(subject):
    return subject['study'] + subject['subject_id'] + '_' + '{:1d}'.format(subject['session'])


def register_subject(datapath='../Data', modalities=None):
    """ register a subject in the database

    if the subject is already registered, then increment the counter of the session number
    if not register the subject in its first session
    """
    def generate_id():
        return '{:05d}'.format(random.randint(0, 99999))

    # take care of the data path
    datapath = Path(datapath).resolve()
    while True:
        try:
            os.mkdir(datapath)
            print("{} succesfully created!".format(datapath))
            break
        except FileExistsError:
            ans = input("{} already exists, using this directory for data storage? Y/[N]? ".format(datapath))
            if ans in {"y", "Y"}:
                print("Your choice has been succesfully registered")
                break
            else:
                datapath = Path(input("specify a new datapath: ")).resolve()

    # probe for study
    while True:
        study = input('Is your subject participating in a Pilot or in the main Study? P / [S]? ').upper()
        if study in {'P', 'S', ''}:
            study = 'S' if study=='' else study
            break
        else:
            print('Invalid answer, please specify P or S')

    participant_list = Path(datapath, 'participants.tsv')
    # create a participant list at the root of the data directory if it does not yet exist and corresponding subject id
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
            print(registered_participants)
            sid = input('give the subject id if the subject is already in the list of participants, if not press [ENTER]: ')
            if sid in registered_participants:
                session = max([int(p['session']) for p in participants if p['subject_id']==sid]) + 1
                if study == 'P':
                    print('It is not allowed to do more than one pilot session on the same subject, converting to main Study!')
                    study = 'S'  # not allowed to do twice a pilot on the same person
                break
            elif sid == '':
                sid = generate_id()
                session = 1 if study=='S' else 0
                while sid in participants:  # must be a unique id
                    sid = generate_id()
                break
                
    subject = dict(subject_id=sid, study=study, session=session, modalities=','.join(modalities))
    with open(participant_list, 'a+', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, delimiter='\t', fieldnames=['subject_id', 'study', 'session', 'modalities'])  # tab seperated file
            writer.writerow(subject) 
    
    # create some extra folders
    subject_path = Path(datapath, get_subjectid(subject)[:-2])
    try:
        os.mkdir(subject_path)
    except FileExistsError:
        pass

    for m in subject['modalities'].split(','):
        try:
            os.mkdir(Path(subject_path, m))
        except FileExistsError:
            pass
               
    return subject, subject_path


def set_experiment_mode():
    while True:
        mode = input('Do you want to run the [[F]]ull experiment or only a [T]est? ')
        if mode.lower() in {'f', ''}:
            run_mode = "full"
            break
        elif mode.lower() == 't':
            run_mode = "test"
            break
        else:
            print("Run mode {} unknown, please choose either 't' or 'f'.".format(mode))
    return run_mode


def create_experiment_structure( nBlocks = 3):
    conditions = ['nAmb_nKp', 'nAmb_Kp', 'Amb_nKp', 'Amb_Kp']  # the four different conditions, key to our experiment
    learning_phase = TrialHandler( [ dict( cond=conditions[k]) for k in range(3)], 1, method='sequential')
    training_phase = TrialHandler( [ dict( cond=conditions[3])], 4)
    testing_phase = TrialHandler( [ dict( cond=conditions[k]) for k in range(4)], nBlocks, method='random')

    exp_structure = TrialHandler(
        [ dict( name="learn", trials=learning_phase),
          dict( name="train", trials=training_phase),
          dict( name="test", trials=testing_phase)], nReps=1, method='sequential')
    return exp_structure