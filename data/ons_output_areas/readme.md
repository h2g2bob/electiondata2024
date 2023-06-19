# ONS Output Areas

We can map output areas to wards.

- 2019: OA11CD https://geoportal.statistics.gov.uk/datasets/ons::output-area-to-ward-to-local-authority-district-december-2019-lookup-in-england-and-wales-1/about 
- 2018: OA11CD https://geoportal.statistics.gov.uk/datasets/ons::output-area-to-ward-to-local-authority-district-december-2018-lookup-in-england-and-wales-1/about
- 2020: OA11CD https://geoportal.statistics.gov.uk/datasets/ons::output-area-to-ward-to-local-authority-district-december-2020-lookup-in-england-and-wales-v2-1/about
- 2023: OA21CD https://geoportal.statistics.gov.uk/datasets/ons::output-area-to-ward-to-local-authority-district-may-2023-lookup-in-england-and-wales/about

And:

- OA11CD to OA21CD https://geoportal.statistics.gov.uk/datasets/ons::output-areas-2011-to-output-areas-2021-to-local-authority-district-2022-lookup-in-england-and-wales-version-2-1/about

```
Source: Office for National Statistics licensed under the Open Government Licence v.3.0
Contains OS data © Crown copyright and database right 2023
```

## Why

Output Areas are approximately the same size, in terms of population.

Ward boundaries change over time, so we can calulate...

- We have election results for (old) wards, so can guess the political
  leanings of each ward and the output areas it contained (at the time)
- We know the wards, and therefore the output areas, of the new
  constituencies, so can apply our guesses per OA to the constituency.

## Example

Taffs Well changed `ward_id`:

```
sqlite> select * from ward_to_blah where ward_name like 'Taff%';
ward_id    ward_name    westminster_id  westminster_name  lower_id   lower_name         upper_id   upper_name         years
---------  -----------  --------------  ----------------  ---------  -----------------  ---------  -----------------  --------------
W05000691  Taffs Well   W07000075       Pontypridd        W06000016  Rhondda Cynon Taf  W06000016  Rhondda Cynon Taf  2018,2019,2020
W05001103  Taff's Well  W07000075       Pontypridd        W06000016  Rhondda Cynon Taf  W06000016  Rhondda Cynon Taf  2022
```

But all the OA stayed the same, so we can tell these are the same place:

```
sqlite> select * from ons_oa_to_ward where ward_id in ('W05000691', 'W05001103');
oa21cd     ward_id  
---------  ---------
W00006515  W05000691
W00006515  W05001103
W00006516  W05000691
W00006516  W05001103
W00006517  W05000691
W00006517  W05001103
W00006518  W05000691
W00006518  W05001103
W00006519  W05000691
W00006519  W05001103
W00006520  W05000691
W00006520  W05001103
W00006521  W05000691
W00006521  W05001103
W00006522  W05000691
W00006522  W05001103
W00006523  W05000691
W00006523  W05001103
W00006524  W05000691
W00006524  W05001103
W00006525  W05000691
W00006525  W05001103
W00006526  W05000691
W00006526  W05001103
```
