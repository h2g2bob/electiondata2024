from csv import DictReader
import sqlite3

DATE = "2023-05-04"
FILE_NAME = f"results-{DATE}.csv"

def read_csv_file():
    with open(FILE_NAME, mode='r', encoding="utf8") as myfile:
        csvreader = DictReader(myfile)
        for row in csvreader:
            yield row

def str_to_bool(string):
    if string == "True":
        return True
    if string == "False":
        return False
    if string == "":
        return False
    raise ValueError(string)

def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
        con.execute("drop table if exists democlub_results")
        con.execute("create table democlub_results(date text, election_id text, ballot_paper_id text, party_name text, ballots_cast int, elected bool)")
        con.execute("create index if not exists democlub_results_election_id_idx on democlub_results (election_id)")
        con.execute("create index if not exists democlub_results_ballot_paper_id_idx on democlub_results (ballot_paper_id)")
        for i, row in enumerate(read_csv_file()):
            date = DATE
            election_id = row['election_id']
            ballot_paper_id = row['ballot_paper_id']
            party_name = row['party_name']
            ballots_cast = int(row['ballots_cast'])
            elected = str_to_bool(row['elected'])

            con.execute(
                "insert into democlub_results(date, election_id, ballot_paper_id, party_name, ballots_cast, elected)"
                " values (?, ?, ?, ?, ?, ?)",
                (date, election_id, ballot_paper_id, party_name, ballots_cast, elected),
            )
            if i % 1000 == 0:
                print(".", end="", flush=True)
    con.execute("vacuum")
    print("done")

if __name__ == "__main__":
    main()
