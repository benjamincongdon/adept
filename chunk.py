import os.path

import pygame

from buffalo import utils

from mapManager import MapManager

"""
A Chunk is a data structure
that holds tiles.
"""
class Chunk:

    """
    CHUNK_HEIGHT and CHUNK_WIDTH represent
    the size, in tiles, of each Chunk
    """
    CHUNK_HEIGHT, CHUNK_WIDTH = 32, 32
    TILE_SIZE                 = 32     # TILE_SIZE represents the tile size, in pixels, when
                                       # Camera.zoom = 1.0

    def __init__(self, x, y):
        """
        This is the Chunk constructor.
        It creates a Chunk at the coordinates (<x>, <y>).
        <x> and <y> are positive or negative integers.

        self.pos  - a 2-tuple that stores the coordinates of the Chunk
        self.defs - a dictionary that stores definitions of tiles
                    self.defs' keys are specified in the file.
                    Each key maps to an RGBA 4-tuple, for now, at least.
        self.data - a two-dimensional array of strings
                    Each string is a key, which, when plugged into the
                    dictionary self.defs, returns an RGBA 4-tuple
        """
        self.path = None
        search_string = "{0},{1}.chunk".format(x, y)
        for m in MapManager.maps:
            if search_string in m.chunk_files:
                self.path = os.path.join(*list(m.path + [search_string]))
                break
        self.pos = x,y
        self.defs = dict()
        self.data = [["" for x in range(Chunk.CHUNK_WIDTH)] for y in range(Chunk.CHUNK_HEIGHT)]
        self.surface = utils.empty_surface(
            (Chunk.TILE_SIZE * Chunk.CHUNK_WIDTH, Chunk.TILE_SIZE * Chunk.CHUNK_HEIGHT)
        )
        self.fromFile(x,y)
        self.render()

    def fromFile(self,x,y):
        """
        This method loads a chunk from a file.
        The chunk is specified by coordinates, <x> and <y>,
        which are positive or negative integers.
        """

        if self.path is None:
            return
        
        # Be sure the URL points to a file before trying to open it
        if not os.path.isfile(self.path):
            print("Could not load chunk in path '" + self.path + "'.")
            return

        with open(self.path,"r") as chunkFile:
            # Keep track of which row of data we want to fill
            row = 0

            for line in chunkFile:
                stripped = line.strip()
                # If the line isn't blank
                if stripped:
                    splitted = stripped.split()
                    if len(splitted) >= 4 and splitted[0] == "define": # If the definition is formatted correctly

                        # Then assign map the value to the specified key in self.defs
                        # This is an RGBA 4-tuple
                        self.defs[splitted[1]] = (
                            int("0x"+splitted[3][1:3],16), # R
                            int("0x"+splitted[3][3:5],16), # G
                            int("0x"+splitted[3][5:7],16), # B
                            255,                           # A = 255 = fully opaque
                        )
                        # This is RGBA and not RGB because Buffalo is written to handle transparency
                        # Pygame suffers huge performance losses when converting between RGB and RGBA
                        # surface types. If everything is RGBA then Pygame never has to convert surface
                        # types and thus does not suffer from these performance losses.

                    else: # If we aren't looking at a correctly formatted definition

                        # Then interprate the line as chunk data
                        for col, key in enumerate(splitted):
                            if col < Chunk.CHUNK_WIDTH and row < Chunk.CHUNK_HEIGHT:
                                self.data[row][col] = key

                        row += 1 # And remember to keep track of the row!

    def render(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):
                if col in self.defs.keys():
                    self.surface.fill(
                        self.defs[col],
                        pygame.Rect(
                            (x * Chunk.TILE_SIZE, y * Chunk.TILE_SIZE),
                            (Chunk.TILE_SIZE, Chunk.TILE_SIZE),
                        )
                    )

    def blit(self, dest, pos):
        dest.blit( self.surface, pos )

    def toFile(self):
        # TODO
        # UPDATE THIS METHOD
        # USE self.path AND OTHER STUFF
        """
        This method saves a chunk to a file.
        This should only be called when a map has been updated at runtime,
        as the function overwrites previous chunk data.
        """

        # Create a URL that's dependent on platform
        url = os.path.join("chunks", str(self.pos[0]) + "," + str(self.pos[1]) + ".chunk")

        #Opens file in overwrite / file creation mode
        with open(url,"w+") as chunkFile:
            #Iterate through the tile definition dictionary
            for key, value in self.defs.items():
                #Start the definition line with the keyword and key
                chunkFile.write("define " + str(key) + " as #")

                #Reassemble the RGB integers to hex strings
                #IMPORTANT: Skipping last element because transparency is not currently saved
                for i in range(0,3):
                    RGBString = hex(value[i])[2:]
                    #Appending 0 to hex values less than 0x10 to maintain 2-character length per RGB
                    if(len(RGBString) < 2):
                        RGBString = "0" + RGBString
                    chunkFile.write(str(RGBString))
                chunkFile.write("\n") #New line after each definition

            #Iterate through the 2-dimensional list containing chunk data
            for row in self.data:
                for col in row:
                    #At each data point: write data, add white space
                    chunkFile.write(str(col) + " ")
                chunkFile.write("\n") #New line at end of each row