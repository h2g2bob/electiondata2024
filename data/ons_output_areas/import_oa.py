from csv import DictReader
import sqlite3

FILE_NAMES = {
    2018: 'Output_Area_to_Ward_to_Local_Authority_District_(December_2018)_Lookup_in_England_and_Wales.csv',
    2019: 'Output_Area_to_Ward_to_Local_Authority_District_(December_2019)_Lookup_in_England_and_Wales.csv',
    2020: 'Output_Area_to_Ward_to_Local_Authority_District_(December_2020)_Lookup_in_England_and_Wales_V2.csv',
    2023: 'Output_Area_to_Ward_to_Local_Authority_District_(May_2023)_Lookup_in_England_and_Wales.csv',
}

OA_11_21_FILENAME = 'Output_Areas_(2011)_to_Output_Areas_(2021)_to_Local_Authority_District_(2022)_Lookup_in_England_and_Wales_(Version_2).csv'

def read_csv_file(filename):
    with open(filename, mode='r', encoding="utf8") as myfile:
        csvreader = DictReader(myfile)
        for row in csvreader:
            yield row

def import_file(con, year, filename):
    yy = f"{year % 100:02d}"
    oa = "11" if year < 2021 else "21"

    # File can start with junk termination characters
    omg = "\ufeff" if year in (2018, 2023) else ""

    print(filename)
    for row in read_csv_file(filename):
        oa__cd = row[f"{omg}OA{oa}CD"]
        wd__cd = row[f"WD{yy}CD"]
        con.execute(
            f"insert into ons_oa{oa}(oa{oa}cd, ward_year, ward_id) values (?, ?, ?)",
            (oa__cd, year, wd__cd,),
        )

def import_file_11_21(con, filename):
    print(filename)
    for row in read_csv_file(filename):
        con.execute(
            "insert into ons_oa11_oa21(oa11cd, oa21cd) values (?, ?)",
            (row["OA11CD"], row["OA21CD"],),
        )

def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
        # 2011 Census Output Areas
        con.execute("drop table if exists ons_oa11")
        con.execute("""
            create table ons_oa11(
                oa11cd text not null,
                ward_year integer not null,
                ward_id text not null,

                primary key (oa11cd, ward_year, ward_id))
        """)
        con.execute("create index ons_oa11_ward_idx on ons_oa11 (ward_id);")

        # 2021 Census Output Areas
        con.execute("drop table if exists ons_oa21")
        con.execute("""
            create table ons_oa21(
                oa21cd text not null,
                ward_year integer not null,
                ward_id text not null,

                primary key (oa21cd, ward_year, ward_id))
        """)
        con.execute("create index ons_oa21_ward_idx on ons_oa21 (ward_id);")

        # 2021 v 2011
        con.execute("drop table if exists ons_oa11_oa21")
        con.execute("""
            create table ons_oa11_oa21(
                oa11cd text not null,
                oa21cd text not null,

                primary key (oa11cd, oa21cd))
        """)
        con.execute("create index ons_reverse_idx on ons_oa11_oa21 (oa21cd, oa11cd);")

        import_file_11_21(con, OA_11_21_FILENAME)

        for year, filename in FILE_NAMES.items():
            import_file(con, year, filename)

        print("materialized view")
        con.execute("""
            create view ons_oa_to_ward as
                -- OA to WD for older years, mapped to OA21
                select distinct oa21cd, ward_id from ons_oa11 join ons_oa11_oa21 using (oa11cd)
                union
                -- OA to WD for OA21
                select distinct oa21cd, ward_id from ons_oa21;
        """)

    print("vacuum")
    con.execute("vacuum")
    print("done")

if __name__ == "__main__":
    main()
