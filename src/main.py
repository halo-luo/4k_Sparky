import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
# import pytesseract
import os
import numpy
import torch
import logging


class ShowSparky:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sparky")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.img_path_dict = {}


if __name__ == '__main__':
    print("hello Sparky")
    window = tk.Tk()
    sparky = ShowSparky(window)
    # sparky.pack()
    window.mainloop()
