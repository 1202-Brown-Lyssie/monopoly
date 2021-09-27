"""
This program is a recreation of the Monopoly board game. The board game is owned by Hasbro. 

Things that need to be added or changed:
Get Out Of Jail Free - this just needs to be checked over again to see if it's all finished.
Income Tax Space - this doesn't do the proper thing, but it doesn't break anything.
Trade System - This is very broken.
Bankrupt Checker - This is very broken.
Conceding - This isn't implimented.
End-of-Game checker - This is not implimented. 
Visual representation of the board - This is not implimented.
Help - This is not implimented in places, and the linking of a pdf isn't ideal.
Randomized Dice Roll - If there are any places in which this isn't there, this needs to be implimented.
Low priority:
Make it so that you can do things inbetween doubles rolls.

author: Lyssie Brown
date: Fall2020
python: 3.8.3
"""


import random

"""There are 3 different types of spaces that a player can own: a Railroad, Utility, and Property.

Each are defined separately because they function in very different ways; however, players can own any of them.
"""

class Railroad():
    """
    This class defines all Railroad objects within the game. The rent of a Railroad is determined by how many
    Railroads are owned by the specific player.
    """
    def __init__(self, name): #To create a Railroad, you need to give it a unique name
        self.name = name
        self.owner = "Bank" #By default, each Railroad is owned by the Bank
        self.cost = 200 #It costs 200 to buy when you land on it.
    def setRent(self, props): #This function will update the rent of the Railroad. It requires the full list of properties in the game.
        #railOwned is the list of all Railroad objects in the list of properties that are ALSO owned by the same owner as the current Railroad.
        #In this way, one person might own 3 railroads and one person might own 1, and the price will be different for each person's Railroads.
        railOwned = [f for f in props if isinstance(f, Railroad) and f.owner == self.owner]
        #The rent, or what a player pays to the owner when they land on the space,
        #is 25 if 1 is owned, 50 if 2, 100 if 3, and 200 is 4
        self.rent = 25 * 2 ** (len(railOwned)-1)

class Utility():
    """
    This class defines all Utility objects within the game. The rent of a Utility is determined by the dice roll
    of the player landing on it, and whether or not the owner has a monopoly on the utilities.
    """
    def __init__(self, name): #To create a Utility, you need to give it a unique name
        self.name = name
        self.owner = "Bank" #By default, each Utility is owned by the Bank
        self.cost = 150 #It costs 150 to buy when you land on it.
        #self.rent = 0
    def setRent(self, props, diceroll): #Unlike other properties, a Utility's rent is dependent on the
        #dice roll of the person landing on it.
        #utilitiesOwned is the list of all Utility objects that are owned by the same owner as the current Utility.
        utilitiesOwned = [f for f in props if isinstance(f, Utility) and f.owner == self.owner] 
        if len(utilitiesOwned) == 2: #If the person owns both utilities in the game,
            self.rent = 10*diceroll 
        else: #the person only owns 1 utility
            self.rent = 4*diceroll #Rent is 4 times the dice roll.

class Property():
    """
    This class defines all Property objects within the game. The rent of a Property is determined by how many
    buildings are on it, and the prices that correspond to each specific property.
    """
    def __init__(self, name, cost, paymentPlan, buildingCost, color): #Name is the name of the Property. Cost is how much it costs to buy it. Payment plan is how much the
        #rent is worth depending on how many bulidings are on it. Building cost is the cost of a buliding to purchase. Color is the color of the property.
        self.name = name
        self.owner = "Bank"
        self.cost = cost
        self.houses = 0
        self.hotels = 0
        self.paymentPlan = paymentPlan
        self.buildingCost = buildingCost
        self.isMortgaged = False
        self.setRent()
        self.color = color
    def setRent(self):
        #This function updates the rent of the property.
        if not self.isMortgaged:
            if self.hotels == 0:
                self.rent = self.paymentPlan[self.houses]
            else:
                self.rent == self.paymentPlan[4]
        else:
            self.rent = 0
    def addBuilding(self):
        #This function adds a building to the property. It adds a house if less than 4 houses are already on it, and replaces the houses with a hotel if 4 houses are on it.
        if self.houses < 4:
            self.houses += 1
        elif self.houses == 4:
            self.houses = 0
            self.hotels = 1
        else:
            return "cannot"
    def removeBuilding(self):
        #This function is the reverse of the addBuilding function.
        if self.hotels == 1:
            self.hotels = 0
            self.houses = 4
        elif self.houses > 0:
            self.houses =- 1
        else:
            return "cannot"

