import argparse

import rich 
import InquirerPy

""" This function will evaluate for 2 case cenarios
   1. Argument passing on run, this means the user will run like these two opts:

       # link flag
       - soundpp-dl -l audio-link 
       - soundpp-dl -link audio-link 

       # file flag
       - soundpp-dl -f links.txt 
       - soundpp-dl -file links.txt 

       The given file should be a readable file like txt in the following format:
            link 1
            link 2
            link 3 
            # comment (ignored by the link parser) 
            link 4 
        
       So, any text line that starts with # (whitespace doesn't count) will be counted as comment.

   2. Actual CLI app.

       [TODO]

"""

def start():
    rich.print("[italic red]Hello[/italic red] World!")

def main():
    start()

if __name__ == "__main__":
    main() 
