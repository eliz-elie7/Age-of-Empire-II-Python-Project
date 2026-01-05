class Map:
    def __init__(self, width, height):
        self.width=width #x
        self.height=height #y
        self.data = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    row.append("#")
                else:
                    row.append(".")
            self.data.append(row)
        

    #----- Dimensions -----
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height