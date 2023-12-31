from csv import DictReader
import sqlite3

FILE_NAMES = {
    2018: 'Ward_to_Westminster_Parliamentary_Constituency_to_Local_Authority_District_(December_2018)_Lookup_in_the_United_Kingdom.csv',
    2019: 'Ward_to_Westminster_Parliamentary_Constituency_to_LAD_to_UTLA_(Dec_2019)_Lookup_in_the_UK.csv',
    2020: 'Ward_to_Westminster_Parliamentary_Constituency_to_Local_Authority_District_to_Upper_Tier_Local_Authority_(December_2020)_Lookup_in_the_United_Kingdom_V2.csv',
    2021: 'WD21_LAD21_UK_LU-from-xlsx.csv',
    2022: 'Ward_to_Westminster_Parliamentary_Constituency_to_Local_Authority_District_to_Upper_Tier_Local_Authority_(December_2022)_Lookup_in_the_United_Kingdom.csv',
    2023: 'Ward_to_Local_Authority_District_(May_2023)_Lookup_in_the_United_Kingdom.csv',
}

def read_csv_file(filename):
    with open(filename, mode='r', encoding="utf8") as myfile:
        csvreader = DictReader(myfile)
        for row in csvreader:
            yield row

def import_file(con, year, filename):
    yy = f"{year % 100:02d}"
    # File can start with junk termination characters
    omg = "\ufeff" if year in (2018, 2022, 2023) else ""
    print(filename, end="", flush=True)
    for i, row in enumerate(read_csv_file(filename)):
        ward_id = row[f"{omg}WD{yy}CD"]
        ward_name = row[f"WD{yy}NM"]
        westminster_id = row.get(f"PCON{yy}CD", None)
        westminster_name = row.get(f"PCON{yy}NM", None)
        lower_id = row[f"LAD{yy}CD"]
        lower_name = row[f"LAD{yy}NM"]
        upper_id = row.get(f"UTLA{yy}CD", None)
        upper_name = row.get(f"UTLA{yy}NM", None)
        con.execute(
            "insert into ward_to_blah(ward_id, ward_name, westminster_id, westminster_name, lower_id, lower_name, upper_id, upper_name, years)"
            " values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            " on conflict (ward_id, westminster_id) where ward_name = ? and westminster_id = ? and lower_id = ?"
            " do update set years = years || ',' || ?, upper_id = coalesce(upper_id, ?), upper_name = coalesce(upper_name, ?)",
            (ward_id, ward_name, westminster_id, westminster_name, lower_id, lower_name, upper_id, upper_name, str(year))
            + (ward_name, westminster_id, lower_id)
            + (str(year), upper_id, upper_name),
        )
        if i % 1000 == 0:
            print(".", end="", flush=True)
    print("")

def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
        con.execute("drop table if exists ward_to_blah")
        con.execute("""
            create table ward_to_blah(
                ward_id text not null,
                ward_name text not null,
                westminster_id text,
                westminster_name text,
                lower_id text not null,
                lower_name text not null,
                upper_id text,
                upper_name text,
                years text not null,

                -- A ward can be in two westminster constituencies, eg: W05000895,Vaynor
                -- so we get two rows in the CSV and two database rows
                primary key (ward_id, westminster_id))
        """)
        con.execute("create index ward_to_blah_ward_name_idx on ward_to_blah (ward_name);")
        con.execute("create index ward_to_blah_westminster_id_idx on ward_to_blah (westminster_id);")
        for year, filename in FILE_NAMES.items():
            import_file(con, year, filename)
    print("vacuum...", end="", flush=True)
    con.execute("vacuum")
    print("done")

if __name__ == "__main__":
    main()
