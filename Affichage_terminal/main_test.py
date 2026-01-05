from Terminal import Terminal
from map import Map

game_map = Map(100, 100)

term = Terminal(game_map)
term.run()