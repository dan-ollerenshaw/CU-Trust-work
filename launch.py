"""
This is the GUI that Children's University can use to
run the program.
"""

import pandas as pd
import sys
from tkinter import Button, Tk
from tkinter.filedialog import askopenfilename, askdirectory

# import program
sys.path.append('C:/Users/djoll/work/CU_trust/program/')
import make_stats
from functions import check_data_input


class ChildrensUniversityGui():
    def __init__(self, master):
        self.master = master
        master.title("This program generates some useful outputs for Children's University Trust.")
                        
        self.loader = Button(master,
                             text='Load the combined dataset.',
                             command=self.load)
        self.loader.grid(row=1, padx=5)

        self.choose_folder = Button(master,
                                    text='Choose a folder to save results to.',
                                    command=self.choose_folder)
        self.choose_folder.grid(row=2, padx=5)
        
        self.func = Button(master,
                           text='Generate statistics and maps.',
                           command=self.run_script)
        self.func.grid(row=3, padx=5)
                
        self.quitter = Button(master,
                              text='Quit program',
                              command=master.quit)
        self.quitter.grid(row=4)
    
        
    def load(self):
        """ User navigates to data file.
        """
        file = askopenfilename(defaultextension='.csv')
        df = pd.read_csv(file)
        check_data_input(df)
        self.data = df
    
    
    def choose_folder(self):
        """ User navigates to folder.
        """
        folder = askdirectory()
        self.folder = folder
        print(f'Selected folder: {folder}')
    
    
    def run_script(self):
        """ Run the program.
        """
        make_stats.main(self.data, self.folder)


def main():
    root = Tk()
    ChildrensUniversityGui(root)
    root.mainloop()
    root.destroy()


if __name__ == '__main__':
    main()
