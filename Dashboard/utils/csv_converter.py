import argparse

import pandas as pd


class ConvertCSV():
    def __init__(self, file):
        self.file = file
        self.read()
        self.save()

    def read(self):
        self.df = pd.read_csv(self.file)
        self.df = self.df[self.df.columns.drop(list(self.df.filter(regex='Unnamed:')))]

    def save(self):
        self.df.to_json(f"{self.file}.json", orient='records')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True,
                    help="File Path")
    args = vars(ap.parse_args())
    ConvertCSV(args['file'])