import subprocess
import sys
sys.path.append("..") 

from CommandInterface import CommandInterface  

class Remote(CommandInterface):
    def command(self):
        # Command to open PowerShell and execute 'ssh ubuntu'
        cmd = 'powershell -Command "Start-Process powershell -ArgumentList \'ssh marco@ubuntu\'"'


        # Open PowerShell and run the command
        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(f"An error occurred: {e}")

