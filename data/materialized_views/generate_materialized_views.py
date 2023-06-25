import sqlite3

PER_OA_SQL = """
with

-- for each output_area, find all the ballot_paper_id which people might have
-- voted with
results_per_oa as (
  select
    a.oa21cd,
    r.date,
    r.ballot_paper_id,
    coalesce(r.normalized_party, r.party_name) as party,
    r.ballots_cast,
    r.elected
  from democlub_results r
  left join ons_oa_to_ward a on a.ward_id = r.ons_ward_id
),

-- for each output_area, how did people vote in the elections which include
-- that output_area
votes_per_party_per_oa as (
  select
    oa21cd,
    party,
    sum(ballots_cast) as votes_per_party,
    group_concat(distinct ballot_paper_id) as ballot_paper_ids
  from results_per_oa
  group by oa21cd, party
),
total_votes_per_oa as (
  select
    oa21cd,
    sum(votes_per_party) as total_votes
  from votes_per_party_per_oa
  group by oa21cd
)
select
  oa21cd,
  pp.party,
  100 * pp.votes_per_party / tv.total_votes as vote_percent,
  pp.ballot_paper_ids
from votes_per_party_per_oa pp
join total_votes_per_oa tv using (oa21cd)
order by 1, 3 desc
"""

OA_TO_W2019 = """
-- find the westminster constituency (or constituencies) for each output_area
select distinct
  w.westminster_name as westminster_2019,
  a.oa21cd
from ward_to_blah w
left join ons_oa_to_ward a on a.ward_id = w.ward_id
"""

PER_W2019_SQL = """
-- Find the vote share in each westminster constituency by taking an average
-- of out vote share estimate in each output_area (as output_areas are all
-- about the same size)
with
vote_pct_per_ons_per_w2019 as (
  select
    c.westminster_2019,
    oa_vote_pct.party,
    oa_vote_pct.oa21cd,
    oa_vote_pct.vote_percent
  from oa_to_westminster2019 c
  join vote_percent_per_party_per_oa oa_vote_pct on c.oa21cd = oa_vote_pct.oa21cd
  where c.westminster_2019 = ?
),
oa_per_w2019 as (
  select
    westminster_2019,
    count(distinct oa21cd) as distinct_oa_in_w2019
  from vote_pct_per_ons_per_w2019
  group by 1
)
select
  westminster_2019,
  party,
  -- average vote percent as sum(percent for each OA) / count(OA)
  sum(vote_percent) / (select distinct_oa_in_w2019 from oa_per_w2019 where oa_per_w2019.westminster_2019 = vote_pct_per_ons_per_w2019.westminster_2019) as vote_percent
from vote_pct_per_ons_per_w2019
group by westminster_2019, party
order by westminster_2019, vote_percent desc;
"""

PER_BCE_REVISED_SQL = """
-- Find the vote share in each proposed constituency by taking an average
-- of out vote share estimate in each output_area (as output_areas are all
-- about the same size)
with
vote_pct_per_ons_per_revised as (
  select
    bce.revised,
    oa_vote_pct.party,
    oa_vote_pct.oa21cd,
    oa_vote_pct.vote_percent
  from bce_proposed bce
  join ons_oa_to_ward oas_in_revised on bce.ward_id = oas_in_revised.ward_id
  join vote_percent_per_party_per_oa oa_vote_pct on oas_in_revised.oa21cd = oa_vote_pct.oa21cd
  where bce.revised = ?
),
oa_per_revised as (
  select
    revised,
    count(distinct oa21cd) as distinct_oa_in_revised
  from vote_pct_per_ons_per_revised
  group by 1
)
select
  revised,
  party,
  -- average vote percent as sum(percent for each OA) / count(OA)
  sum(vote_percent) / (select distinct_oa_in_revised from oa_per_revised where oa_per_revised.revised = vote_pct_per_ons_per_revised.revised) as vote_percent
from vote_pct_per_ons_per_revised
group by revised, party
order by revised, vote_percent desc;
"""

def main():
    con = sqlite3.connect("../data.sqlite3")
    with con:
        con.execute("drop table if exists oa_to_westminster2019")
        con.execute("drop table if exists vote_percent_per_party_per_oa")
        con.execute("drop table if exists combined_local_votes_to_westminster_2019")

        print("Generating oa_to_westminster2019")
        con.execute(
            "create table oa_to_westminster2019 as " + OA_TO_W2019
        )

        print("Generating vote_percent_per_party_per_oa")
        con.execute(
            "create table vote_percent_per_party_per_oa as " + PER_OA_SQL
        )

        print("Generating combined_local_votes_to_westminster_2019")
        con.execute("""
            create table combined_local_votes_to_westminster_2019 (
                westminster_2019 text not null,
                party text not null,
                vote_percent integer not null,
                primary key (westminster_2019, party)
            )
        """)
        for row in list(con.execute("select distinct c.westminster_2019 from oa_to_westminster2019 c")):
            print(".", end="", flush=True)
            [w2019] = row
            con.execute(
                "insert into combined_local_votes_to_westminster_2019 " + PER_W2019_SQL,
                (w2019,)
            )
        print("")

        print("Generating combined_local_votes_to_revised")
        con.execute("""
            create table combined_local_votes_to_revised (
                revised text not null,
                party text not null,
                vote_percent integer not null,
                primary key (revised, party)
            )
        """)
        for row in list(con.execute("select distinct bce.revised from bce_proposed bce")):
            print(".", end="", flush=True)
            [revised] = row
            con.execute(
                "insert into combined_local_votes_to_revised " + PER_BCE_REVISED_SQL,
                (revised,)
            )
        print("")

    print("vacuum")
    con.execute("vacuum")

if __name__ == "__main__":
    main()
