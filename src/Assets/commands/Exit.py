import sys
sys.path.append("..") 

from CommandInterface import CommandInterface  

class Exit(CommandInterface):
    def command(self):
        exit (0)
