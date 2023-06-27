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

def generate(shorttitle, sql, per_pary_sql):
    fulltitle = f"Local election vote share, applied to constituency boundaries from {shorttitle}"
    print(
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
        f"<title>{fulltitle}</title>"
        "<link rel=\"stylesheet\" href=\"media/style.css\" />"
        "<link rel=\"alternate\" type=\"application/rss+xml\" href=\"index.rss\" />"
        "<meta charset=\"UTF-8\">"
        "<meta http-equiv=\"x-ua-compatible\" content=\"ie=edge\">"
        "<meta property=\"og:title\" content=\"{fulltitle}\" />"
        "<meta property=\"twitter:title\" content=\"{fulltitle}\" />"
        "<meta property=\"description\" content=\"{fulltitle}\" />"
        "<meta property=\"og:description\" content=\"{fulltitle}\" />"
        "<meta property=\"og:type\" content=\"article\" />"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />"
        "<meta name=\"robots\" content=\"noodp,noydir\"/>"
        "<meta property=\"og:locale\" content=\"en_GB\" />"
        "</head>"
        "<body>"
        f"<h1>{fulltitle}</h1>"
    )
    print("<ul>")
    print("<li>Contains National Statistics data © Crown copyright and database rights 2023</li>")
    print("<li>Contains OS data © Crown copyright and database right 2022, 2023</li>")
    # We don't use postcode data on this page
    # print("<li>Contains Royal Mail data © Royal Mail copyright and database right 2023</li>")
    # print("<li>Contains data from Wikipedia covered by the Creative Commons license</li>")
    print("<li>Contains data from Democracy Club provided under the Creative Commons Attribution 4.0 licence</li>")
    print("<li>Contains data from Office for National Statistics licensed under the Open Government Licence v.3.0</li>")
    print("<li>Hastily calculated by David Batley - my contribution cc-by 4.0</li>")
    print("</ul>")
    print("<p>For details on how this is calculated, read <a href=\"https://github.com/h2g2bob/electiondata2024\">github.com/h2g2bob/electiondata2024</a>.</p>")
    print(
        '<div>'
        '<label for="searchin"'
        ' style="background: #ccc; border: 0.1em #ccc solid; border-radius: 0.5em; min-height: 0.8em; display: inline-block; padding: 0.3em; padding-left: 0.5em; padding-right: 0.5em;"'
        ' >&#x1F50E;&nbsp;<input type="text" id="searchin" onkeyup="do_filter()"></label>'
        '<script type="application/javascript"><!--\n'
        'function do_filter() {\n'
        ' var value = document.getElementById("searchin").value;\n'
        ' Array.from(document.getElementsByTagName("div")).forEach((div) => {\n'
        '  if (div.hasAttribute("data-constituency")) {\n'
        '   div.style.display = div.getAttribute("data-constituency").toLowerCase().indexOf(value.toLowerCase()) == -1 ? "none" : "";\n'
        '  }\n'
        ' });\n'
        '}\n'
        '--></script>'
        '</div>'
    )
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
                print(
                    f"<div data-constituency=\"{constituency}\">"
                    f"<h2>{constituency}</h2>"
                    "<ul>"
                )
            blocklen = (vote_pct * 15) // 100
            colorbar = f'<font color="{party_color(party)}">{"■" * blocklen}{"□" * (15 - blocklen)}</font>'
            print(f"<li>{colorbar} {vote_pct}% {party}</li>")

        print_end(con, per_pary_sql, constituency)
    print("</body></html>")

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
    print(
        "</ul>"
        "<details><summary>Details</summary>"
        "<p>Based on elections:</p>"
        "<ul>"
    )
    for ballot_id in sorted(ballot_ids):
        print(f"<li>{ballot_id}</li>")
    print(
        "</ul>"
        "</details>"
        "</div>"
    )

if __name__ == "__main__":
    main()
