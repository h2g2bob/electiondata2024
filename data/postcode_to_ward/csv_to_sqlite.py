from csv import DictReader
from io import TextIOWrapper
from zipfile import ZipFile
import sqlite3

def read_csv_file():
    with ZipFile('postcodes.zip', 'r') as myzip:
        with myzip.open('postcodes.csv') as myfile:
            csvreader = DictReader(TextIOWrapper(myfile, encoding="utf8"))
            for row in csvreader:
                yield row

def main():
    con = sqlite3.connect("postcodes_to_ward.sqlite3")
    with con:
        con.execute("create table postcodes_to_ward(postcode_nospace text primary key, postcode text, ward_id)")
        for row in read_csv_file():
            postcode = row["Postcode"]
            postcode_nospace = postcode.upper().replace(" ", "")
            ward_id = row["Ward Code"]
            con.execute("insert into postcodes_to_ward(postcode_nospace, postcode, ward_id) values (?, ?, ?)", (postcode_nospace, postcode, ward_id,))
    con.execute("vacuum")

if __name__ == "__main__":
    main()
