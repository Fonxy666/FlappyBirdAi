# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pygame
import neat
import time
import os
import random

WIN_WIDTH = 550
WIN_HEIGHT = 700
FPS = 30

score = 0
generation = 0
population = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans",40)

sBirdPath1 = os.path.join("img", "bird1.png")
sBirdPath2 = os.path.join("img", "bird2.png")
sBirdPath3 = os.path.join("img", "bird3.png")
sBasePath = os.path.join("img", "base.png")
sBgPath = os.path.join("img", "bg.png")
sPipePath = os.path.join("img", "pipe.png")

screen_size = (WIN_WIDTH, WIN_HEIGHT)

BIND_IMGS = [pygame.transform.scale(pygame.load(sBirdPath1)),
             pygame.transform.scale(pygame.load(sBirdPath2)),
             pygame.transform.scale(pygame.load(sBirdPath3))]

