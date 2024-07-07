#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   simulation.py: main entry point of program
#
#   10/09/2023 - created at
#

from scene import Scene
from utils import get_args, check_dependencies

def main():
    check_dependencies()
    
    print("\t---\tStarting Simulation\t---\t")
    MainLoop = Scene(*get_args())
    MainLoop.start()
    print("\t---\tFinishes Simulation. Exiting Program\t---\t") 
   
if __name__ == '__main__':
    main()