from typing import List, Any

import pygame
from pygame import *
import math
import random

global black
black = (0, 0, 0)
global white
white = (255, 255, 255)


class Display:
    def __init__(self, len, val, xp, yp, scr):
        self.nums = []
        self.l = len
        self.v = val
        self.x = xp
        self.y = yp
        self.val = 0
        self.s = scr
        for i in range(len):
            self.nums.append(SevenSeg(0, self.x + 30 * i, self.y, self.s))

    def updateVal(self, val):
        self.v = val;
        temp = val;
        for i in range(len(self.nums) - 1, -1, -1):
            self.nums[i].setVal(temp % 10)
            temp = (int)(temp / 10)

    def draw(self):
        for i in self.nums:
            i.draw()


class Fleet:
    j: list[list[Any]]

    def __init__(self, xp, yp, scr):
        self.j = [[], [], [], [], [], [], [], [], []]
        self.x = xp
        self.y = yp
        self.s = scr
        self.row = 8
        self.column = 4
        self.dir = 20
        self.shot = Bullet(800, 800, self.s, False)
        self.shooting = False
        for i in range(9):
            for j in range(5):
                self.j[i].append(Alien((self.x + i * 50), (self.y + j * 40), i, j))

    def draw(self):
        for i in self.j:
            for k in i:
                if k.isAlive():
                    k.draw(self.s)

    def getAlien(self, x, y):
        return self.j[x][y]

    def shoot(self, ship):
        if self.shooting:
            return
        target = ship.getPos()
        closest = 1000
        closesti = 1000
        for i in range(9):
            if abs(self.j[i][4].getX() - target) < closest:
                closest = abs(self.j[i][4].getX() - target)
                closesti = i
        closesti += random.randint(-1, 1)
        if closesti > 8:
            closesti = 8
        elif closesti < 0:
            closesti = 0
        noShips = True
        lowest = -1
        for i in range(4, -1, -1):
            if self.j[closesti][i].isAlive():
                noShips = False
                lowest = i
                break
        if noShips:
            return
        else:
            self.shot = Bullet(self.j[closesti][lowest].getX() + 12, self.j[closesti][lowest].getY(), self.s, False);
            self.shooting = True

    def updateShot(self):
        if self.shooting:
            self.shot.updateShot()
            if self.shot.getHeight() > 480:
                self.shooting = False
                self.shot.setPos(800, 800)

    def unAliveShip(self, z):
        x = (int)(z / 5)
        y = z % 5
        self.j[x][y].kill()

    def shipsLeft(self):
        x = 0
        for i in self.j:
            for k in i:
                if k.isAlive():
                    x += 1
        return x

    def isAlive(self):
        alive = False
        for i in self.j:
            for k in i:
                if k.isAlive():
                    alive = True
                    break
            if alive:
                break
        return alive

    def move(self):
        low = False
        for i in self.j:
            for k in i:
                if k.descendCheck() and k.isAlive():
                    low = True
                    k.stopLower()
        if low:
            self.flip()
            for i in self.j:
                for k in i:
                    k.lower(50)
        else:
            for i in self.j:
                for k in i:
                    k.move(self.dir)

    def flip(self):
        self.dir *= -1

    def lower(self):
        for i in self.j:
            for k in i:
                k.lower(50)
                k.stopLower()
                if k.isInvaded():
                    self.invaded = True

    def checkInvaded(self):
        for i in self.j:
            for k in i:
                if k.isInvaded() and k.isAlive():
                    return True
        return False


class Alien:
    def __init__(self, xp, yp, x1, y1):
        self.x = xp
        self.y = yp
        self.xc = x1
        self.yc = y1
        self.alive = True
        self.descend = False
        self.invaded = False

    def stopLower(self):
        self.descend = False

    def descendCheck(self):
        return self.descend

    def draw(self, scr):
        pygame.draw.rect(scr, white, (self.x, self.y, 25, 25))

    def isAlive(self):
        return self.alive

    def getXc(self):
        return self.xc

    def getYc(self):
        return self.yc

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def kill(self):
        self.alive = False

    def move(self, dir):
        self.x += dir
        if dir > 0:
            if self.x + 25 >= 625:
                self.descend = True
        else:
            if self.x <= 15:
                self.descend = True

    def lower(self, dir):
        self.y += dir
        if self.y >= 420:
            self.invaded = True

    def isInvaded(self):
        return self.invaded