class Entity(): #The Bank is the only entity in the game, but each Person inherits all of the Entity methods.
    def __init__(self, properties):
        self.money = 1 * 10^8 #An arbitrarily big number
        self.properties = []
        for x in properties:
            self.properties.append(x)
    def giveMoney(self, amt, recipient):
        #Gives money to one player (or the Bank) at the expense of the other.
        recipient.money += amt
        self.money -= amt
    def getPropertyByName(self, propName):
        #Returns the property object that corresponds to the string of the name given.
        for x in self.properties:
            if x is not None:
                if x.name == propName:
                    return x
        return None
    def giveProperty(self, propName, recipient):
        #Moves a property from self.properties to the list of properties of another player/Bank.
        giftProp = self.getPropertyByName(propName)
        giftProp.owner = recipient.name
        recipient.properties.append(giftProp)
        self.properties.remove(giftProp)
    def mortgageProperty(self, propName):
        #Changes the isMortaged boolean to True of an owned property and gives 1/2 the value of the property to the owner.
        prop = self.getPropertyByName(propName)
        prop.isMortgaged = True
        self.money += .5 * prop.cost
    def unmortgageProperty(self, propName):
        #Changes the isMortaged boolean to False of an owned property and makes the owner pay 1/2 the value of the property + 10% of that (55% of the value of the property in total).
        prop = self.getPropertyByName(propName)
        prop.isMortgaged = False
        self.takeMoney(.55 * prop.cost)


