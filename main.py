import sys
sys.dont_write_bytecode = True
import horusScreens as hs

skip_Intro = True

def main():
    if not skip_Intro:
        hs.intro_Screen()
    else:
        hs.main_Screen()

main()