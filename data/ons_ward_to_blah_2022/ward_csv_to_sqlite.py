from csv import DictReader
import sqlite3

FILE_NAME = 'Ward_to_Westminster_Parliamentary_Constituency_to_Local_Authority_District_to_Upper_Tier_Local_Authority_(December_2022)_Lookup_in_the_United_Kingdom.csv'

def read_csv_file():
    with open(FILE_NAME, mode='r', encoding="utf8") as myfile:
        csvreader = DictReader(myfile)
        for row in csvreader:
            yield row

def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:

        con.execute("drop table if exists ward_to_blah")
        con.execute("create table ward_to_blah(ward_id, ward_name text, westminster_id text, westminster_name text, lower_id text, lower_name text, upper_id text, upper_name text)")
        con.execute("create index if not exists ward_to_blah_ward_id_idx on ward_to_blah (ward_id)")
        con.execute("create index if not exists ward_to_blah_ward_name_idx on ward_to_blah (ward_name)")
        con.execute("create index ward_to_blah_westminster_id_idx on ward_to_blah (westminster_id);")
        for i, row in enumerate(read_csv_file()):
            ward_id = row['\ufeffWD22CD']
            ward_name = row['WD22NM']
            westminster_id = row['PCON22CD']
            westminster_name = row['PCON22NM']
            lower_id = row['LAD22CD']
            lower_name = row['LAD22NM']
            upper_id = row['UTLA22CD']
            upper_name = row['UTLA22NM']
            con.execute(
                "insert into ward_to_blah(ward_id, ward_name, westminster_id, westminster_name, lower_id, lower_name, upper_id, upper_name)"
                " values (?, ?, ?, ?, ?, ?, ?, ?)",
                (ward_id, ward_name, westminster_id, westminster_name, lower_id, lower_name, upper_id, upper_name),
            )
            if i % 1000 == 0:
                print(".", end="", flush=True)
    con.execute("vacuum")
    print("done")

if __name__ == "__main__":
    main()