class Person(Entity):
    """
    All players are instances of Person. A Person can move across the board and can purchase buildings.
    change: create trade system

    """
    def __init__(self, name):
        self.name = name
        self.location = 0 #The location on the board; used with gameBoardSpaces
        self.money = 1500
        self.jailCountdown = 0 #Used with the jail_space function
        self.getOutOfJailFreeCards = 0 #A person can get a Get out of Jail Free card from a chance or community chest card
        self.properties = []
        self.doublesCounter = 0 #Used to count the number of doubles rolls a person has had at any point in their turn. If this hits 3, they go to jail
    def moveLinear(self, x, allowPassingGo = True, nearestCard = False, doublesAllowed = True):
        if type(x) == str: #change
            newX = x.split(',')
            newMovement = int(newX[0]) + int(newX[1])
            gotDoubles = newX[0] == newX[1]
            if gotDoubles and self.doublesCounter == 2:
                print("You got doubles! Because you have gotten doubles 3 times this turn, you must go to jail.".format(d=self.doublesCounter))
                goToJail(self)
                return
            self.location += newMovement
        elif type(x) == list:
            if x[0] == x[1] and self.doublesCounter == 2:
                goToJail(self)
                return
            self.location += int(x[0]) + int(x[1])
        else:
            self.location += x
        if self.location >= len(gameBoardSpaces):
            print("You're above the limit for where you should be!!! You're at " + str(self.location))
            self.location -= len(gameBoardSpaces)
            print("You are now at " + str(self.location))
            if allowPassingGo and self.location > 0:
                    print("You passed go and get to collect $200!")
                    self.money += 200
                    print("You now have {money}.".format(money=self.money))
        if isinstance(gameBoardSpaces[self.location], (Property, Utility, Railroad)):
            print("You landed on {0}!".format(gameBoardSpaces[self.location].name))
            if isinstance(gameBoardSpaces[self.location], Utility):
                utility_space(self, x, nearestCard = nearestCard)
            else:
                prop_space(self, nearestCard = nearestCard)
        else:
            print("You landed on something other than a Property, Utility, or Railroad.")
            gameBoardSpaces[self.location](self)
        if type(x) == str and doublesAllowed and not self.jailCountdown:
            if gotDoubles:
                self.doublesCounter += 1
                print("You got doubles! You have gotten doubles {d} times this turn.".format(d=self.doublesCounter))
                
                #User-entered dicerolling
                #doublesRoll = input("You may roll again. What did you roll?")
                #Random dicerolling
                print("You may roll again.")
                doublesRoll = rollTwoDice()
                #End random dicerolling
                print("You rolled {0}.".format(" and ".join(str(x) for x in doublesRoll)))
                self.moveLinear(doublesRoll)
        elif type(x) == list and doublesAllowed and not self.jailCountdown:
            if x[0] == x[1]:
                self.doublesCounter += 1
                print("You got doubles! You have gotten doubles {d} times this turn.".format(d=self.doublesCounter))
                
                #User-entered dicerolling
                #doublesRoll = input("You may roll again. What did you roll?")
                #Random dicerolling
                print("You may roll again.")
                doublesRoll = rollTwoDice()
                #End random dicerolling
                print("You rolled {0}.".format(" and ".join(str(x) for x in doublesRoll)))
                self.moveLinear(doublesRoll)

    def hasMonopoly(self,color):
        #Function to check if a player has a monopoly in a certain color
        for p in getNamesInColorGroup(color):
            if p not in [x.name for x in self.properties]:
                #print(p)
                return False
        return True
    def purchaseBuilding(self, propName):
        #Used to put a building on a property
        prop = self.getPropertyByName(propName)
        if self.hasMonopoly(prop.color):
            prop.addBuilding()
            prop.setRent()
            return "success"
        else:
            return "failed"
    def sellBuilding(self, propName):
        #Used to sell a building on a property
        prop = self.getPropertyByName(propName)
        if self.hasMonopoly(prop.color):
            prop.removeBuilding()
            prop.setRent()
            self.money += prop.buildingCost
            return "success"
        else:
            return "failed"
    def takeMoney(self, amt, canExit = True, recipientIfBankrupt = "Bank"):
        #UNFINISHED,
        #replace 'person += some integer' statements throughout code, which will allow the player to go bankrupt or make money in order to avoid going bankrupt from having to pay money.
        #if person can't pay the money, they need to be able to sell buildings and mortgage property (with BANK)
        #and sell property without any bulidings on the color group to another player. also sell railroads and utilities to other players
        #if the person can't sell anything else and make up the money, then they have to give up their remaining money AND property (liquidated if bank) to the recipient
        #CHANGE: in the game there's a rule that you need to pay an interest of 10 percent of the property's rent if you purchase it from another player. we can add that to the giveProperty() function
        while True:
            if self.money + amt < 0: #If the person can't afford to pay the amount
                print("You can't afford to pay the amount.")
                if canExit: #If the person can't afford to pay the amount, but is allowed to not pay (as in, they are buying a building or property, not paying would mean the sale doesn't go through)
                    return False
                else: #The person isn't allowed to exit, so they must pay the amount.
                    print("You must make enough money to pay the amount. You can do this by selling buildings on any properties you own, mortaging properties,\nand trading with other players.")
                    while True:
                        if self.money + amt < 0: #The person still needs to make enough money to pay the amount
                            options = ["TRADE", "SELL BUILDING", "MORTGAGE", "EXIT", "DECLARE BANKRUPTCY"]
                            choice = input("Please type either TRADE (to trade with other players), SELL BUILDING (to sell buildings on property you own), MORTGAGE (to mortgage a property), \
EXIT (if you have made enough money) DECLARE BANKRUPTCY (to exit this menu and lose the game)")
                            if choice.upper() not in options:
                                print("Please chose another option, or type EXIT to exit.")
                                continue
                            elif choice.upper() == "TRADE":
                                self.trade()
                            elif choice.upper() == "SELL BUILDING":
                                propName = input("Please choose a property to sell a building on.")
                                if self.getPropertyByName(propName) is not None:
                                    self.sellBuilding()
                                else:
                                    print("Your request failed.")
                            elif choice.upper() == "MORTGAGE":
                                ropName = input("Please choose a property to sell a building on.")
                                if self.getPropertyByName(propName) is not None:
                                    self.sellBuilding()
                                else:
                                    print("Your request failed.")
                                    
                        else: #The person has made enough money to pay the amount
                            self.money += amt
                            break
            else: #If the person can afford to pay the amount 
                self.money += amt
                break

#The following functions are all run when a player moves (Person.moveLinear function). They are pretty much done.
def go_space(person): 
    person.money += 200
    print(person.name + str(person.money))
