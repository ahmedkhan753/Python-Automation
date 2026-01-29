import os
import pandas as pd

class extract:
    FOLDER = r'D:\PROJECTS\python-automation\pdf'
    FILENAME ='Serie Ibiza-1-1-3.pdf'
    FILE_PATH = os.path.join(FOLDER, FILENAME)

    def __init__(self,FILE_PATH):
        self.FILE_PATH = FILE_PATH

    def extract_tables(self):
        df = pd.read_pdf(self.FILE_PATH)

    def extract_features(self):

    def detect_bullets(self):
