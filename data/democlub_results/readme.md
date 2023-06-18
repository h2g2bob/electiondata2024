# Democracy Club election results

DemoClub: https://candidates.democracyclub.org.uk/uk_results/

```
wget https://candidates.democracyclub.org.uk/media/csv-archives/results-2023-05-04.csv
wget https://candidates.democracyclub.org.uk/media/csv-archives/results-2022-05-05.csv
wget https://candidates.democracyclub.org.uk/media/csv-archives/results-2021-05-06.csv
wget https://candidates.democracyclub.org.uk/media/csv-archives/results-2019-05-02.csv
wget https://candidates.democracyclub.org.uk/media/csv-archives/results-2018-05-03.csv
```

```
The data on this site is provided under the Attribution 4.0 (CC BY 4.0) licence.
Please give credit to Democracy Club when reusing this data.
```

## Other data which Democracy Club publish

Note there are other nice APIs, like candidates
`wget https://candidates.democracyclub.org.uk/media/candidates-2023-05-04.csv`
amd election data
`https://candidates.democracyclub.org.uk/api/next/ballots/?election_date=2023-05-04`

## Some things the data can report

The importer maps the democlub results to `ons_ward_id`, so you can query
ballots cast per council:

```
sqlite> select ons.lower_name, sum(dc.ballots_cast) from ward_to_blah ons
join democlub_results dc on ons.ward_id = dc.ons_ward_id
where ons.westminster_name = 'Rochford and Southend East'
group by 1
order by 2 desc;
lower_name       sum(dc.ballots_cast)
---------------  --------------------
Southend-on-Sea  11019
Rochford         4160
```

That's ballots cast, and not electorate. It might get misleading because some
voters vote more frequently than others, eg: a large ward might vote for
3 councilors (each person casts 3 votes every 4 years) and a small ward might
vote for 1 councilor (each person casts 1 vote every 4 years).

(Surprisingly different ward sizes between councils is not a problem when
you just count votes.)

And a query for ballots cast per party:

```
sqlite> select dc.party_name, sum(dc.ballots_cast) from ward_to_blah ons
join democlub_results dc on ons.ward_id = dc.ons_ward_id
where ons.westminster_name = 'Rochford and Southend East'
group by 1
order by 2 desc;
party_name                       sum(dc.ballots_cast)
-------------------------------  --------------------
Conservative and Unionist Party  6918
Labour Party                     2982
Labour and Co-operative Party    1534
Independent                      1228
Liberal Democrats                966
Green Party                      761
Rochford District Residents      403
Confelicity                      342
Reform UK                        45
```

There should be some normalization
