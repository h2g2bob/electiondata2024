from csv import DictReader
from dataclasses import dataclass
from typing import ClassVar
import re
import sqlite3

def read_csv_file(file_name):
    with open(file_name, mode="r", encoding="utf8") as myfile:
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
        return "Labour"
    if party_name == "Conservative and Unionist Party":
        return "Conservative"
    if party_name == "Liberal Democrats":
        return "Liberal Democrats"
    if party_name == "Green Party":
        return "Green"
    if party_name == "Independent":
        return "Independent"
    if party_name == "Plaid Cymru - The Party of Wales":
        return "Plaid Cymru"
    if party_name == "Trade Unionist and Socialist Coalition":
        return "TUSC"
    return None


@dataclass
class WardMappings:
    mappings: dict

    @classmethod
    def load(cls, con, ward_mapping_year):
        mappings = {}
        for row in con.execute(
            "select ward_id, ward_name from ward_to_blah where years like ?",
            ("%" + ward_mapping_year + "%",),
        ):
            [ward_id, ward_name] = row
            # XXX no check about duplicate ward_ids
            # XXX eg: from constituencies which have been re-numbered from one year to the next
            mappings[cls.normalize(ward_name)] = ward_id
        if not mappings:
            raise RuntimeError(f"No values in ward_to_blah for {ward_mapping_year}. Import ons_ward_to_blah before the democlub_results import.")
        return cls(mappings=mappings)

    def lookup(self, democlub_ballot_paper_id):
        parts = democlub_ballot_paper_id.split(".")
        assert parts[0] == "local", f"What election is {democlub_ballot_paper_id}"
        [_local, _council, ward, _date] = parts
        ons_ward_id = self.mappings.get(self.normalize(ward), None)
        assert ons_ward_id is not None, f"what {ward} from {democlub_ballot_paper_id}: check ward_to_blah for similar names"
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
        if text == "Littledown & Ilford":
            return "littledowniford"
        return re.sub(
            r"[^a-z]+", "", text.lower().replace(" and ", "").replace("-and-", "")
        )


ignore_elections = [
    # County Councils (upper) have larger wards than District Councils (lower)
    # and it's hard to find data about what these wards are
    # so lets skip them
    "cambridgeshire",
    "derbyshire",
    "devon",
    "east-sussex",
    "essex",
    "gloucestershire",
    "hampshire",
    "hertfordshire",
    "kent",
    "lancashire",
    "leicestershire",
    "lincolnshire",
    "norfolk",
    "nottinghamshire",
    "oxfordshire",
    "somerset",
    "staffordshire",
    "suffolk",
    "surrey",
    "swansea",
    "warwickshire",
    "west-sussex",
    "worcestershire",

    # Northern ireland regions
    # (I think the ward data doesn't cover northern ireland?)
    "antrim-and-newtownabbey",
    "ards-and-north-down",
    "armagh-city-banbridge-and-craigavon",
    "belfast",
    "causeway-coast-and-glens",
    "derry-city-and-strabane",
    "fermanagh-and-omagh",
    "lisburn-and-castlereagh",
    "mid-and-east-antrim",
    "mid-ulster",
    "newry-mourne-and-down",
]
re_ignore_elections = re.compile(
    r"^local\.(" + "|".join(re.escape(name) for name in ignore_elections) + ")\."
)

problems = [
    "local.tower-hamlets.bethnal-green-east.2022-05-05",
    "local.tower-hamlets.bethnal-green-west.2022-05-05",
]


def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
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

        election_date_to_ons_date = {
            "2018-05-03": "2018",
            "2019-05-02": "2019",
            "2021-05-06": "2021",
            "2022-05-05": "2022",
            "2023-05-04": "2023",
        }
        for election_date, ons_date in election_date_to_ons_date.items():
            import_democlub(con, election_date, ons_date)

    print("vacuum")
    con.execute("vacuum")
    print("done")

def import_democlub(con, date: str, ward_mapping_year: str):
        file_name = f"results-{date}.csv"
        print(file_name)

        ward_mappings = WardMappings.load(con, ward_mapping_year)

        for i, row in enumerate(read_csv_file(file_name)):
            election_id = row["election_id"]
            ballot_paper_id = row["ballot_paper_id"]
            party_name = row["party_name"]
            ballots_cast = int(row["ballots_cast"])
            try:
                elected = str_to_bool(row["elected"])
            except KeyError:
                elected = str_to_bool(row["is_winner"])

            is_by_election = ".by." in ballot_paper_id
            if is_by_election:
                continue

            other_elections = [
                "gla.",
                "mayor.",
                "senedd.",
                "sp.",
            ]
            if any(ballot_paper_id.startswith(prefix) for prefix in other_elections):
                continue

            if re_ignore_elections.search(ballot_paper_id) is not None:
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


if __name__ == "__main__":
    main()