def prop_space(person, nearestCard = False): #For Properties and Railroads
    prop = [x for x in props if x.name == gameBoardSpaces[person.location].name][0]
    print("This property is owned by {0}.".format(prop.owner))
    if prop.owner == "Bank":
        if input("Do you want to buy this property?") == "yes":
            Board.giveProperty(prop.name, person)
            person.money -= prop.cost
            print("You now have {0} left.".format(person.money))
            print("Your properties are: {0}".format(",".join([x.name for x in person.properties])))
        else:
            print("Okay, you didn't buy this property.")
    elif nearestCard:
        print("You must pay {0} to {1}.".format(prop.rent*2,prop.owner))
        person.money -= prop.rent*2
        getPersonByName(prop.owner).money += prop.rent*2
        print("{0} has {1} left.".format(prop.owner,getPersonByName(prop.owner).money))
        print("You, {0}, have {1} left.".format(person.name, person.money))
    else:
        print("You must pay {0} to {1}.".format(prop.rent,prop.owner))
        person.money -= prop.rent
        getPersonByName(prop.owner).money += prop.rent
        print("{0} has {1} left.".format(prop.owner,getPersonByName(prop.owner).money))
        print("You, {0}, have {1} left.".format(person.name, person.money))
def utility_space(person, diceroll, nearestCard = False):
    prop = [x for x in props if x.name == gameBoardSpaces[person.location].name][0]
    print("This property is owned by {0}.".format(prop.owner))
    if prop.owner == "Bank":
        if input("Do you want to buy this property?") == "yes":
            Board.giveProperty(prop.name, person)
            person.money -= prop.cost
            print("You now have {0} left.".format(person.money))
            print("Your properties are: {0}".format(",".join([x.name for x in person.properties])))
        else:
            print("Okay, you didn't buy this property.")
    elif nearestCard: #This only happens when nearestCard is True and the space is owned by someone other than the Bank.
    #nearestCard is only True when the player draws a certain card
        
        #User-entered dicerolling
        #specialRoll = int(input("What did you roll?"))
        #Random dicerolling
        print("You may roll again.")
        specialRoll = rollTwoDice()
        #End random dicerolling
        print("You rolled {0}.".format(" and ".join(str(x) for x in specialRoll)))

        #~~
        print("You must pay {0} to {1}.".format(specialRoll*10,prop.owner))
        person.money -= specialRoll*10
        getPersonByName(prop.owner).money += specialRoll*10
        print("{0} has {1} left.".format(prop.owner,getPersonByName(prop.owner).money))
        print("You, {0}, have {1} left.".format(person.name, person.money))
    else: #In normal cases
        prop.setRent(props, diceroll)
        print("You must pay {0} to {1}.".format(prop.rent,prop.owner))
        person.money -= prop.rent
        getPersonByName(prop.owner).money += prop.rent
        print("{0} has {1} left.".format(prop.owner,getPersonByName(prop.owner).money))
        print("You, {0}, have {1} left.".format(person.name, person.money))
def jail_space(person):
    #This function is used to determine what happens for any player that is sitting in jail (on space 10).
    #The following are the rules that determine what happens when a player is on the jail space.
    #If the person is just visiting jail, their .jailCountdown value will be 0. Thus, nothing much happens,
    # and it is similar to Free parking.
    #If the person was put in jail, they will be forced to stay in jail until they get out.
    #Upon being sent to jail, their turn ends.
    #On their next turn, they get the opportunity to either use a Get Ouf of Jail Free card (if they have one),
    # or they can roll.
    #If they roll dice, and if they get doubles, they get out of jail and move forward that many spaces.
    if not person.jailCountdown: #0 #if the person starts with 0, aka they're just visiting
        print("You're in jail! Just visiting~")
        return
    elif person.jailCountdown == 4:
        person.jailCountdown -= 1
    elif person.jailCountdown > 1: #3, 2, 1 ->2, 1, 0
        print("You're in jail! You have {num} turns left.".format(num=person.jailCountdown)) 
        if person.getOutOfJailFreeCards > 0:
            print("If you use a Get Out of Jail Free card or roll doubles, you will be allowed out of jail.")
            useCard = input("Would you like to use a Get Out of Jail Free Card?")
            if useCard == 'yes':
                print("You used a card.")
                #CHANGE: this doesn't use rollTwoDice() nor can it handle lists.
                a = int(input("You may now roll to move! What did you roll?"))
                person.jailCountdown = 0
                person.moveLinear(a)
                willRoll = False
            else:
                print("You didn't use a card.")
                willRoll = True
        else:
            willRoll = True
        if willRoll:
            a, b = input("What did you roll?").split(",")
            print(a, b)
            a= int(a)
            b=int(b)
            if a == b:
                print("You rolled {0} and {1}! That's doubles. Congratulations, you can move {2}.".format(a, b, a+b))
                person.jailCountdown = 0
                person.moveLinear(a+b)
            else:
                print("You rolled {0} and {1}! You didn't get doubles.".format(a, b))
                person.jailCountdown -= 1
                print("You have {0} turns left in jail.".format(person.jailCountdown))
                if person.jailCountdown == 0: #this could put the person to 0
                    print("You ran out of turns. You must pay a $50 fine, and you will move forward the number of spaces you just rolled.")
                    print("Even if you roll doubles this turn, you do not get to go again.")
                    person.moveLinear(a+b)
                    return
    if person.jailCountdown == 0:
        print("You, {0}, need to pay 50 dollars.".format(person.name))
        person.money -= 50
        print("You have {0}".format(person.money))
