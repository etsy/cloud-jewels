import pandas as pd
from summary_utils import get_summary
from config import *
from generate_cloud_jewels import *

# Generate the spec filepath from its pieces
spec_filepath = "{}{}{}{}.csv".format(BASE_FILEPATH, BASE_FILENAME, FILENAME_DELIMITER, SPEC)

# Get a dataframe of cleaned spec data with crucial server model information parsed out
cleaned_spec = clean_spec_data(spec_filepath)
parsed_spec = parse_out_processors(cleaned_spec)

# Save to csv for inspection
parsed_spec.to_csv("{}/{}{}Parsed.csv".format(OUTPUT_DIRECTORY, SPEC, FILENAME_DELIMITER), index=False)

# Generate summary stats & cloud jewels
spec_summary = get_summary_df(parsed_spec, SPEC)
spec_summary.to_csv("{}/{}{}Summary.csv".format(OUTPUT_DIRECTORY, SPEC, FILENAME_DELIMITER), index=True)

# Begin a dataframe of summary results which we'll add each family's summary stats to
cj_summary_df = spec_summary

### Find the rows from SPEC that are relevant to this processor family:
for family in GOOGLE_MACHINE_FAMILIES:

	# Generate the spec filepath from its pieces
	family_filepath = "{}{}{}{}.csv".format(BASE_FILEPATH, BASE_FILENAME, FILENAME_DELIMITER, family)

	# Get a dataframe of cleaned spec data with crucial server model information parsed out
	cleaned_family = clean_family_data(family_filepath, family)
	parsed_family = parse_out_processors(cleaned_family)

	# Save to csv for inspection
	parsed_family.to_csv("{}/{}{}Parsed.csv".format(OUTPUT_DIRECTORY, family, FILENAME_DELIMITER), index=False)

	# Get the intersection of this family's data and the SPEC data
	relevant_entries = get_family_spec_data(parsed_spec, parsed_family)

	# Write the relevant matching rows to csv to inspect
	relevant_entries.to_csv("{}/{}{}Entries.csv".format(OUTPUT_DIRECTORY, family, FILENAME_DELIMITER), index=False)

	# Generate summary stats & cloud jewels
	family_summary_df = get_summary_df(relevant_entries, family)

	# Save this family's summary to CSV for inspection
	family_summary_df.to_csv("{}/{}{}Summary.csv".format(OUTPUT_DIRECTORY, family, FILENAME_DELIMITER), index=True, header=False)

	# Merge this family's summary data to all the others we've generated
	cj_summary_df = cj_summary_df.join(family_summary_df)

# Save the whole summary of all families to CSV
cj_summary_df.to_csv("{}/All Summary.csv".format(OUTPUT_DIRECTORY), index=True)

#### Generate Cloud Jewels for each GCP machine series using family data

# Read in the CSV of machine series data
gcp_series_filepath = "{}{}{}{}.csv".format(BASE_FILEPATH, BASE_FILENAME, FILENAME_DELIMITER, "GCP Machine Series")

gcp_series = clean_gcp_machine_series_data(gcp_series_filepath)

# Save the cleaned GCP Machine Series data to CSV for inspection
gcp_series.to_csv("{}/GCP Machine Series Summary.csv".format(OUTPUT_DIRECTORY), index=False)

cj_summary = cj_summary_df.loc["cloud jewels"]
cj_summary = cj_summary.to_frame()
cj_summary = cj_summary.reset_index().rename(columns={"index":"family"})

# Get just the Cloud Jewels for each processor family
#cj = pd.DataFrame({"family":["AMD EPYC Milan","AMD EPYC Rome","Haswell", "Broadwell", "Cascade Lake", "Ice Lake", "Skylake", "Ivy Bridge", "Sandy Bridge"], "cloud jewels": [1.15, 1.05, 2.2325, 1.81, 2.32, 2.35,2.34, 3.425,4.8375]})

# Merge our dataset of GCP Series : Processor Family with our dataset of Processor Family : Cloud Jewels
# This should give us a table like:
#   type    | family        | cloud jewels
#   --------|---------------|-------------
#   E2      | Skylake       | 2.0
#   E2      | Broadwell     | 2.1
#   E2      | Haswell       | 1.9
#   E2      | AMD EPYC Rome | 2.2
#   N2      | Skylake       | 2.0
#   N2      | Ice Lake      | 1.8
cj_to_series = gcp_series.merge(cj_summary)

# Group by GCP series and get the mean Cloud Jewels for each series
# (Since we grouped by, again we have to reset our average cloud jewels "column" and name it)
avg_cj_per_series = cj_to_series.groupby("type")["cloud jewels"].mean().reset_index(name="cloud jewels")

# Write this final GCP series : average Cloud Jewels mapping to CSV for use against our billing data 
avg_cj_per_series.to_csv("{}/Cloud Jewels per Machine Series.csv".format(OUTPUT_DIRECTORY), index=False)

