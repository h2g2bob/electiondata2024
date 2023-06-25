# python -m markdown -f bce_revised.html bce_revised.md

import sqlite3

SQL = """
    select
        revised,
        case when vote_percent >= 5 then party else 'Other' end as party,
        sum(vote_percent) as vote_percent
    from combined_local_votes_to_revised
    where revised is not null
    group by 1,2
    order by 1,3 desc
"""

PER_PARTY = """
    select
        oa_vote_pct.ballot_paper_ids,
        oa_vote_pct.oa21cd
    from vote_percent_per_party_per_oa oa_vote_pct
    left join ons_oa_to_ward oa_to_w on oa_vote_pct.oa21cd = oa_to_w.oa21cd
    left join bce_proposed bce on bce.ward_id = oa_to_w.ward_id
    where bce.revised = ?
"""

def main():
    print("# Vote share at local elections for BCE revised proposals")
    print("")
    print("- Contains National Statistics data © Crown copyright and database rights 2023")
    print("- Contains OS data © Crown copyright and database right 2022, 2023")
    print("- Contains Royal Mail data © Royal Mail copyright and database right 2023")
    print("- Contains data from Wikipedia covered by the Creative Commons license ")
    print("- Contains data from Democracy Club provided under the Attribution 4.0 print("") licence.")
    print("- Contains data from Office for National Statistics licensed under the Open Government Licence v.3.0")
    print("- Hastily calculated by David Batley - my contribution cc-by 4.0")
    print("")
    con = sqlite3.connect("../data/data.sqlite3")
    with con:
        old_constituency = None
        rows = tuple(con.execute(SQL))
        for row in rows:
            [constituency, party, vote_pct] = row
            if constituency != old_constituency:
                if old_constituency is not None:
                    print_end(con, old_constituency)
                old_constituency = constituency
                print(f"## {constituency}")
            print(f"- {vote_pct}% {party}")

        print_end(con, constituency)

def print_end(con, constituency):
    ballot_ids = set()
    for row in con.execute(PER_PARTY, (constituency,)):
        [ballot_ids_str, _oa21cd] = row
        ballot_ids |= set(ballot_ids_str.split(","))
    print("")
    print("Based on elections:")
    print("")
    for ballot_id in sorted(ballot_ids):
        print(f"- {ballot_id}")
    print("")

if __name__ == "__main__":
    main()
