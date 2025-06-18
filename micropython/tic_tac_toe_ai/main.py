import time
import machine, neopixel

WIDTH = 3
HEIGHT = 3

COLOR_NONE = 0
COLOR_RED = 1
COLOR_GREEN = 2
COLOR_BLUE = 3
COLOR_RED_REMOVE = 4
COLOR_GREEN_REMOVE = 5

COLOR_PLAYER1 = COLOR_RED
COLOR_PLAYER1_REMOVE = COLOR_RED_REMOVE
COLOR_PLAYER2 = COLOR_GREEN
COLOR_PLAYER2_REMOVE = COLOR_GREEN_REMOVE

KEY_DOWN_TIME = 0.05
    

class Screen:

    PROCESS_BLINK_PLAYER = 0
    PROCESS_BLINK_REMOVE = 1

    def __init__(self):
        self.__processesEnabled = [False, False]
        self.__processVariables = [None, None]
        self.__lastTimes = [0, 0]
        self.__lastStates = [0, 0]
        self.__np = neopixel.NeoPixel(machine.Pin(0), 9)
        self.__npPlayer = neopixel.NeoPixel(machine.Pin(1), 2)
        self.__colors = []
        for i in range(WIDTH * HEIGHT):
            self.__colors.append(COLOR_NONE)
        self.clear()
        self.update()
        self.setPlayer(False, False)
                
    def clear(self):
        for i in range(WIDTH * HEIGHT):
                self.__colors[i] = COLOR_NONE
        
    def update(self):
        for i in range(WIDTH * HEIGHT):
                self.__np[i] = self.__colorToRGB(self.__colors[i])
        self.__np.write()
        
    def setColor(self, x : int, y : int, color : int):
        self.__colors[x + y * WIDTH] = color
        
    def setPlayer(self, player1, player2):
        if player1:
            self.__npPlayer[0] = self.__colorToRGB(COLOR_PLAYER1)
        else:
            self.__npPlayer[0] = self.__colorToRGB(COLOR_NONE)
        if player2:
            self.__npPlayer[1] = self.__colorToRGB(COLOR_PLAYER2)
        else:
            self.__npPlayer[1] = self.__colorToRGB(COLOR_NONE)
        self.__npPlayer.write()

    def blinkScreen(self):
        colors = self.__colors.copy()
        for i in range(20):
            for i in range(len(self.__colors)):
                self.__colors[i] = COLOR_NONE
            screen.update()
            time.sleep(0.05)
            self.__colors = colors.copy()
            screen.update()
            time.sleep(0.05)

    def gameStop(self):
        self.clear()
        for i in range(WIDTH * HEIGHT):
            if i < 3:
                index = i
            elif i == 3:
                index = 5
            elif i < 7:
                index = 8 - i + 4
            elif i == 7:
                index = 3
            else:
                index = 4
            for ii in range(255 / 16):
                self.__np[index]= (0, 0, ii * 16)
                self.__np.write()
                time.sleep(0.01)

    def gameStart(self):
        self.clear()
        for ii in range(255 // 16, -1, -1):
            for i in range(WIDTH * HEIGHT):
                self.__np[i]= (0, 0, ii * 16)
            self.__np.write()
            time.sleep(0.01)

    def disableProcess(self, process):
        self.__processesEnabled[process] = False

    def enableProcess(self, process, variable):
        self.__processesEnabled[process] = True
        self.__processVariables[process] = variable
        self.__lastStates[process] = 0
        self.__lastTimes[process] = 0

    def process(self):
        t = time.ticks_ms()
        if self.__processesEnabled[Screen.PROCESS_BLINK_PLAYER]:
            if t - self.__lastTimes[Screen.PROCESS_BLINK_PLAYER] > 250:
                self.__lastTimes[Screen.PROCESS_BLINK_PLAYER] = t
                if self.__lastStates[Screen.PROCESS_BLINK_PLAYER] == 1:
                    self.setPlayer(self.__processVariables[Screen.PROCESS_BLINK_PLAYER] == 0, self.__processVariables[Screen.PROCESS_BLINK_PLAYER] == 1)
                    self.__lastStates[Screen.PROCESS_BLINK_PLAYER] = 0
                else:
                    self.setPlayer(False, False)
                    self.__lastStates[Screen.PROCESS_BLINK_PLAYER] = 1
        if self.__processesEnabled[Screen.PROCESS_BLINK_REMOVE]:
            if self.__lastStates[Screen.PROCESS_BLINK_REMOVE] == 0:
                for i in range(WIDTH * HEIGHT):
                    if self.__colors[i] == COLOR_PLAYER1_REMOVE:
                        self.__processVariables[Screen.PROCESS_BLINK_REMOVE] = (i, 0)
                        self.__lastStates[Screen.PROCESS_BLINK_REMOVE] = 1
                    elif self.__colors[i] == COLOR_PLAYER2_REMOVE:
                        self.__processVariables[Screen.PROCESS_BLINK_REMOVE] = (i, 1)
                        self.__lastStates[Screen.PROCESS_BLINK_REMOVE] = 1
            elif self.__lastStates[Screen.PROCESS_BLINK_REMOVE] == 1:
                if t - self.__lastTimes[Screen.PROCESS_BLINK_REMOVE] > 250:
                    color = COLOR_PLAYER1
                    if self.__processVariables[Screen.PROCESS_BLINK_REMOVE][1] == 1:
                        color = COLOR_PLAYER2
                    self.__colors[self.__processVariables[Screen.PROCESS_BLINK_REMOVE][0]] = color
                    self.update()
                    self.__lastStates[Screen.PROCESS_BLINK_REMOVE] = 2
            elif self.__lastStates[Screen.PROCESS_BLINK_REMOVE] == 2:
                if t - self.__lastTimes[Screen.PROCESS_BLINK_REMOVE] > 250:
                    color = COLOR_PLAYER1_REMOVE
                    if self.__processVariables[Screen.PROCESS_BLINK_REMOVE][1] == 1:
                        color = COLOR_PLAYER2_REMOVE
                    self.__colors[self.__processVariables[Screen.PROCESS_BLINK_REMOVE][0]] = color
                    self.update()
                    self.__lastStates[Screen.PROCESS_BLINK_REMOVE] = 1

    def __colorToRGB(self, color : int):
        if color == COLOR_NONE:
            return (0, 0, 0)
        if color == COLOR_RED:
            return (0, 255, 0)
        if color == COLOR_GREEN:
            return (255, 0, 0)
        if color == COLOR_BLUE:
            return (0, 0, 255)
        if color == COLOR_RED_REMOVE:
            return (0, 20, 0)
        if color == COLOR_GREEN_REMOVE:
            return (20, 0, 0)
        return (0, 0, 0)
    
class Keyboard:
    
    def __init__(self):
        self.__pinRows = []
        self.__pinRows.append(machine.Pin(8, machine.Pin.OUT))
        self.__pinRows.append(machine.Pin(9, machine.Pin.OUT))
        self.__pinRows.append(machine.Pin(10, machine.Pin.OUT))
        for y in range(HEIGHT):
            self.__pinRows[y].high()
        self.__pinCols = []
        self.__pinCols.append(machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP))
        self.__pinCols.append(machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP))
        self.__pinCols.append(machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP))
        self.__player1Key = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
        self.__player2Key = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
        self.__player1KeyDownTimestamp = 0
        self.__player2KeyDownTimestamp = 0
        self.__player1KeyDown = False
        self.__player2KeyDown = False
        
    def getKeyPressed(self):
        for y in range(HEIGHT):
            self.__pinRows[y].low()
            time.sleep(0.02)
            for x in range(WIDTH):
                if self.__pinCols[x].value() == 0:
                    self.__pinRows[y].high()
                    return x, y
            self.__pinRows[y].high()
            time.sleep(0.02)
        return -1, -1
    
    def getPlayerKeyPressed(self):
        t = time.ticks_ms()
        if self.__player1Key.value() == 0:
            if (t - self.__player1KeyDownTimestamp > 0.2) and not self.__player1KeyDown:
                self.__player1KeyDownTimestamp = t
                self.__player1KeyDown = True
                return 0
        else:
            self.__player1KeyDownTimestamp = 0
            self.__player1KeyDown = False
        if self.__player2Key.value() == 0:
            if (t - self.__player2KeyDownTimestamp > 0.2) and not self.__player2KeyDown:
                self.__player2KeyDownTimestamp = t
                self.__player2KeyDown = True
                return 1
        else:
            self.__player2KeyDownTimestamp = 0
            self.__player2KeyDown = False
        return -1
    
