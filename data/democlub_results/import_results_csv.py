from csv import DictReader
from dataclasses import dataclass
from typing import ClassVar
import re
import sqlite3

YEAR_FILTER = "2022"
DATE = "2022-05-05"
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


def normalize_party_name(party_name):
    if party_name in ("Labour Party", "Labour and Co-operative Party"):
        return "L"
    if party_name == "Conservative and Unionist Party":
        return "C"
    if party_name == "Liberal Democrats":
        return "LD"
    if party_name == "Green Party":
        return "G"
    if party_name == "Independent":
        return "I"
    if party_name == "Plaid Cymru - The Party of Wales":
        return "PC"
    if party_name == "Trade Unionist and Socialist Coalition":
        return "TUSC"
    if (
        "Residents" in party_name
        or ("Resident" in party_name and "Association" in party_name)
        or ("Resident" in party_name and "Group" in party_name)
    ):
        return "RA"
    if party_name == "Britain First":
        return None
    if (
        "Independents" in party_name
        or "Independent Party" in party_name
        or "Independent Group" in party_name
        or party_name.endswith(" First")
        or party_name.endswith(" First Party")
        or party_name.endswith(" Matters")
        or party_name
        in (
            "Yorkshire Party",
            "Tunbridge Wells Alliance",
            "Proud of Oldham & Saddleworth",
            "Our West Lancashire",
            "Coventry Citizens Party",
            "One Kearsley",
        )
    ):
        return "LOCAL"
    return None


@dataclass
class WardMappings:
    mappings: dict

    @classmethod
    def load(cls, con):
        mappings = {}
        for row in con.execute(
            "select ward_id, ward_name from ward_to_blah where years like ?",
            ("%" + YEAR_FILTER + "%",),
        ):
            [ward_id, ward_name] = row
            # XXX no check about duplicate ward_ids
            # XXX eg: from constituencies which have been re-numbered from one year to the next
            mappings[cls.normalize(ward_name)] = ward_id
        return cls(mappings=mappings)

    def lookup(self, democlub_ballot_paper_id):
        parts = democlub_ballot_paper_id.split(".")
        assert parts[0] == "local"
        [_local, _council, ward, _date] = parts
        ons_ward_id = self.mappings.get(self.normalize(ward), None)
        assert ons_ward_id is not None, f"what {ward} from {democlub_ballot_paper_id}"
        return ons_ward_id

    @staticmethod
    def normalize(text):
        if text == "westwood-jacksdale":
            return "jacksdalewestwood"
        if text == "Rhyl T? Newydd":
            return "rhyltynewydd"
        if text == "Pen draw Ll?n":
            return "pendrawllyn"
        if text == "Tre-garth a Mynydd Llandygái":
            return "tregarthamynyddllandygai"
        if text == "Canolbarth Môn":
            return "canolbarthmon"
        if text == "Hunmanby & Sherburn (part Scarborough)":
            return "hunmanbysherburn"
        if text == "tafs-well":
            return "taffswell"
        return re.sub(
            r"[^a-z]+", "", text.lower().replace(" and ", "").replace("-and-", "")
        )


upper_tier_elections = [
    "somerset",
    "swansea",
]
re_upper_tier_elections = re.compile(
    r"^local\." + "|".join(re.escape(name) for name in upper_tier_elections) + "\."
)

problems = [
    "local.tower-hamlets.bethnal-green-east.2022-05-05",
    "local.tower-hamlets.bethnal-green-west.2022-05-05",
]


def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
        ward_mappings = WardMappings.load(con)

        con.execute("drop table if exists democlub_results")
        con.execute(
            """
            create table democlub_results(
                date text not null,
                election_id text not null,
                ballot_paper_id text not null,
                party_name text,
                ballots_cast int,
                elected bool not null,
                normalized_party text,
                ons_ward_id text)
            """
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

            if re_upper_tier_elections.search(ballot_paper_id) is not None:
                continue

            if ballot_paper_id in problems:
                continue

            ons_ward_id = ward_mappings.lookup(ballot_paper_id)
            normalized_party = normalize_party_name(party_name)

            con.execute(
                "insert into democlub_results(date, election_id, ballot_paper_id, party_name, ballots_cast, elected, normalized_party, ons_ward_id)"
                " values (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    date,
                    election_id,
                    ballot_paper_id,
                    party_name,
                    ballots_cast,
                    elected,
                    normalized_party,
                    ons_ward_id,
                ),
            )

            if i % 1000 == 0:
                print(".", end="", flush=True)
    con.execute("vacuum")
    print("done")


if __name__ == "__main__":
    main()
