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
select
  c.westminster_2019,
  oa_vote_pct.party,
  -- vote percent as an average of the percentages of all OAs:
  sum(oa_vote_pct.vote_percent) / count(distinct oa21cd) as vote_percent
from vote_percent_per_party_per_oa oa_vote_pct
left join oa_to_westminster2019 c using (oa21cd)
group by westminster_2019, party
order by westminster_2019, vote_percent desc
"""

PER_BCE_REVISED_SQL = """
-- Find the vote share in each proposed constituency by taking an average
-- of out vote share estimate in each output_area (as output_areas are all
-- about the same size)
select
  bce.revised,
  oa_vote_pct.party,
  -- vote percent as an average of the percentages of all OAs:
  sum(oa_vote_pct.vote_percent) / count(distinct oa_vote_pct.oa21cd) as vote_percent
from vote_percent_per_party_per_oa oa_vote_pct
left join ons_oa_to_ward oa_to_w on oa_vote_pct.oa21cd = oa_to_w.oa21cd
left join bce_proposed bce on bce.ward_id = oa_to_w.ward_id
group by revised, party
order by revised, vote_percent desc
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
        con.execute(
            "create table combined_local_votes_to_westminster_2019 as " + PER_W2019_SQL
        )

        print("Generating combined_local_votes_to_revised")
        con.execute(
            "create table combined_local_votes_to_revised as " + PER_BCE_REVISED_SQL
        )

    print("vacuum")
    con.execute("vacuum")

if __name__ == "__main__":
    main()
