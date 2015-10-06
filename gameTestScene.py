import sys

import pygame
from buffalo import utils
from buffalo.scene import Scene
from buffalo.label import Label

from chunk import Chunk
from camera import Camera
from mapManager import MapManager
from pluginManager import PluginManager
from inventoryUI import InventoryUI
from inventory import Inventory
from guiManager import GUIManager

from playerCharacter import PlayerCharacter

class GameTestScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.BACKGROUND_COLOR = (0, 0, 0, 255)
        PluginManager.loadPlugins()
        Camera.init()
        self.pc = PlayerCharacter(
            Inventory(),
            name="Tom",
            fPos=(float(utils.SCREEN_M[0]), float(utils.SCREEN_M[1])),
            size=(32, 64),
            speed=1.0,
            )
        self.labels.add(
            Label(
                (5,5),
                "Location",
                x_centered=True,
                y_centered=True,
            )
        )
        Camera.lock(self.pc)
        self.UIManager = GUIManager()
        self.UIManager.guiScreens.append(InventoryUI(self.pc.inventory, self.UIManager))
        self.UIManager.updateGUIs()


    def on_escape(self):
        sys.exit()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.pc.yv += -self.pc.speed
        if keys[pygame.K_s]:
            self.pc.yv += self.pc.speed
        if keys[pygame.K_d]:
            self.pc.xv += self.pc.speed
        if keys[pygame.K_a]:
            self.pc.xv += -self.pc.speed
        self.pc.update()
        self.UIManager.update()
        Camera.update()

    def blit(self):
        for row in range(MapManager.LC_HEIGHT):
            for col in range(MapManager.LC_WIDTH):
                x, y = col - MapManager.LC_WIDTH // 2, row - MapManager.LC_HEIGHT // 2
        Camera.blitView()
        self.UIManager.blit(utils.screen, (0,0))
        self.pc.blit(utils.screen)