def goToJail(person):
    print("Go to jail!")
    person.jailCountdown = 4
    person.moveLinear(10 - person.location, allowPassingGo=False)
def go_to_jail_space(person):
    goToJail(person)
def income_tax_space(person): #!!! change: finish this
    print("Nothing to see here.")
def luxury_tax_space(person):
    print("You were fined 75 dollars.")
    person.money -= 75
def free_parking_space(person):
    print("Nothing happens at Free Parking.")



#The following two lists of dictionaries are used to define the chance and community chest cards in the game.
#When a player lands on a chance space, they 'draw' one of the chance cards.
#When a player lands on a chest cards, they 'draw' one of the community chest cards.
#One card, aka dictionary is passed as **card into the do_the_card function.
#For better understanding of the cards themselves, see the do_the_card function.
chance_cards = [
    #These cards are all money cards, ie they simply give or take away money to the player.
        {"cardMessage": "Pay poor tax of $15", "cardType":"money", "moneyChange": -15},
        {"cardMessage": "Bank pays you dividend of $50", "cardType":"money", "moneyChange": 50},
        {"cardMessage": "Your building and loan matures. Collect $150", "cardType":"money", "moneyChange": 150},
    #These cards determine what money goes where by either using the players or by using houses and hotels.
        {"cardMessage": "Make general repairs on all your property. For each house, pay $25; for each hotel, $100", "cardType": "housesAndHotels", "moneyChange": [25,100]},
        {"cardMessage": "You have been elected Chairman of the Board. Pay each player #50", "cardType": "getFromEachPlayer", "moneyChange": -50},
    #These cards are all movement-related. The card specifies a specific space on the board to go to.
        {"cardMessage": "Advance to go! Collect $200", "cardType":"moveTo", "movement":0},
        {"cardMessage": "Go directly to jail. Do not pass go, do not collect $200", "cardType":"moveTo", "movement":10},
        {"cardMessage": "Take a walk on the Boardwalk. Advance token to Boardwalk", "cardType":"moveTo", "movement":39},
        {"cardMessage": "Advance to St. Charles Place. If you pass Go, collect $200", "cardType":"moveTo", "movement":11},
        {"cardMessage": "Advance to Illinois Ave.", "cardType":"moveTo", "movement":24},
        {"cardMessage": "Take a ride on the Reading. If you pass Go, collect $200", "cardType":"moveTo", "movement":5},
    #These cards are all movement-related, but they have special mechanics associated with them.
        {"cardMessage": "Advance token to nearest utility. If unowned, you may buy it from bank. If owned, throw dice and pay owner a total ten times the amount thrown.",
            "cardType":"moveToNearest", "movement":"nearestUtility"},
        {"cardMessage": "Advance token to the nearest Railroad and pay owner Twice the Rental to which he is otherwise entitled.\nIf Railroad is unowned, you may buy it from the bank.",
            "cardType":"moveToNearest", "movement":"nearestRailroad"},
    #In the original game, these cards are kept by the player upon drawing it, but for our purposes they won't be.
        {"cardMessage": "Get out of jail free! This card may be kept until needed, or sold.", "cardType":"getOutOfJailFree"},
    
    ]
