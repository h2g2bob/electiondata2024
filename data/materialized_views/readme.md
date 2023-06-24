# Materialized Views

sqlite3 doesn't support materialized views, so actually these are
`create table ... as select ...`.

Run this after running the other data import scripts, and it will generate an
estimate of local government vote share per constituency:

```
sqlite> select * from combined_local_votes_to_westminster_2019 where westminster_2019 = 'Reading West';
westminster_2019  party                         vote_percent
----------------  ----------------------------  ------------
Reading West      L                             44
Reading West      C                             28
Reading West      LD                            14
Reading West      G                             10
Reading West      UK Independence Party (UKIP)  1
Reading West      The Liberal Party             0
Reading West      TUSC                          0
Reading West      I                             0
```

Some intermediate data is logged:

```
sqlite> select * from oa_to_westminster2019 c left join vote_percent_per_party_per_oa using (oa21cd) where c.westminster_2019 = 'Reading East' and party = 'I';
...
(A list of oa21cd which had elections with independent candidates)
```
