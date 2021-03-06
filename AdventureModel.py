
import random

from AdventureGameState import AdventureGameState


class AdventureModel:
    
    def __init__(self, mapJson):
        random.seed()
        self._map = mapJson
        self._map['users'] = []

    
    @property
    def idString(self):
        return self._map['adventure']
    
    @property
    def about(self):
        return self._map['about']
    
    @property
    def version(self):
        return self._map['version']
    
    @property
    def roomTypes(self):
        return self._map['room_types']

    @property
    def rooms(self):
        return self._map['rooms']

    @property
    def nouns(self):
        return self._map['nouns']
    
    @property
    def verbs(self):
        return self._map['verbs']
    
    @property
    def nextPlayableNounId(self) -> str:
        result = None
        for noun in (self.nouns):
            if noun['playable'] == 'true':
                result = noun['id']
        return result
    
            
    def connectUser(self, newUser):
        self.nounWithId(newUser.data['id'])['active'] = 'true'
        self.nounWithId(newUser.data['id'])['connected'] = 'true'


    def disconnectUserWithId(self, userId):
        self.nounWithId(userId)['active'] = 'false'
        self.nounWithId(userId)['connected'] = 'false'
    
    
    def childObjectOfParentArrayKeyWithChildId(self, parentArrayKey, objectId):
        result = None
        for childObj in (self._map[parentArrayKey]):
            if childObj['id'] == objectId:
                result = childObj
        return result

    
    def roomWithId(self, roomId):
        return self.childObjectOfParentArrayKeyWithChildId('rooms', roomId)

    
    def roomTypeWithId(self, roomTypeId):
        return self.childObjectOfParentArrayKeyWithChildId('room_types', roomTypeId)

    
    def nounWithId(self, nounId):
        return self.childObjectOfParentArrayKeyWithChildId('nouns', nounId)

    
    def nounIdWithShortDesc(self, shortDesc):
        result = None
        for noun in (self.nouns):
            if noun['short_desc'] == shortDesc:
                result = noun['id']
        return result
    
    
    def grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys(self, greatGrandparentArrayKey, parentArrayKey, childString):
        result = []
        for grandparentObj in (self._map[greatGrandparentArrayKey]):
            for childStr in (grandparentObj[parentArrayKey]):
                if childStr == childString:
                    result.append(grandparentObj)
        return result

    
    def roomsContainingNounWithId(self, nounId):
        result = [ ]
        result = self.grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys('rooms', 'obvious_nouns', nounId)
        if len(result) == 0:
            # If the noun is found in another noun's inventory, return the room of that noun
            result = self.grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys('nouns', 'inventory', nounId)
            if len(result) != 0:
                result = self.roomsContainingNounWithId(result[0]['id'])
        return result

    
    def setLitInRoomWithId(self, roomId, isLit):
        room = self.roomWithId(roomId)
        if isLit:
            room['lit'] = 'true'
        else:
            room['lit'] = 'false'


    def gameStateForNounWithId(self, nounId):
        result = None
        gameState = self.nounWithId(nounId)['game_state']
        if gameState == 'starting':
            result = AdventureGameState.STARTING
        elif gameState == 'started':
            result = AdventureGameState.STARTED
        elif gameState == 'playing':
            result = AdventureGameState.PLAYING
        elif gameState == 'finished_won':
            result = AdventureGameState.FINISHEDWON
        elif gameState == 'finished_lost':
            result = AdventureGameState.FINISHEDLOST
        elif gameState == 'quitting':
            result = AdventureGameState.QUITTING
        elif gameState == 'quit':
            result = AdventureGameState.QUIT
        return result


    def setGameStateForNounWithId(self, gameState, nounId):
        if gameState == AdventureGameState.STARTING:
            self.nounWithId(nounId)['game_state'] = 'starting'
        elif gameState == AdventureGameState.STARTED:
            self.nounWithId(nounId)['game_state'] = 'started'
        elif gameState == AdventureGameState.PLAYING:
            self.nounWithId(nounId)['game_state'] = 'playing'
        elif gameState == AdventureGameState.FINISHEDWON:
            self.nounWithId(nounId)['game_state'] = 'finished_won'
        elif gameState == AdventureGameState.FINISHEDLOST:
            self.nounWithId(nounId)['game_state'] = 'finished_lost'
        elif gameState == AdventureGameState.QUITTING:
            self.nounWithId(nounId)['game_state'] = 'quitting'
        elif gameState == AdventureGameState.QUIT:
            self.nounWithId(nounId)['game_state'] = 'quit'


    def expandSpecialVariablesInString(self, theString, sourceNounId, verbId, targetNounId, nounString):
        if sourceNounId != None:
            theString = theString.replace('${SOURCE_NOUN_ID}', sourceNounId)
        if targetNounId != None:
            theString = theString.replace('${TARGET_NOUN_ID}', targetNounId)
        if verbId != None:
            theString = theString.replace('${VERB_ID}', verbId)
        if nounString != None:
            theString = theString.replace('${TARGET_NOUN_STRING}', nounString)
        result = theString
        return result


    def execPythonString(self, pythonString) -> bool:
        result = True
        try:
            exec(pythonString)
        except:
            result = False
            # DEBUG
            print('[WARNING] script failed: \n' + pythonString + '\n')
        return result


    def preprocessedTriggerForNoun(self, trigger, noun) -> str:
        result = ''
        if noun[trigger] != None:
            result = self.expandSpecialVariablesInString(noun[trigger], noun['id'], None, None, None)
        return result


    def moveNounWithIdThroughExit(self, nounId, exitDir) -> bool:
        result = True
        currentRoom = self.roomsContainingNounWithId(nounId)[0]
        try:
            newRoomId = currentRoom['exit_' + exitDir]
            room = self.roomWithId(newRoomId)
            noun = self.nounWithId(nounId)
            allowedIn = True
            scared = False
            # Is this noun afraid of anything in its current room?
            for scaryItemId in noun['afraid_of']:
                if (scaryItemId in currentRoom['obvious_nouns']) and (self.nounWithId(scaryItemId)['alive'] == 'true'):
                    scared = True
            if not scared:
                # Are there any required items in the new room?
                if len(room['requires_nouns']) != 0:
                    # Check the noun's inventory for those items
                    for requiredItem in room['requires_nouns']:
                        if requiredItem not in noun['inventory']:
                            allowedIn = False
                if allowedIn:
                    # Attempt to move the noun
                    self.removeNounWithIdFromRoomWithId(nounId, currentRoom['id'])
                    self.addNounWithIdToRoomWithId(nounId, newRoomId)
                    # Run the on_entry script of the new room
                    pythonString = self.expandSpecialVariablesInString(room['on_entry'], nounId, exitDir, None, None)
                    self.execPythonString(pythonString)
                else:
                    # Notify the noun that it's missing required items
                    self.sendNotificationToNoun('You\'re missing an item that permits you to go that way.', noun)
            else:
                # Notify the noun that it's afraid
                self.sendNotificationToNoun('You\'re too terrified to do that!', noun)
        except:
            result = False
            # Unable to move
            noun = self.nounWithId(nounId)
            # Notify the noun of its inability to move
            self.sendNotificationToNoun('You can\'t go that way.', noun)
        return result


    def sendNotificationToNoun(self, notificationString, noun) -> bool:
        result = False
        # Only send the notification if the noun is playable and connected
        if noun['playable'] == 'true':
            if noun['connected'] == 'true':
                noun['notifications'].append(notificationString)
                result = True
        return result


    def addNounWithIdToRoomWithId(self, nounId, roomId) -> bool:
        result = False
        obviousNouns = self.roomWithId(roomId)['obvious_nouns']
        if nounId not in obviousNouns:
            obviousNouns.append(nounId)
            result = True
        return result
    

    def removeNounWithIdFromRoomWithId(self, nounId, roomId) -> bool:
        result = False
        obviousNouns = self.roomWithId(roomId)['obvious_nouns']
        if nounId in obviousNouns:
            obviousNouns.remove(nounId)
            result = True
        return result


    def addNounWithIdToInventoryOfNounWithId(self, sourceNounId, targetNounId) -> bool:
        result = False
        sourceNoun = self.nounWithId(sourceNounId)
        targetNoun = self.nounWithId(targetNounId)
        if sourceNounId not in targetNoun['inventory']:
            targetNoun['inventory'].append(sourceNounId)
            result = True
            self.sendNotificationToNoun('Taken.', self.nounWithId(targetNounId))
            # Run the on_take script
            pythonString = self.expandSpecialVariablesInString(sourceNoun['on_take'], targetNounId, 'take', sourceNounId, 'take')
            self.execPythonString(pythonString)
        return result


    def removeNounWithIdFromInventoryOfNounWithId(self, sourceNounId, targetNounId) -> bool:
        result = False
        sourceNoun = self.nounWithId(sourceNounId)
        targetNoun = self.nounWithId(targetNounId)
        if sourceNounId in targetNoun['inventory']:
            targetNoun['inventory'].remove(sourceNounId)
            result = True
            self.sendNotificationToNoun('Dropped.', self.nounWithId(targetNounId))
            # Run the on_drop script
            pythonString = self.expandSpecialVariablesInString(sourceNoun['on_drop'], targetNounId, 'drop', sourceNounId, 'drop')
            self.execPythonString(pythonString)
        return result


    def switchNounWithId(self, nounId) -> bool:
        result = False
        noun = self.nounWithId(nounId)
        if noun['switchable'] == 'true':
            result = True
            holders = self.grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys('nouns', 'inventory', nounId)
            if noun['on'] == 'false':
                noun['on'] = 'true'
                for holdingNoun in holders:
                    self.sendNotificationToNoun('The ' + noun['short_desc'] + ' is now on.', holdingNoun)
            else:
                noun['on'] = 'false'
                for holdingNoun in holders:
                    self.sendNotificationToNoun('The ' + noun['short_desc'] + ' is now off.', holdingNoun)


    def lookAtNounStringFromNounWithId(self, targetNounString, sourceNounId) -> bool:
        if targetNounString[0] != '$':
            # A noun was specified by the user
            visible = True
            targetNounId = self.nounIdWithShortDesc(targetNounString)
            if targetNounId != None:
                # Target noun exists
                if self.roomsContainingNounWithId(sourceNounId)[0] in self.roomsContainingNounWithId(targetNounId):
                    # And is in the same room as the source noun
                    pass
                else:
                    visible = False
            else:
                # Target noun does not exist
                visible = False
            if visible:
                self.sendNotificationToNoun(self.nounWithId(targetNounId)['long_desc'], self.nounWithId(sourceNounId))
            else:
                self.sendNotificationToNoun('You don\'t see a ' + targetNounString + ' here.', self.nounWithId(sourceNounId))
            result = visible
        else:
            # The user just typed "look"
            self.sendNotificationToNoun(self.roomTypeWithId(self.roomsContainingNounWithId(sourceNounId)[0]['type'])['long_desc'], self.nounWithId(sourceNounId))
            result = True
        return result


    def attackNounStringFromNounWithId(self, defenderNounString, attackerNounId) -> bool:
        if defenderNounString[0] != '$':
            # A noun was specified by the user
            visible = True
            defenderNounId = self.nounIdWithShortDesc(defenderNounString)
            if defenderNounId != None:
                # Target noun exists
                if self.roomsContainingNounWithId(attackerNounId)[0] in self.roomsContainingNounWithId(defenderNounId):
                    # And is in the same room as the source noun
                    pass
                else:
                    visible = False
            else:
                # Target noun does not exist
                visible = False
            if visible:
                # Is the target mortal?
                defenderNoun = self.nounWithId(defenderNounId)
                if defenderNoun['mortal'] == 'true':
                    # And is it alive?
                    if defenderNoun['alive'] == 'true':
                        # And does the attacker have any weapons in their inventory?
                        attackerNoun = self.nounWithId(attackerNounId)
                        attackerIsArmed = False
                        for itemId in attackerNoun['inventory']:
                            if self.nounWithId(itemId)['weapon'] == 'true':
                                attackerIsArmed = True
                        if attackerIsArmed:
                            # Ok, target is dead
                            defenderNoun['alive'] = 'false'
                            # Run the on_death script
                            pythonString = self.expandSpecialVariablesInString(defenderNoun['on_death'], attackerNounId, 'kill', defenderNounId, 'kill')
                            self.execPythonString(pythonString)
                        else:
                            # No weapons!
                            # FIXME: Right now, the attacker simply loses if it doesn't have a weapon
                            self.sendNotificationToNoun('Since you didn\'t bring a weapon to this fight... well, you got killed.', attackerNoun)
                            self.setGameStateForNounWithId(AdventureGameState.FinishedLost, attackerNounId)
            else:
                self.sendNotificationToNoun('You don\'t see a ' + defenderNounString + ' here.', self.nounWithId(attackerNounId))
            result = visible
        else:
            # The user just typed "kill"
            self.sendNotificationToNoun('Looking to fight, eh? You\'ll need to specify a target!', self.nounWithId(attackerNounId))
            result = True
        return result


    def randomObviousExitForRoom(self, room) -> str:
        exitDir = None
        obviousExits = room['obvious_exits']
        exitList = obviousExits.split(',')
        # Iterate through all obvious exits
        if len(exitList) != 0:
            stillLooking = True
            while stillLooking:
                for exit in (exitList):
                    exitDir = exit.strip()
                    # If a random check passes, choose this exit
                    if random.randrange(1,4) == 2:
                        stillLooking = False
                        break
        return exitDir


    def moveNounWithIdRandomly(self, nounId) -> bool:
        result = True
        try:
            oldRoom = self.roomsContainingNounWithId(nounId)[0]
            exitDir = self.randomObviousExitForRoom(oldRoom)
            if self.moveNounWithIdThroughExit(nounId, exitDir):
                newRoom = self.roomsContainingNounWithId(nounId)[0]
                # Notify nouns in the new room
                for otherNounId in newRoom['obvious_nouns']:
                    # But only if the noun was not in the previous room
                    if otherNounId not in oldRoom['obvious_nouns']:
                        shortDesc = self.nounWithId(nounId)['short_desc']
                        self.sendNotificationToNoun('a ' + shortDesc + ' unexpectedly enters the room.', self.nounWithId(otherNounId))
            else:
                print('[DEBUG] ' + nounId + ' was unable to move ' + exitDir)
                pass
        except:
            result = False
        return result
