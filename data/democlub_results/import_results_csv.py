from csv import DictReader
from dataclasses import dataclass
from typing import ClassVar
import re
import sqlite3

DATE = "2023-05-04"
FILE_NAME = f"results-{DATE}.csv"


def read_csv_file():
    with open(FILE_NAME, mode="r", encoding="utf8") as myfile:
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


@dataclass
class WardMappings:
    mappings: dict

    # https://www.lgbce.org.uk/all-reviews/
    lgbce_review: ClassVar = (
        "amber-valley",
        "bedford",
        "blaby",
        "bolton",
        "bracknell-forest",
        "brighton-and-hove",
        "central-bedfordshire",
        "charnwood",
        "chesterfield",
        "derby",
        "derbyshire-dales",
        "east-hertfordshire",
        "east-staffordshire",
        "epsom-and-ewell",
        "fenland",
        "fylde",
        "gravesham",
        "guildford",
        "lancaster",
        "liverpool",
        "luton",
        "malvern-hills",
        "mansfield",
        "medway",
        "mid-devon",
        "mid-sussex",
        "mole-valley",
        "new-forest",
        "north-kesteven",
        "north-lincolnshire",
        "rushcliffe",
        "slough",
        "south-staffordshire",
        "southampton",
        "stockport",
        "stockton-on-tees",
        "stoke-on-trent",
        "stratford-on-avon",
        "telford-and-wrekin",
        "tonbridge-and-malling",
        "trafford",
        "waverley",
        "west-lancashire",
        "wigan",
        "wolverhampton",
        "wychavon",
    )

    @classmethod
    def load(cls, con):
        mappings = {}
        for row in con.execute("select ward_id, ward_name from ward_to_blah"):
            [ward_id, ward_name] = row
            mappings[cls.normalize(ward_name)] = ward_id
        return cls(mappings=mappings)

    def lookup(self, democlub_ballot_paper_id):
        parts = democlub_ballot_paper_id.split(".")
        assert parts[0] == "local"
        [_local, council, ward, _date] = parts
        is_boundary_edited = council in self.lgbce_review
        ons_ward_id = self.mappings.get(self.normalize(ward), None)
        assert ons_ward_id is not None or is_boundary_edited
        return (is_boundary_edited, ons_ward_id)

    @staticmethod
    def normalize(text):
        if text == "westwood-jacksdale":
            return "jacksdalewestwood"
        return re.sub(
            r"[^a-z]+", "", text.lower().replace(" and ", "").replace("-and-", "")
        )


def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
        ward_mappings = WardMappings.load(con)

        con.execute("drop table if exists democlub_results")
        con.execute(
            "create table democlub_results(date text, election_id text, ballot_paper_id text, party_name text, ballots_cast int, elected bool, ons_ward_id text, lgbce_review bool)"
        )
        con.execute(
            "create index if not exists democlub_results_election_id_idx on democlub_results (election_id)"
        )
        con.execute(
            "create index if not exists democlub_results_ballot_paper_id_idx on democlub_results (ballot_paper_id)"
        )
        con.execute(
            "create index if not exists democlub_results_ons_ward_id_idx on democlub_results (ons_ward_id)"
        )
        for i, row in enumerate(read_csv_file()):
            date = DATE
            election_id = row["election_id"]
            ballot_paper_id = row["ballot_paper_id"]
            party_name = row["party_name"]
            ballots_cast = int(row["ballots_cast"])
            elected = str_to_bool(row["elected"])

            is_by_election = ".by." in ballot_paper_id
            if is_by_election:
                continue

            if ballot_paper_id.startswith("mayor."):
                continue

            [is_boundary_edited, ons_ward_id] = ward_mappings.lookup(ballot_paper_id)

            con.execute(
                "insert into democlub_results(date, election_id, ballot_paper_id, party_name, ballots_cast, elected, ons_ward_id, lgbce_review)"
                " values (?, ?, ?, ?, ?, ?, ?, ?)",
                (date, election_id, ballot_paper_id, party_name, ballots_cast, elected, ons_ward_id, is_boundary_edited),
            )

            if i % 1000 == 0:
                print(".", end="", flush=True)
    con.execute("vacuum")
    print("done")


if __name__ == "__main__":
    main()
