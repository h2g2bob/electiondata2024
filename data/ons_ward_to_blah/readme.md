# Ward to Westminster Parliamentary Constituency and Local Authority

ONS:

- May 2023: https://geoportal.statistics.gov.uk/datasets/ons::ward-to-local-authority-district-may-2023-lookup-in-the-united-kingdom/about
- Dec 2022: https://geoportal.statistics.gov.uk/datasets/ons::ward-to-westminster-parliamentary-constituency-to-local-authority-district-to-upper-tier-local-authority-december-2022-lookup-in-the-united-kingdom/about
- Dec 2021: https://geoportal.statistics.gov.uk/documents/ward-to-local-authority-district-december-2021-lookup-in-the-united-kingdom-1/about
- Dec 2020: https://geoportal.statistics.gov.uk/datasets/ons::ward-to-westminster-parliamentary-constituency-to-local-authority-district-to-upper-tier-local-authority-december-2020-lookup-in-the-united-kingdom-v2-1/about
- Dec 2019: https://geoportal.statistics.gov.uk/datasets/ons::ward-to-westminster-parliamentary-constituency-to-lad-to-utla-dec-2019-lookup-in-the-uk/about
- Dec 2018: https://geoportal.statistics.gov.uk/datasets/ons::ward-to-westminster-parliamentary-constituency-to-local-authority-district-december-2018-lookup-in-the-united-kingdom-1/about

Ward to Westminster Parliamentary Constituency to Local Authority District to Upper Tier Local Authority (December 2022) Lookup in the United Kingdom

```
Source: Office for National Statistics licensed under the Open Government Licence v.3.0
Contains OS data © Crown copyright and database right 2022
```

## Using the data

The "Moulsham Lodge" ward is in the "Chelmsford" Local Authority District (LAD, lower) and the "Essex"
Upper Tier Local Authority (UTLA, upper). It's also in Chelmsford westminster constituency.

```
sqlite> select * from ward_to_blah where ward_id = 'E05004108';
ward_id    ward_name       westminster_id  westminster_name  lower_id   lower_name  upper_id   upper_name  years
---------  --------------  --------------  ----------------  ---------  ----------  ---------  ----------  -------------------
E05004108  Moulsham Lodge  E14000628       Chelmsford        E07000070  Chelmsford  E10000012  Essex       2018,2019,2020,2022
```

### Wards in multiple constituencies

Some wards are split between multiple westminster constituencies. This one is in 3 constituencies:

```
sqlite> select * from ward_to_blah where ward_id = 'E05008562';
ward_id    ward_name   westminster_id  westminster_name  lower_id   lower_name  upper_id   upper_name      years
---------  ----------  --------------  ----------------  ---------  ----------  ---------  --------------  -------------------
E05008562  Kirkburton  E14000645       Colne Valley      E08000034  Kirklees    E11000006  West Yorkshire  2018,2019,2020,2022
E05008562  Kirkburton  E14000666       Dewsbury          E08000034  Kirklees    E11000006  West Yorkshire  2018,2019,2020,2022
E05008562  Kirkburton  E14000756       Huddersfield      E08000034  Kirklees    E11000006  West Yorkshire  2018,2019,2020,2022
```

### Wards re-numbered

It seems like many wards got re-numbered. This seems to apply to all of Wales and London:

```
sqlite> select * from ward_to_blah where ward_name = 'West Cross';
ward_id    ward_name   westminster_id  westminster_name  lower_id   lower_name  upper_id   upper_name  years
---------  ----------  --------------  ----------------  ---------  ----------  ---------  ----------  --------------
W05000550  West Cross  W07000046       Gower             W06000011  Swansea     W06000011  Swansea     2018,2019,2020
W05001070  West Cross  W07000046       Gower             W06000011  Swansea     W06000011  Swansea     2022
```

At the same time, some wards were renamed:

```
sqlite> select * from ward_to_blah where ward_name like 'Marylebone%';
ward_id    ward_name               westminster_id  westminster_name                  lower_id   lower_name   upper_id   upper_name    years
---------  ----------------------  --------------  --------------------------------  ---------  -----------  ---------  ------------  --------------
E05000641  Marylebone High Street  E14000639       Cities of London and Westminster  E09000033  Westminster  E13000001  Inner London  2018,2019,2020
E05013801  Marylebone              E14000639       Cities of London and Westminster  E09000033  Westminster  E13000001  Inner London  2022
```

### LGBCE boundary reviews

https://www.lgbce.org.uk/all-reviews/ does periodic reviews.

Normally, not much changes, but sometimes larger changes are made.

Often this comes from events happening, such as Suffolk Coastal got merged with Waveney to beome
[East Suffolk](https://en.wikipedia.org/wiki/East_Suffolk_District):

```
sqlite> select * from ward_to_blah where lower_name in ('East Suffolk', 'Suffolk Coastal', 'Waveney') order by lower_name, ward_name;
ward_id    ward_name                       westminster_id  westminster_name                   lower_id   lower_name       upper_id   upper_name  years
---------  ------------------------------  --------------  ---------------------------------  ---------  ---------------  ---------  ----------  --------------
E05012734  Aldeburgh & Leiston             E14000981       Suffolk Coastal                    E07000244  East Suffolk     E10000029  Suffolk     2019,2020,2022
E05012735  Beccles & Worlingham            E14001022       Waveney                            E07000244  East Suffolk     E10000029  Suffolk     2019,2020,2022
...
E05012761  Woodbridge                      E14000981       Suffolk Coastal                    E07000244  East Suffolk     E10000029  Suffolk     2019,2020,2022
E05012762  Wrentham, Wangford & Westleton  E14000981       Suffolk Coastal                    E07000244  East Suffolk     E10000029  Suffolk     2019,2020,2022
E05010432  Aldeburgh                       E14000981       Suffolk Coastal                    E07000205  Suffolk Coastal                         2018
E05010433  Deben                           E14000981       Suffolk Coastal                    E07000205  Suffolk Coastal                         2018
...
E05010457  Woodbridge                      E14000981       Suffolk Coastal                    E07000205  Suffolk Coastal                         2018
E05010457  Woodbridge                      E14000624       Central Suffolk and North Ipswich  E07000205  Suffolk Coastal                         2018
E05007228  Beccles North                   E14001022       Waveney                            E07000206  Waveney                                 2018
E05007229  Beccles South                   E14001022       Waveney                            E07000206  Waveney                                 2018
...
E05007250  Wrentham                        E14000981       Suffolk Coastal                    E07000206  Waveney                                 2018
```

Note that `upper_id` and `upper_name` here are `null` because that data is missing from the 2018 dataset.
