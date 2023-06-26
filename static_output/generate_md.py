# python -m markdown -f bce_revised.html bce_revised.md

import sqlite3
import sys

SQL_REVISED = """
    select
        revised,
        case when vote_percent >= 5 then party else 'Other' end as party,
        sum(vote_percent) as vote_percent
    from combined_local_votes_to_revised
    where revised is not null
    group by 1,2
    order by 1,3 desc
"""

PER_PARTY_REVISED = """
    select
        oa_vote_pct.ballot_paper_ids,
        oa_vote_pct.oa21cd
    from vote_percent_per_party_per_oa oa_vote_pct
    left join ons_oa_to_ward oa_to_w on oa_vote_pct.oa21cd = oa_to_w.oa21cd
    left join bce_proposed bce on bce.ward_id = oa_to_w.ward_id
    where bce.revised = ?
"""

SQL_W2019 = """
    select
        westminster_2019,
        case when vote_percent >= 5 then party else 'Other' end as party,
        sum(vote_percent) as vote_percent
    from combined_local_votes_to_westminster_2019
    where westminster_2019 is not null
    group by 1,2
    order by 1,3 desc
"""

PER_PARTY_W2019 = """
    select
        oa_vote_pct.ballot_paper_ids,
        oa_vote_pct.oa21cd
    from vote_percent_per_party_per_oa oa_vote_pct
    left join ons_oa_to_ward oa_to_w on oa_vote_pct.oa21cd = oa_to_w.oa21cd
    left join ward_to_blah blah on blah.ward_id = oa_to_w.ward_id
    where blah.westminster_name = ?
"""

def main():
    [_, mode] = sys.argv
    if mode == "w2019":
        generate("the 2019 general election", SQL_W2019, PER_PARTY_W2019)
    elif mode == "revised":
        generate("the revised proposals", SQL_REVISED, PER_PARTY_REVISED)
    else:
        raise ValueError(mode)

def generate(title, sql, per_pary_sql):
    print(f"# Local election vote share, applied to constituency boundaries from {title}")
    print("")
    print("- Contains National Statistics data © Crown copyright and database rights 2023")
    print("- Contains OS data © Crown copyright and database right 2022, 2023")
    # We don't use postcode data on this page
    # print("- Contains Royal Mail data © Royal Mail copyright and database right 2023")
    # print("- Contains data from Wikipedia covered by the Creative Commons license ")
    print("- Contains data from Democracy Club provided under the Attribution 4.0 licence.")
    print("- Contains data from Office for National Statistics licensed under the Open Government Licence v.3.0")
    print("- Hastily calculated by David Batley - my contribution cc-by 4.0")
    print("")
    print("For details on how this is calculated, read [https://github.com/h2g2bob/electiondata2024]")
    print("")
    con = sqlite3.connect("../data/data.sqlite3")
    with con:
        old_constituency = None
        rows = tuple(con.execute(sql))
        for row in rows:
            [constituency, party, vote_pct] = row
            if constituency != old_constituency:
                if old_constituency is not None:
                    print_end(con, per_pary_sql, old_constituency)
                old_constituency = constituency
                print(f"## {constituency}")
            blocklen = (vote_pct * 15) // 100
            colorbar = f'<font color="{party_color(party)}">{"■" * blocklen}{"□" * (15 - blocklen)}</font>'
            print(f"- {colorbar} {vote_pct}% {party}")

        print_end(con, per_pary_sql, constituency)

def party_color(party):
    return {
        "Labour": "#DC241F",
        "Liberal Democrats": "#FAA61A",
        "Green": "#6AB023",
        "Conservative": "#0087DC",
    }.get(party, "black")

def print_end(con, per_pary_sql, constituency):
    ballot_ids = set()
    for row in con.execute(per_pary_sql, (constituency,)):
        [ballot_ids_str, _oa21cd] = row
        ballot_ids |= set(ballot_ids_str.split(","))
    print("")
    print("<details><summary>Details</summary>")
    print("")
    print("Based on elections:")
    print("")
    print("<ul>")
    for ballot_id in sorted(ballot_ids):
        print(f"<li>{ballot_id}</li>")
    print("</ul>")
    print("")
    print("</details>")
    print("")

if __name__ == "__main__":
    main()
