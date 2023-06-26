Data for an election geek.

- `data/*/readme.md` describes where you can get source data
- python scripts compile it into `data/data.sqlite3`

The 2024 elections may be interesting: the [Boundary Commission for England]
and other nations are editing the Westminster constituency boundaries.

[Boundary Commission for England]: https://boundarycommissionforengland.independent.gov.uk/

# Approach

The idea is

- the new constituencies are (mosly) aligned to local government wards
- we can look at the elections in these wards and give an average of how people voted

Simple!

Sadly, there are details:

- different local authorities have different types of election, but constituencies can cross local authority boundares
- some local authorities have wards of different sizes, where larger wards elect two or three councilors
  (eg: [Tendring])
- sometimes ward boundaries are changed, eg: by the [LGBCE]. Not everything is listed on the LGBCE page: Reading
  changed the ward boundaries in 2019, but this isn't listed?!
- Suffolk Coastal and Waveney merged to become East Suffolk, and this changed all the ward boundaries.

The solution to this is to count things by ONS Output Areas (OA), ie: track which elections an OA has participated in.
This is useful because OA all contain approximately the same number of people.

More bad news: OA changed between the 2011 census and 2021 census. The ONS prodive a best-fit mapping from one to the
other.

[Tendring]: https://tdcdemocracy.tendringdc.gov.uk/mgMemberIndex.aspx?FN=WARD&VW=LIST&PIC=0
[LGBCE]: https://www.lgbce.org.uk/all-reviews

# Caveats

- Turnout is ignored: if one ward has high turnout and another low turnout, I'll average them with equal weight
- Numbers are rounded down at several points, so percentages add up to less than 100%.
- I've ignored Scotland, Wales and Northern Ireland.