chest_cards = [
    #These cards are all money cards, ie they simply give or take away money to the player.
        {"cardMessage": "You have won second prize in a beauty contest. Collect $10", "cardType":"money", "moneyChange": 10},
        {"cardMessage": "You inherit $100", "cardType":"money", "moneyChange": 100},
        {"cardMessage": "Receive for services - $25", "cardType":"money", "moneyChange": 25},
        {"cardMessage": "Pay school tax of $150", "cardType":"money", "moneyChange": -150},
        {"cardMessage": "Pay hospital $100", "cardType":"money", "moneyChange": -100},
        {"cardMessage": "Life insurance matures. Collect $100", "cardType":"money", "moneyChange": 100},
        {"cardMessage": "Income tax refund. Collect $20", "cardType":"money", "moneyChange": 20},
        {"cardMessage": "Xmas fund matures. Collect $100", "cardType":"money", "moneyChange": 100},
        {"cardMessage": "From sale of stock you get $45", "cardType":"money", "moneyChange": 45},
        {"cardMessage": "Doctor's fee. Pay $50", "cardType":"money", "moneyChange": -50},
        {"cardMessage": "Bank error in your favor. Collect $200", "cardType":"money", "moneyChange": 200},
    #These cards determine what money goes where by either using the players or by using houses and hotels.
        {"cardMessage": "Grand Opera Opening. Collect $50 from each player", "cardType": "getFromEachPlayer", "moneyChange": 50},
        {"cardMessage": "You are assessed for street repairs. $40 per house, $115 per hotel", "cardType": "housesAndHotels", "moneyChange": [40,115]},
    #These cards are all movement-related. The card specifies a specific place to go.
        {"cardMessage": "Advance to go! Collect $200", "cardType":"moveTo", "movement":0},
    #These cards are all movement-related as well, but they specify a number of spaces to travel by.
        {"cardMessage": "Go back 3 spaces", "cardType":"moveBy", "movement":-3},
    #In the original game, these cards are kept by the player upon drawing it, but for our purposes they won't be.
        {"cardMessage": "Get out of jail free! This card may be kept until needed, or sold.", "cardType":"getOutOfJailFree"}
    ]
def chance_space(person):
    card = random.choice(chance_cards)
    do_the_card(person, **card)
def chest_space(person):
    card = random.choice(chest_cards)
    do_the_card(person, **card)
def do_the_card(person, cardMessage, cardType, movement=0, moneyChange=0, skipGo=False): #Function is run when a person 'draws a card'
    print("You drew the card: '{message}'!".format(message=cardMessage))
    if cardType == "money":
        print(moneyChange)
        person.money += moneyChange
    elif cardType == "moveTo":
        if movement == 10: #If it's a 'go to jail' card
            goToJail(person)
        else:
            person.moveLinear(movement - person.location)
    elif cardType == "getFromEachPlayer":
        for p in playerList:
            if p is not person:
                if moneyChange > 0:
                    print("You, {p}, must give {name} {amt}.".format(p=p.name, name=person.name, amt=moneyChange))
                else:
                    print("You, {name}, must give {p} {amt}.".format(p=p.name, name=person.name, amt=moneyChange))
                p.money -= moneyChange
                person.money += moneyChange
    elif cardType == "housesAndHotels":
        houseCharge = moneyChange[0]
        hotelCharge = moneyChange[1]
        print("You must pay {houseCharge} for each house you own, and {hotelCharge} for each hotel you own.".format(houseCharge=houseCharge, hotelCharge=hotelCharge))
        houseNum = 0
        hotelNum = 0
        for prop in person.properties:
            print(prop.name)
            print("adding {0} houses".format(prop.houses))
            houseNum += prop.houses
            print("adding {0} houses".format(prop.hotels))
            hotelNum += prop.hotels
        totalCost = houseNum * houseCharge + hotelNum * hotelCharge
        print("Because you have {0} houses and {1} hotels, you must pay {2}.".format(houseNum, hotelNum, totalCost))
        person.money -= totalCost
    elif cardType == "getOutOfJailFree":
        person.getOutOfJailFreeCards += 1
        print("You now have {0} get out of jail free cards.".format(person.getOutOfJailFreeCards))
    elif cardType == "moveToNearest":
        if movement == "nearestUtility":
        #Finding the nearest utility space
        #The nearest utility will either be on space 12 (Electric Company) or 28 (Water Works)
        #Because the payment system is special, we will have to
            if person.location < 12 or person.location > 28:
                targetLocation = 12
            else:
                targetLocation = 28
        if movement == "nearestRailroad":
            targetLocation = 0
            railroadLocations = (5,15,25,35)
            for value in railroadLocations:
                if person.location < value:
                    targetLocation = value
                    break
            if targetLocation == 0:
                targetLocation = railroadLocations[0]
        print("targetLocation = " + str(targetLocation))
        person.moveLinear(targetLocation - person.location, nearestCard = True)
    elif cardType == "moveBy":
        person.moveLinear(person.location + movement)
    else:
        print("You seem to have hit a card that doesn't exist.")