class Bullet:
    def __init__(self, xp, yp, scr, sh):
        self.x = xp
        self.y = yp
        self.s = scr
        self.ship = sh

    def draw(self):
        pygame.draw.rect(self.s, white, (self.x, self.y, 4, 10))

    def setPos(self, xp, yp):
        self.x = xp
        self.y = yp

    def alienCollision(self, f):
        c = -1
        for i in range(9):
            for k in range(5):
                if self.x + 2 < f.j[i][k].getX() + 25 and self.x + 2 > f.j[i][k].getX() and self.y > f.j[i][
                    k].getY() and self.y < f.j[i][k].getY() + 25 and f.j[i][k].isAlive():
                    self.setPos(800, 800)
                    return (i * 5) + k
        return -1

    def shipCollision(self, ship):
        if self.x + 2 > ship.getPos() - 20 and self.x + 2 < ship.getPos() + 20 and self.y + 10 > ship.getHeight() and self.y + 10 < ship.getHeight() + 10:
            self.setPos(800, 800)
            return True
        return False

    def updateShot(self):
        if self.ship:
            self.y -= 5
        else:
            self.y += 3

    def getHeight(self):
        return self.y


class Ship:
    def __init__(self, xp, yp, scr):
        self.lives = 3
        self.x = xp
        self.y = yp
        self.s = scr
        self.bul = Bullet(800, 800, self.s, True)
        self.shooting = False

    def move(self, m):
        if self.x + m > 600:
            self.x = 600
        if self.x + m < 40:
            self.x = 40
        else:
            self.x += m

    def draw(self):
        pygame.draw.rect(self.s, white, (self.x - 20, self.y, 40, 10))
        pygame.draw.rect(self.s, white, (self.x - 15, self.y - 5, 30, 5))
        pygame.draw.rect(self.s, white, (self.x - 2, self.y - 10, 4, 10))

    def setPos(self, x1):
        self.x = x1

    def getPos(self):
        return self.x

    def getHeight(self):
        return self.y

    def endShot(self):
        self.shooting = False

    def shoot(self):
        if not self.shooting:
            self.shooting = True
            self.bul.setPos(self.x - 2, self.y - 5)

    def checkShot(self, f):
        x = self.bul.alienCollision(f)
        if x != -1:
            f.unAliveShip(x)
            self.shooting = False
            self.bul.setPos(800, 800)
            return True
        return False

    def moveShot(self):
        if self.shooting:
            self.bul.updateShot()
            if self.bul.getHeight() < 0:
                self.shooting = False
                self.bul.setPos(800, 800)


class SevenSeg:
    def __init__(self, v, xPos, yPos, scr):
        self.data = []
        v = str(v)
        self.setVal(v)
        self.x = xPos
        self.y = yPos
        self.s = scr

    def setVal(self, val):
        val = str(val)
        if val == '1':
            self.data = [False, False, True, False, False, True, False]
        elif val == '2':
            self.data = [True, False, True, True, True, False, True]
        elif val == '3':
            self.data = [True, False, True, True, False, True, True]
        elif val == '4':
            self.data = [False, True, True, True, False, True, False]
        elif val == '5':
            self.data = [True, True, False, True, False, True, True]
        elif val == '6':
            self.data = [True, True, False, True, True, True, True]
        elif val == '7':
            self.data = [True, False, True, False, False, True, False]
        elif val == '8':
            self.data = [True, True, True, True, True, True, True]
        elif val == '9':
            self.data = [True, True, True, True, False, True, True]
        elif val == '0':
            self.data = [True, True, True, False, True, True, True]

    def draw(self):
        if self.data[0]:
            pygame.draw.rect(self.s, white, (self.x, self.y, 20, 3))
        if self.data[1]:
            pygame.draw.rect(self.s, white, (self.x, self.y, 3, 14))
        if self.data[2]:
            pygame.draw.rect(self.s, white, (self.x + 17, self.y, 3, 14))
        if self.data[3]:
            pygame.draw.rect(self.s, white, (self.x, self.y + 11, 20, 3))
        if self.data[4]:
            pygame.draw.rect(self.s, white, (self.x, self.y + 12, 3, 15))
        if self.data[5]:
            pygame.draw.rect(self.s, white, (self.x + 17, self.y + 12, 3, 15))
        if self.data[6]:
            pygame.draw.rect(self.s, white, (self.x, self.y + 24, 20, 3))


