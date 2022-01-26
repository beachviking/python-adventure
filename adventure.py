#!/usr/bin/env python3
# Filename: gkadventure.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# gkAdventure is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. gkAdventure allows the use of custom maps, which are JSON-formatted.
#
# This file contains the main game logic.
#

import io
import sys
import json
import os.path

from AdventureGameState import AdventureGameState

from AdventureModel import AdventureModel
from AdventureView import AdventureView
from AdventureController import AdventureController
from AdventureUser import AdventureUser


def main(mapFile):
    """
    Main program block for gkAdventure
    """
    if fileExists(mapFile):
        map = loadMap(mapFile)
        play(map)
    else:
        usage()


def fileExists(filename):
    """
    Returns True if a filename exists
    """
    result = True
    if os.path.isfile(filename) == False:
        result = False
    return result


def loadMap(filename):
    """
    Loads JSON from a gkAdventure map and returns the data
    """
    jsonString = open(filename).read()
    result = json.loads(jsonString)
    return result


def play(map):
    """
    The main game logic for gkAdventure
    """
    # Define the local console
    localInput = sys.stdin
    localOutput = sys.stdout
    # Create a model instance (shared by all users)
    model = AdventureModel(map)
    # Create a user instance (containing a local view and controller)
    localUser = AdventureUser(AdventureView(localOutput, model), AdventureController(localInput, model))
    
    # Connect the user instance to the shared model (via the controller)
    localUser.connect()
    # User wants to play
    localUser.stillWantsToPlay = True
    # Set game state to Starting
    localUser.gameState = AdventureGameState.STARTING

    # Main game loop
    while localUser.stillWantsToPlay:
        # Starting
        if localUser.gameState == AdventureGameState.STARTING:
            localUser.transmit()
            localUser.gameState = AdventureGameState.STARTED
        # Started
        elif localUser.gameState == AdventureGameState.STARTED:
            localUser.transmit()
            localUser.gameState = AdventureGameState.PLAYING
        # Playing (primary gameplay)
        elif localUser.gameState == AdventureGameState.PLAYING:
            # Run before_each_turn noun scripts
            localUser.processBeforeTurnTriggers()
            # Transmit the user's view
            localUser.transmit()
            # Receive input from the user
            input = localUser.receive()
            # Process the input
            localUser.controller.parseCommandFromNounWithId(input, localUser.data['id'])
            # Run after_each_turn noun scripts
            localUser.processAfterTurnTriggers()
        # Finished / Won
        elif localUser.gameState == AdventureGameState.FINISHEDWON:
            # Transmit victory notification to all nouns
            for noun in localUser.controller.model.nouns:
                localUser.controller.model.sendNotificationToNoun(noun['id'] + ' has won the game.', noun)
                # And if any playable nouns aren't this user, they've lost
                if (noun['playable'] == 'true') and (noun['id'] != localUser.data['id']):
                    noun['id']['game_state'] = 'finished_lost'
                    localUser.controller.model.sendNotificationToNoun('Due to the sudden horror of this realization, you immediately drop dead of a heart attack.', noun)
            # Transmit the user's view
            localUser.transmit()
            localUser.gameState = AdventureGameState.QUITTING
        # Finished / Lost
        elif localUser.gameState == AdventureGameState.FINISHEDLOST:
            localUser.transmit()
            localUser.gameState = AdventureGameState.QUITTING
        # Quitting
        elif localUser.gameState == AdventureGameState.QUITTING:
            localUser.transmit()
            localUser.stillWantsToPlay = False
    
    # Set game state to Quit
    localUser.gameState = AdventureGameState.QUIT
    # Disconnect the user instance from the shared model
    localUser.disconnect()


def usage():
    """
    Displays usage information
    """
    print('gkAdventure, an iteractive fiction interpreter')
    print('Copyright (c) 2013 Greg M. Krsak (greg.krsak@gmail.com)')
    print('Provided under the MIT License: http://opensource.org/licenses/MIT')
    print()
    print('Usage: gkadventure.py <json_filename>')
    print()
    print('Where <json_filename> is the filename of a JSON-formatted gkAdventure map.')
    print('Please report any bugs to greg.krsak@gmail.com')


if __name__ == '__main__':
    argv = 'tutorial-map.json'
    try:
        argv = sys.argv[1]
    except:
        pass
    main(argv)