class Sound:
    
    def __init__(self):
        self.__pwm = machine.PWM(machine.Pin(15), duty_u16=0)
        self.__pwm.init(freq=2000, duty_u16=0)
        
    def playMove(self, player):
        if player == 0:
            self.__pwm.freq(2500)
        else:
            self.__pwm.freq(3000)
        self.__pwm.duty_u16(32768)
        time.sleep(0.1)
        self.__pwm.duty_u16(0)

    def playSelect(self):
        self.__pwm.freq(2500)
        self.__pwm.duty_u16(32768)
        time.sleep(0.08)
        self.__pwm.freq(3000)
        self.__pwm.duty_u16(32768)
        time.sleep(0.08)
        self.__pwm.duty_u16(0)      

    def playBadMove(self):
        self.__pwm.freq(500)
        for i in range(20):
            self.__pwm.duty_u16(32768)
            time.sleep(0.01)
            self.__pwm.duty_u16(0)
            time.sleep(0.01)

class Game:
    
    HISTORY_SIZE = 7
    MAX_AI_DEPTH = 4

    def __init__(self, screen):
        self.__screen = screen
        self.__playerColors = []
        self.__playerColors.append(COLOR_RED)
        self.__playerColors.append(COLOR_GREEN)
        self.__playground = []
        self.__history = []
        self.clear()
        
    def clear(self):
        self.__playground.clear()
        for i in range(WIDTH * HEIGHT):
            self.__playground.append(-1)
        self.__history.clear()
        self.__screen.clear()
        self.__screen.update()
                
    def getPlayer(self, x, y):
        return self.__getPlayer(x, y, self.__playground)
                
    def getWinner(self):
        winner, kind = self.__getWin(self.__playground)
        return winner
    
    def isPlaygroundFull(self):
        return -1 not in self.__playground
        
    def blinkWinner(self):
        winner, kind = self.__getWin(self.__playground)
        for i in range(20):
            self.__setWinColor(kind, 0)
            time.sleep(0.05)
            self.__setWinColor(kind, self.__playerColors[winner])
            time.sleep(0.05)

    def putPlayer(self, x, y, player):
        self.__putPlayer(y * WIDTH + x, player, self.__playground, self.__history)
        self.__screen.setColor(x, y, self.__playerColors[player])
        self.__screen.update()
        
    def checkHistory(self):
        if len(self.__history) >= Game.HISTORY_SIZE:
            x = self.__history[0][1] % WIDTH
            y = self.__history[0][1] // WIDTH
            player = self.__history[0][0]
            self.__playground[y * WIDTH + x] = -1
            self.__history.pop(0)        
            for i in range(5):
                self.__screen.setColor(x, y, COLOR_NONE)
                self.__screen.update()
                time.sleep(0.05)
                self.__screen.setColor(x, y, self.__playerColors[player])
                self.__screen.update()
                time.sleep(0.05)
            self.__screen.setColor(x, y, COLOR_NONE)
            self.__screen.update()
        if len(self.__history) == Game.HISTORY_SIZE - 1:
            x = self.__history[0][1] % WIDTH
            y = self.__history[0][1] // WIDTH
            player = self.__history[0][0]
            color = COLOR_PLAYER1_REMOVE
            if player == 1:
                color = COLOR_PLAYER2_REMOVE
            self.__screen.setColor(x, y, color)
            self.__screen.update()

    def getBestMove(self, player):
        bestScore = float("-inf")
        bestMove = None
        playground = self.__playground.copy()
        history = self.__history.copy()

        moves = self.__availableMoves(playground)
        if len(moves) >= 7:
            maxDepth = 3
        else:
            maxDepth = Game.MAX_AI_DEPTH

        for move in self.__availableMoves(playground):
            # Make a calculating move
            playground[move] = player
            history.append((player, move))
            # Recursively call minimax with the next depth and the minimizing player
            score = self.__minimax(player, 0, maxDepth, False, playground.copy(), history.copy())
            # Reset the move
            playground[move] = -1
            history.pop()

            # Update the best score
            if score > bestScore:
                bestScore = score
                bestMove = move
        print("Best move for player {}: {}".format(player, bestMove))
        return bestMove
    
    def __minimax(self, player, depth, maxDepth, isMaximizing, playground, history):
        winner, kind = self.__getWin(playground)
        self.__screen.process()
        if winner == player:
            return 1 + maxDepth - depth
        if winner != -1:
            return -1 - maxDepth + depth
        if -1 not in playground:
            return 0
        
        if depth >= maxDepth:
            return 0

        if len(self.__history) >= Game.HISTORY_SIZE:
            index = self.__history[0][1]
            player = self.__history[0][0]
            playground[index] = -1
            history.pop(0)

        nextPlayer = player + 1
        if nextPlayer > 1:
            nextPlayer = 0

        # if it is the maximizing player's turn (AI), we want to maximize the score
        if isMaximizing:
            bestScore = float("-inf")
            for index in self.__availableMoves(playground):
                # Make a calculating move
                playground[index] = player
                history.append((player, index))
                # Recursively call minimax with the next depth and the minimizing player
                score = self.__minimax(player, depth + 1, maxDepth, False, playground.copy(), history.copy())
                # Reset the move
                playground[index] = -1
                history.pop()
                # Update the best score
                bestScore = max(score, bestScore)
            return bestScore
        else:
            # if it is the minimizing player's turn (human), we want to minimize the score
            bestScore = float("inf")
            for move in self.__availableMoves(playground):
                # Make a calculating move
                playground[move] = nextPlayer
                history.append((nextPlayer, move))
                # Recursively call minimax with the next depth and the maximizing player
                score = self.__minimax(player, depth + 1, maxDepth, True, playground.copy(), history.copy())
                # Reset the move
                playground[move] = -1
                history.pop()
                # Update the best score
                bestScore = min(score, bestScore)
            return bestScore
        
    def __availableMoves(self, playground):
        return [i for i, player in enumerate(playground) if player == -1]

    def __putPlayer(self, index, player, playground, history):
        history.append((player, index))
        playground[index] = player

    def __setWinColor(self, kind, color):
        if kind < 3:
            self.__screen.setColor(0, kind, color)
            self.__screen.setColor(1, kind, color)
            self.__screen.setColor(2, kind, color)
            self.__screen.update()
        elif kind < 6:
            self.__screen.setColor(kind - 3, 0, color)
            self.__screen.setColor(kind - 3, 1, color)
            self.__screen.setColor(kind - 3, 2, color)
            self.__screen.update()
        elif kind == 6:
            self.__screen.setColor(0, 0, color)
            self.__screen.setColor(1, 1, color)
            self.__screen.setColor(2, 2, color)
            self.__screen.update()
        elif kind == 7:
            self.__screen.setColor(0, 2, color)
            self.__screen.setColor(1, 1, color)
            self.__screen.setColor(2, 0, color)
            self.__screen.update()
        
    @staticmethod
    def __getPlayer(x, y, playground):
        return playground[y * WIDTH + x]
            
    def __getWin(self, playground):
        for y in range(HEIGHT):
            p = self.__getPlayer(0, y, playground)
            if (p != -1) and (p == self.__getPlayer(1, y, playground)) and (p == self.__getPlayer(2, y, playground)):
                return p, y
        for x in range(WIDTH):
            p = self.__getPlayer(x, 0, playground)
            if (p != -1) and (p == self.__getPlayer(x, 1, playground)) and (p == self.__getPlayer(x, 2, playground)):
                return p, 3 + x
        p = self.__getPlayer(0, 0, playground)
        if (p != -1) and (p == self.__getPlayer(1, 1, playground)) and (p == self.__getPlayer(2, 2, playground)):
            return p, 6
        p = self.__getPlayer(0, 2, playground)
        if (p != -1) and (p == self.__getPlayer(1, 1, playground)) and (p == self.__getPlayer(2, 0, playground)):
            return p, 7
        return -1, -1
        