def main():
    pygame.init()
    screen = pygame.display.set_mode([640, 480])
    running = True
    gameLoop = True
    clock = pygame.time.Clock()
    while running:
        idle = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        while idle:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    idle = False
                    gameLoop = False
            screen.fill(black)
            pygame.draw.rect(screen, white, (0, 40, 640, 5))
            pygame.display.update()
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_RETURN]:
                idle = False
        player = Ship(320, 440, screen)
        level = Fleet(105, 70, screen)
        stage = 0
        stageEnd = True
        score = 0
        moveClock = 0
        lives = 3
        extraLife = 100
        gameIdle = True
        global descend
        descend = False
        scoreDisplay = Display(4, 0, 5, 5, screen)
        livesDisplay = Display(1, 3, 600, 5, screen)
        while gameIdle:
            if lives == 0:
                gameLoop = False
                gameIdle = False
                running = False
                idle = False
            else:
                gameLoop = True
            if stageEnd:
                stage += 1
                tempY = 20 + 50 * stage
                if tempY > 220:
                    tempY = 220
                level = Fleet(105, tempY, screen)
                stageEnd = False
            screen.fill(black)
            pygame.draw.rect(screen, white, (0, 40, 640, 5))
            level.draw()
            scoreDisplay.draw()
            livesDisplay.updateVal(lives)
            livesDisplay.draw()
            pygame.time.delay(3000)
            while gameLoop:
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        idle = False
                        gameLoop = False
                        gameIdle = False
                screen.fill(black)
                pygame.draw.rect(screen, white, (0, 40, 640, 5))
                pressed_keys = pygame.key.get_pressed()
                if pressed_keys[K_LEFT]:
                    player.move(-2)
                if pressed_keys[K_RIGHT]:
                    player.move(2)
                if pressed_keys[K_z]:
                    player.shoot()
                if random.randint(1, 100) == 42:
                    level.shoot(player)
                level.updateShot()
                player.moveShot()
                if player.checkShot(level):
                    score += 1
                level.shot.draw()
                player.draw()
                player.bul.draw()
                scoreDisplay.draw()
                livesDisplay.draw()
                if score >= extraLife:
                    lives += 1
                    extraLife += 100
                if level.shot.shipCollision(player):
                    gameLoop = False
                    lives -= 1
                    livesDisplay.updateVal(lives)
                    screen.fill(black)
                    level.draw()
                    pygame.draw.rect(screen, white, (0, 40, 640, 5))
                    scoreDisplay.updateVal(score)
                    scoreDisplay.draw()
                    livesDisplay.draw()
                    player.setPos(320)
                if level.checkInvaded():
                    lives = 0
                    gameLoop = False
                    screen.fill(black)
                    level.draw()
                    pygame.draw.rect(screen, white, (0, 40, 640, 5))
                    scoreDisplay.updateVal(score)
                    scoreDisplay.draw()
                    livesDisplay.draw()
                if level.shipsLeft() > 0:
                    speed = (int)((10 * math.log2(level.shipsLeft())) + 2)
                else:
                    speed = 1
                    stageEnd = True
                    score += 5
                    gameLoop = False
                    screen.fill(black)
                if moveClock >= speed:
                    level.move()
                    moveClock = 0
                else:
                    moveClock += 1
                level.draw()
                scoreDisplay.updateVal(score)
                livesDisplay.updateVal(lives)
                scoreDisplay.draw()
                pygame.display.update()
    if score < 20:
        print('You lost, waaaaaaah')


main()
pygame.quit()
