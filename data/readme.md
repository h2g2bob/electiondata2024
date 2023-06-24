# The data

Order of running scripts:

1. run `ons_output_areas` and `ons_ward_to_blah`
2. run `democlub_results`
3. run `materialized_views`
4. run `postcode_to_ward` (if you want postcode lookups)

For each subdirectory:

* Get the datafiles described in the readme, probably in `csv` format and put
  them in the subdirectory
* Run the `.py` file (in the subdirectory)
* The output is a `data.sqlite3` file in this directory (not the subdirectory)