#List of property, utility, and railroad objects in the game
props = [
    Property("Mediterranean Ave.", 60, [2,10,30,90,160,250],50, "brown"), # 0
    Property("Baltic Ave.", 60, [4,20,60,180,320,450],50, "brown"), # 1
    Railroad("Reading Railroad"), # 2
    Property("Oriental Ave.", 100, [6,30,90,270,400,550], 50, "light_blue"), # 3
    Property("Vermont Ave.", 100, [6,30,90,270,400,550], 50, "light_blue"), # 4
    Property("Connecticut Ave.", 120, [8,40,100,300,450,600], 50, "light_blue"), # 5
    Property("St. Charles Place", 140, [10,50,150,450,625,750], 100, "pink"), # 6
    Utility("Electric Company"), # 7
    Property("States Ave.", 140, [10,50,150,450,625,750], 100, "pink"), # 8
    Property("Virginia Ave.", 160, [12,60,180,500,700], 100, "pink"), # 9
    Railroad("Pennsylvania Railroad"), # 10
    Property("St. James Place", 180, [14,70,200,550,750,950], 100, "orange"), # 11
    Property("Tennessee Ave.", 180, [14,70,200,550,750,950], 100, "orange"), # 12
    Property("New York Ave.", 200, [16,80,220,600,800,1000], 100, "orange"), # 13
    Property("Kentucky Ave.", 220, [18,90,250,700,875,1050], 150, "red"), # 14
    Property("Indiana Ave.", 220, [18,90,250,700,875,1050], 150, "red"),# 15
    Property("Illinois Ave.", 240, [20,100,300,750,925,1100], 150, "red"), # 16
    Railroad("B. & O. Railroad"), # 17
    Property("Atlantic Ave.", 260, [22,110,330,800,975,1150], 150, "yellow"), # 18
    Property("Ventnor Ave.", 260, [22,110,330,800,975,1150], 150, "yellow"), # 19
    Utility("Water Works"), # 20
    Property("Marvin Gardens", 280, [24,120,360,850,1025,1200], 150, "yellow"), # 21
    Property("Pacific Ave.", 300, [26,130,390,900,1100,1275], 200, "green"), # 22
    Property("North Carolina Ave.", 300, [26,130,390,900,1100,1275], 200, "green"), # 23
    Property("Pennsylvania Ave.", 320, [28,150,450,1000,1200,1400], 200, "green"), # 24
    Railroad("Short Line"), # 25
    Property("Park Place", 350, [35,175,500,1100,1300,1500], 200, "blue"), # 26
    Property("Boardwalk", 400, [50,200,600,1400,1700,2000], 200, "blue") # 27
]
#Uses props list and other gameboard space functions to represent the board
gameBoardSpaces = [
    go_space, #0
    props[0], #Property Mediterranean Ave. #1
    chest_space, #2
    props[1], #Property Baltic Ave. #3
    income_tax_space, #4
    props[2], #Railroad Reading Railroad #5
    props[3], #Property Oriental Ave. #6
    chance_space, #7
    props[4], #Property Vermont Ave. #8
    props[5], #Property Connecticut Ave. #9
    jail_space, #10, the first corner of the board
    props[6], #Property St. Charles Place #11
    props[7], #Utility Electric Company #12
    props[8], #Property States Ave. #13
    props[9], #Property Virginia Ave. #14
    props[10], #Railroad Pennsylvania Railroad #15
    props[11], #Property St. James Place #16
    chest_space, #17
    props[12], #Property Tennessee Ave. #18
    props[13], #Property New York Ave. #19
    free_parking_space, #20, the second corner of the board
    props[14], #Property Kentucky Ave. #21
    chance_space, #22
    props[15], #Property Indiana Ave. #23
    props[16], #Property Illinois Ave. #24
    props[17], #Railroad B. & O. Railroad #25
    props[18], #Property Atlantic Ave. #26
    props[19], #Property Ventnor Ave. #27
    props[20], #Utility Water Works #28
    props[21], #Property Marvin Gardens #29
    go_to_jail_space, #30, the third corner of the board
    props[22], #Property Pacific Ave. #31
    props[23], #Property North Carolina Ave. #32
    chest_space, #33
    props[24], #Property Pennsylvania Ave. #34
    props[25], #Railroad Short Line #35
    chance_space, #36
    props[26], #Property Park Place #37
    luxury_tax_space, #38
    props[27], #Property Boardwalk #39
]

