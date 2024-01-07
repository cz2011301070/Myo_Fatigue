import pandas as pd
import os
class CSVHandler_Pd:
    def __init__(self, filename:str):
        self.file_path = os.path.join(os.getcwd(), "Data", filename+'.csv')

    def read_data(self):
        try:
            df = pd.read_csv(self.file_path)
            return df
        except FileNotFoundError:
            print(f"file {self.file_path} is not found, please check the file path")

    def write_data(self, content, mode='a'):
        try:
            df = pd.DataFrame(content)
            df.to_csv(self.file_path, index=False, header=True, mode=mode)
        except Exception as e:
            print(f"error rasied during writing data:{e}")
