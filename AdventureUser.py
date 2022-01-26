# Filename: AdventureUser.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# gkAdventure is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. gkAdventure allows the use of custom maps, which are JSON-formatted.
#
# This file contains the "user" code. The user provides input to the controller,
# and receives output from the view.
#

from AdventureController import AdventureController
from AdventureGameState import AdventureGameState
from AdventureView import AdventureView


class AdventureUser:
    
    def __init__(self, view: AdventureView, controller: AdventureController):
        self.view = view
        self.controller = controller
        
        self._data = self.view.dictionaryForNewUser

    
    @property
    def data(self):
        return self._data
    

    @property
    def gameState(self):
        return self.controller.gameStateForUserWithId(self._data['id'])
    @gameState.setter
    def gameState(self, v):
        self.controller.setGameStateForUserWithId(v, self._data['id'])

    
    def input(self):
        return self.controller.waitForInput();
    
    
    def output(self):
        return self.view.output
    
    
    def connect(self):
        self.controller.connectUser(self)


    def disconnect(self):
        self.controller.disconnectUser(self)


    def processBeforeTurnTriggers(self):
        for noun in self.controller.model.nouns:
            pythonString = self.controller.preprocessedBeforeTurnTriggerForNoun(noun)
            self.controller.runScript(pythonString)


    def processAfterTurnTriggers(self):
        for noun in self.controller.model.nouns:
            pythonString = self.controller.preprocessedAfterTurnTriggerForNoun(noun)
            self.controller.runScript(pythonString)


    def transmit(self):
        # Starting
        if self.gameState == AdventureGameState.STARTING:
            self.view.renderWelcomeBanner()
            # Transmit the view to the user
            self.view.output.write(self.view.waitingOutput())
        # Started
        elif self.gameState == AdventureGameState.STARTED:
            pass
        # Playing
        elif self.gameState == AdventureGameState.PLAYING:
            userId = self.data['id']
            userRoom = self.controller.model.roomsContainingNounWithId(userId)[0]
            self.view.renderNotificationsForNounId(userId)
            self.view.renderRoom(userRoom)
            self.view.renderInputPromptForNounId(userId)
            # Don't let the player notice themself in the room
            # FIXME: There's a better way than this
            friendlyNoun = self.controller.model.nounWithId(self.data['id'])['short_desc']
            indefiniteArticle = self.view.indefiniteArticleForWord(friendlyNoun)
            stringToRemove = indefiniteArticle + ' ' + friendlyNoun + ' is here\n'
            sanitizedOutput = self.view.waitingOutput().replace(stringToRemove, '')
            # Transmit the view to the user
            self.view.output.write(sanitizedOutput)
        # Finished / Won
        elif self.gameState == AdventureGameState.FINISHEDWON:
            userId = self.data['id']
            userRoom = self.controller.model.roomsContainingNounWithId(userId)[0]
            self.view.renderNotificationsForNounId(userId)
            self.view.renderRoom(userRoom)
            self.view.renderVictoryMessageForNounId(userId)
            # Don't let the player notice themself in the room
            # FIXME: There's a better way than this
            friendlyNoun = self.controller.model.nounWithId(self.data['id'])['short_desc']
            indefiniteArticle = self.view.indefiniteArticleForWord(friendlyNoun)
            stringToRemove = indefiniteArticle + ' ' + friendlyNoun + ' is here\n'
            sanitizedOutput = self.view.waitingOutput().replace(stringToRemove, '')
            # Transmit the view to the user
            self.view.output.write(sanitizedOutput)
            pass
        # Finished / Lost
        elif self.gameState == AdventureGameState.FINISHEDLOST:
            userId = self.data['id']
            userRoom = self.controller.model.roomsContainingNounWithId(userId)[0]
            self.view.renderNotificationsForNounId(userId)
            self.view.renderDefeatMessageForNounId(userId)
            # Transmit the view to the user
            self.view.output.write(self.view.waitingOutput())
        # Quitting
        elif self.gameState == AdventureGameState.QUITTING:
            pass
        # (unknown game state)
        else:
            print('[ERROR] User game state is set to an unknown value of \'' + self.gameState + '\'')

    def receive(self):
        # Receive input from the user
        return self.controller.waitForInput()

