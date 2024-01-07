import csv
import os

class CSVHandler:
    def __init__(self, filename:str):
        self.filename  = os.path.join(os.getcwd(), "Data", filename+'.csv')
        
    
    def write_first_row(self, firstrow:list):
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(firstrow)

    def close_file(self):
        self.file.close()
    
    def write_row(self,content):
        with open(self.filename, mode='a+', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(content)

    def read_rows(self):
        data_list = []
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.reader(file)
            # skip the header row
            next(reader) 
            for row in reader:
                data_list.append(row)
            # data_list = [row for row in reader]
        return data_list