def getNamesInColorGroup(color):
    # This function is used to get a list of the names of the properties that have a certain color.
    # Ex. Using 'blue' would get ['Park Place', 'Boardwalk']
    onlyColoredSpaces = [f for f in props if isinstance(f, Property)] # Getting only the spaces that are properties, aka those that would have a color
    return [x.name for x in onlyColoredSpaces if x.color == color] # Out of the properties with color, get a list of those that have the specified color
    #These two statement can't be combined since you can't check the color of Railroads and Utilities since they have no color

#Board functions as the Bank.
Board = Entity(props)

def getPersonByName(name):
    #Gets the relevant Person object that has the given name
    for x in playerList:
        if x is not None:
            if x.name == name:
                return x
    return None
def setAllRentForPropertiesAndRailroads(props): #This function updates the rent for all properties and railroads in the game.
    for p in props:
        if isinstance(p, Railroad):
            p.setRent(props)
        elif isinstance(p, Property):
            p.setRent()

#This is a list of the players of the game. Ideally, playerList would be created as a result of an input from the user, but for now it is made up of 4 people.
playerList = [Person("Apple"),Person("Orange"), Person("Banana"), Person("Pineapple")]



def displayInventory(person):
    #UNFINISHED
    propsString = ""
    for i in range(len(person.properties)-1):
        propsString += person.properties[i].name + ","
    if len(person.properties) > 0:
        propsString += person.properties[-1]
    print(propsString)

def rollTwoDice():
    #This function returns a string with two random values from 1-6 and is the automated form of random dice-rolling for this game.
    results = [random.randrange(1,7),random.randrange(1,7)]
    return results

def inputWithHelpOption(string):
    #UNFINISHED
    if string.upper() == "HELP": #CHANGE
        pass
    else:
        pass

def doATurn(person):
    #This function gives a set of options for the player to do on their turn. Some options are unfinished or broken, but some work.
    options = ["ROLL", "BUILDING", "TRADE", "RULES", "DISPLAY BOARD", "DISPLAY INVENTORY", "NEXT"]
    while True:
        choice = input("Please type either {options}, or type HELP to enter the help menu. ".format(options=", ".join(options)))
        if choice.upper() in options:
            print("You chose {c}.".format(c=choice.upper()))
            if choice.upper() == "ROLL":
                if person.location == 10 and person.jailCountdown: #if the person is in jail
                        jail_space(person)
                else:
                    #User-entered dicerolling
                    #diceroll = input("{0}, what number did you roll?".format(person.name))
                    #Random dicerolling
                    diceroll = rollTwoDice()
                    #End random dicerolling
                    print("You rolled {0}.".format(" and ".join(str(x) for x in diceroll)))
                    person.moveLinear(diceroll)
                    person.doublesCounter = 0
                    options.remove("ROLL")
            elif choice.upper() == "BUILDING":
                while True:
                    propName = input("Please pick a property to place a building on, or type EXIT to not place any buildings.")
                    prop = person.getPropertyByName(propName)
                    if prop is not None and propName.upper() != "EXIT":
                        colorOfProp = prop.color
                        if person.hasMonopoly(colorOfProp):
                            print("Person has monopoly")
                            person.purchaseBuilding(propName)
                            break
                        else:
                            print("You can't place a building on a property if you don't have a Monopoly there.")
                    elif propName.upper() == "EXIT":
                        print("You chose EXIT.")
                        break
                    elif propName.upper() == "EXIT":
                        break
                    else:
                        print("You typed in a property that you cannot place buildings on, or you mispelled a property name. This input is case-sensitive. Type EXIT to exit.")
            elif choice.upper() == "TRADE":
                while True:
                    playerName = input("Please input a player's name that you would like to trade with.")
                    if not playerName in [player.name for player in playerList]:
                        print("You need to choose another one., or type EXIT to exit the trade.")
                        continue
                    elif playerName == "EXIT":
                        break
                    else:
                        player = getPersonByName(playerName)
                        displayInventory(player)
                        break
            elif choice.upper() == "RULES":
                print("Please read this pdf in your browswer to access the rules. http://www.mtholyoke.edu/~blerner/cs315/Monopoly/MonopolyRules.pdf")
            elif choice.upper() == "NEXT":
                if "ROLL" not in options:
                    return
                else:
                    print("You need to ROLL before you can pass your turn.")
        else:
            print("Please pick another option.")


gameStart = True
roundNum = 1
#The actual game loop
while gameStart:
    print("ROUND {0}".format(roundNum))
    for player in playerList:
        print("It's {0}'s turn.".format(player.name))
        setAllRentForPropertiesAndRailroads(props)
        doATurn(player)
    roundNum += 1