screen = Screen()
keyboard = Keyboard()
sound = Sound()
game = Game(screen)
screen.update()

player = 0
playerChanged = True

aiPlayer = -1
finished = False

screen.gameStop()

while True:

    screen.disableProcess(Screen.PROCESS_BLINK_PLAYER)
    screen.disableProcess(Screen.PROCESS_BLINK_REMOVE)
    screen.setPlayer(not aiPlayer == 0, not aiPlayer == 1)

    while True:
        x, y = keyboard.getKeyPressed()
        if (x != -1) and (y != -1):
            screen.setPlayer(False, False)
            screen.gameStart()
            break
        playerKey = keyboard.getPlayerKeyPressed()
        if playerKey == 0:
            if aiPlayer == -1:
                aiPlayer = 0
                screen.setPlayer(False, True)
            elif aiPlayer == 0:
                aiPlayer = -1
                screen.setPlayer(True, True)
            sound.playSelect()
        if playerKey == 1:
            if aiPlayer == -1:
                aiPlayer = 1
                screen.setPlayer(True, False)
            elif aiPlayer == 1:
                aiPlayer = -1
                screen.setPlayer(True, True)
            sound.playSelect()

    game.clear()
    player = 0
    finished = False
    playerChanged = True

    while not finished:
        screen.process()

        if playerChanged:
            screen.setPlayer(player == 0, player == 1)
            if player == aiPlayer:
                screen.enableProcess(Screen.PROCESS_BLINK_PLAYER, player)
            else:
                screen.disableProcess(Screen.PROCESS_BLINK_PLAYER)
            time.sleep(0.2)
            playerChanged = False

        processWinner = False
        if player == aiPlayer:
            t = time.ticks_ms()
            print("AI is thinking...")
            bestMove = game.getBestMove(player)
            while time.ticks_ms() - t < 2000:
                screen.process()
            if bestMove is not None:
                game.putPlayer(bestMove % WIDTH, bestMove // WIDTH, player)
                sound.playMove(player)
                processWinner = True
        playerKey = keyboard.getPlayerKeyPressed()
        if playerKey != -1:
            sound.playSelect()
            screen.gameStop()
            finished = True
        x, y = keyboard.getKeyPressed()
        if (x != -1) and (y != -1):
            if game.getPlayer(x, y) == -1:
                game.putPlayer(x, y, player)
                sound.playMove(player)
                processWinner = True
            else:
                sound.playBadMove()
        if processWinner:
            winner = game.getWinner()
            if winner != -1:
                print("Player {} wins".format(winner))
                game.blinkWinner()
                screen.gameStop()
                finished = True
            else:
                if game.isPlaygroundFull():
                    print("It's a tie!")
                    screen.blinkScreen()
                    screen.gameStop()
                    finished = True
                else:
                    screen.disableProcess(Screen.PROCESS_BLINK_REMOVE)
                    game.checkHistory()
                    screen.enableProcess(Screen.PROCESS_BLINK_REMOVE, 0)
                    player += 1
                    if player > 1:
                        player = 0
                    playerChanged = True
                