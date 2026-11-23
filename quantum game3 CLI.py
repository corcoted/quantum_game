
# # Quantum Guessing Game
# by Ted Corcovilos 20160610
#
# The computer picks a random quantum spin-1/2 state from a predetermined list.
# The player requests measurements (Pauli operators Sx, Sy, or Sz) and attempts to guess the state.
# v.3 20261117 migrate to external game files

import random  #for generating random numbers for the measurements

random.seed() # set a seed based on current time

import argparse
import csv
from pathlib import Path

import numpy as np


def read_game_file(name):
    # reads the states from a csv file and returns them as an np.array
    with open(name) as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
    states = []
    comment = ""
    for row in rows:
        if row[0].startswith("#"):
            comment += row[0][1:]
            continue
        vector = np.array([float(i) for i in row])
        states.append(vector)
    return np.concat(states).reshape((-1,3)), comment

# States are stored as an array of Bloch vectors (length of vectors must be <= 1) in a csv file

def build_lookup(states):
    #Build lookup table (probablility of measuring + for each state) [axis, states]
    lookup=np.zeros((measurements.shape[0],Nstates),dtype=int)
    for i in range(measurements.shape[0]):
        for j in range(Nstates):
            lookup[i, j] = np.round(0.5*(1.0+np.dot(states[j],measurements[i]))*dsize)
    return lookup

def measure(state, axis):
    """
    Perform a quantum measurement on a state vector along an axis vector. Returns +/-1.
    """
    #simulate dice rolls
    if (random.randint(1,dsize)<=lookup[axis,state]):
        out = 1
    else:
        out = -1
    return out

def print_state_table():
    print(game_comment)
    print("Possible states are")
    for i in range(0,Nstates,1):
        print(f"{i}: {states[i]}")

def print_result_table(res,bad=[]):
    print("Result table: ")
    print(("{:>5} "*4).format("","x","y","z"))
    print(("{:>5} "*4).format("+",res[0,1], res[1,1], res[2,1]))        
    print(("{:>5} "*4).format("-",res[0,0], res[1,0], res[2,0]))
    if len(bad)>0:
        print(f"Bad guesses: {bad}")

def play(): #play the game!
    """
    Play the Game!
    """
    guesses = 0
    quit = False
    bad_guesses = []
    resultTable = np.zeros((measurements.shape[0],2),dtype=int)
    goal = random.randrange(Nstates)
    while (True): #main measurement loop
        print(f"Measurement number {guesses}")
        test = -1
        while test == -1: #make sure we have a valid input
            print("Which measurement do you want: x, y, z, (g)uess, (s)how states, show (r)esults, or (q)uit? ")
            key = input("Input: ")
            test = {
                'x': 0,
                'y': 1,
                'z': 2,
                'g': -10,
                's': -20,
                'r': -30,
                'q': -99
            }.get(key,-1)
        if(test==-99):
            print(f"Quit.  State was {goal}: {states[goal]}")
            quit=True
            break
        if(test==-20): # Show the state table
            print_state_table()
            continue
        if(test==-30): # Show the measurement results
            print_result_table(resultTable,bad_guesses)
            continue
        if(test==-10): # Handle guess
            print_state_table()
            key = int(input("Guess? "))
            if (key==goal):
                print(f"Correct! Final score: {guesses}")
                break
            else:
                print(f"Wrong! Penalty: {penalty}")
                bad_guesses.append(key)
                guesses = guesses+5
                continue
        guesses = guesses+1
        result = measure(goal,test)
        resultTable[test,(1+result)//2] = resultTable[test,(1+result)//2]+1
        #Ntests = resultTable[test,0]+resultTable[test,1]
        print(f"Measurement result: {result}")
        if (guesses>maxguess):
            print(f"Exceeded measurement limit!  Guesses = {guesses}")
            break
        print_result_table(resultTable,bad_guesses)
    return guesses, goal, quit

def main():
    q = False
    total = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file", help="Name of game file", default='game1.csv')
    args = parser.parse_args()
    game_file=Path(args.file)
    if not game_file.exists():
        raise OSError(f"Game file {game_file} not found.")

    # TODO don't use globals
    # some game constants
    global penalty; penalty = 5 #points for incorrect guess
    global maxguess; maxguess = 200 # maximum number of measurements allowed
    global dsize; dsize = 20 # size of the dice used for rolling

    # Game tables, etc.
    global states
    global Nstates
    global game_comment
    global measurements
    global Nmeasurements

    states, game_comment = read_game_file(game_file)
    Nstates = states.shape[0]
    measurements = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]) #measurement axes (Bloch sphere rep. of Pauli matrices)
    Nmeasurements = measurements.shape[0] # number of possible measurements
    global lookup
    lookup = build_lookup(states)
    while not q:
        c, g, q = play()
        total = total + c
        print(f"Total score = {total}")

if __name__ == "__main__":
    main()
