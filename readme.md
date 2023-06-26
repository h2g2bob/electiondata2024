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
- sometimes ward boundaries are changed. This is normally done by the [LGBCE], although not everything is included
  on their website (eg: Reading).
- District councils get merged or changed. For example [Cumbria County Council was replaced by two unitary authorities],
  which also changed all the ward boundaries. You can see the effect of this where Carlisle constituency includes
  elections from both Carlisle District Council and Cumberland Unitary Authority.

The solution to this is to count things by ONS Output Areas (OA), ie: track which elections an OA has participated in.
This is useful because OA all contain approximately the same number of people.

More bad news: OA changed between the 2011 census and 2021 census. The ONS prodive a best-fit mapping from one to the
other.

[Tendring]: https://tdcdemocracy.tendringdc.gov.uk/mgMemberIndex.aspx?FN=WARD&VW=LIST&PIC=0
[LGBCE]: https://www.lgbce.org.uk/all-reviews
[Cumbria County Council was replaced by two unitary authorities]: https://en.wikipedia.org/wiki/2019%E2%80%932023_structural_changes_to_local_government_in_England#Cumbria

# Caveats

- Turnout is ignored: if one ward has high turnout and another low turnout, I'll average them with equal weight
- People sometimes vote differently at local elections and general elections, for example [Gainsborough] has a Lib Dem
  council and Labour MP.
- Numbers are rounded down in some intermediate stages, so percentages can add up to less than 100%.
- I've ignored Scotland, Wales and Northern Ireland.

[Gainsborough]: https://en.wikipedia.org/wiki/Gainsborough_(UK_Parliament_constituency)
