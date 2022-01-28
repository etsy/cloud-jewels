import pandas as pd
from processor_parser import generate_processor
from config import AMD_FAMILIES, AVG_INDUSTRY_SERVER_UTILIZATION

# The fields we parse out about a processor and use to join spec data to machine family data
PROCESSOR_UNION_FIELDS = ["brand","make","model","moniker","version"]

# All numeric fields used in calculations -- we need to make sure these are sanitized
NUMERIC_FIELDS = ["launch_date", "Nodes", "Cores", "Chips", "MHz", "Total Threads", "Total Memory (GB)", "avg. watts @ active idle", "avg. watts @ 100%"]


# Parse important fields out of processor name column
# We use these fields to join SPEC data to processor families
def parse_description(df):
    processor = generate_processor(str(df["processor"]))
    df["company"] = processor.company
    df["brand"] = processor.brand
    df["make"] = processor.make
    df["model"] = processor.model
    df["moniker"] = processor.moniker
    df["version"] = processor.version
    return df

# Remove commas from numbers :grimacing:
def get_safe_float(val):
    return float(str(val).replace(",",""))

# Remove non-numbers
def clean_numeric_field(field_value):
    try:
        float(field_value)
    except ValueError:
        field_value = "NaN"
    return float(field_value)

# Make sure we have numbers, and don't divide by 0
def safe_divide(num, den):
    if get_safe_float(den) > 0:
        return round(get_safe_float(num)/get_safe_float(den), 2)
    else:
        return 0

def apply_cleaning_fxn(df, field):
    df[field] = df.apply(lambda row: clean_numeric_field(row[field]), axis=1)
    return df

def clean_numeric_fields(df):
    for field in NUMERIC_FIELDS:
        df = apply_cleaning_fxn(df, field)
    return df

# Add some summary columns:
# (we consider 1 thread to be *close enough* to 1 vCPU)
#   - watts per thread at idle (we use this to calculate Cloud Jewels)
#   - watts per thread at max (we use this to calculate Cloud Jewels)
#   - watts per core at idle (we don't use this but it's good to look at)
#   - watts per core at max (we don't use this but it's good to look at)
#   - threads per core (this is almost always either 1 or 2, but it varies, so it's good to look at the avg)
#   - clean up the date field while we're munging
def get_watts_and_thread_stats(df):
    df["watts per thread idle"] = df.apply(lambda row: safe_divide(row["avg. watts @ active idle"], row["Total Threads"]), axis=1)
    df["watts per thread max"] = df.apply(lambda row: safe_divide(row["avg. watts @ 100%"], row["Total Threads"]), axis=1)
    df["watts per core idle"] = df.apply(lambda row: safe_divide(row["avg. watts @ active idle"], row["Cores"]), axis=1)
    df["watts per core max"] = df.apply(lambda row: safe_divide(row["avg. watts @ 100%"], row["Cores"]), axis=1)
    df["threads per core"] = df.apply(lambda row: safe_divide(row["Total Threads"], row["Cores"]), axis=1)
    return df

# cloud jewels (estimated watts per hour) = watts per hour when idle + 
# average utilization * (watts per hour at 100% utilization - watts per hour when idle)
def cloud_jewels(watts_idle, watts_max, avg_util = AVG_INDUSTRY_SERVER_UTILIZATION):
    return watts_idle + avg_util*(watts_max - watts_idle)

# generate a set of summary stats + cloud jewels for this set of servers
def get_summary(df):
    df_safe_numbers = clean_numeric_fields(df)
    df_with_watts = get_watts_and_thread_stats(df_safe_numbers)
    summary = df_with_watts[["Nodes", "Chips", "MHz", "Total Memory (GB)", "Cores", "Total Threads", "avg. watts @ active idle", "avg. watts @ 100%", "watts per thread idle", "watts per thread max", "watts per core idle", "watts per core max", "threads per core"]].mean()
    summary["cloud jewels"] = cloud_jewels(summary["watts per thread idle"], summary["watts per thread max"])
    summary["minimum year"] = df["launch_date"].min()
    summary["maximum year"] = df["launch_date"].max()
    summary["median year"] = df["launch_date"].median()
    return summary

def clean_spec_data(raw_data):

	# Remove new lines from column names
	raw_data.columns = [x.replace("\n", " ") for x in raw_data.columns.to_list()]

	# Remove repeated header rows mixed in with the data
	#   These look like either NA values in the "Hardware Vendor Test Sponsor" column
	#   or the header text ("Hardware Vendor Test Sponsor") in that column
	raw_data.drop(raw_data[raw_data["Hardware Vendor Test Sponsor"].isna()].index, inplace=True)
	raw_data.drop(raw_data[raw_data["Hardware Vendor Test Sponsor"] == "Hardware Vendor\nTest Sponsor"].index, inplace=True)

	# Remove lines without energy data (have "NC" in the fields we care about)
	raw_data.drop(raw_data[raw_data["avg. watts @ 100%"] == "NC"].index, inplace=True)

	# Extract date from the System Enclosure field
	#   Looks like:
	#       PowerEdge M915
	#       Dell PowerEdge M1000e
	#       Aug 2, 2011 | HTML | Text
	# We just want that year on the third line, so we split on | and take the first piece of that split.
	# So we'll have:
	#       PowerEdge M915
	#       Dell PowerEdge M1000e
	#       Aug 2, 2011 
	raw_data[["info_and_date","html","text"]] = raw_data["System Enclosure (if applicable)"].str.split("|",expand=True)
	# Then we'll snag the last 4 digits starting one digit from the end because the last 5 digits look like "2009 "
	raw_data["launch_date"] = raw_data["info_and_date"].str[-5:-1]

	# Rename description column for consistency across spreadsheets
	raw_data.rename(columns={"CPU Description":"processor"}, inplace=True)

	# Drop columns we don't need
	raw_data.drop(columns=["Hardware Vendor Test Sponsor", "System Enclosure (if applicable)", "JVM Vendor", "ssj_ops @ 100%", "Result (Overall ssj_ops/watt)", "info_and_date", "html", "text"], inplace=True)

	return raw_data

def parse_out_processors(clean_data):
    # Parse processor info out of the description
    return clean_data.apply(parse_description, axis=1)

def get_summary_df(data, family_name):
	summary = get_summary(data)
	summary.name = family_name
	return summary.to_frame()

def get_family_spec_data(family_data, spec_data):

    # Get the intersection of this family's data and the SPEC data
    return pd.merge(spec_data, family_data, on=PROCESSOR_UNION_FIELDS, how='inner')

def clean_gcp_machine_series_data(gcp_series):

	# Split out the series name from the text, e.g. from "E2* General-purpose" get "E2*"
	gcp_series[["machine","text"]] = gcp_series["Machine series"].str.split(" ",1,expand=True)

	# Strip unwanted characters off the series name, e.g. from "E2*" get "E2"
	gcp_series["type"] = gcp_series["machine"].str.extract(r'([0-9a-zA-Z]+)')

	# Drop the columns we don't need
	gcp_series = gcp_series.drop(columns=["Machine series", "vCPUs", "Memory (per vCPU)", "Custom VMs", "Local SSDs", "Sustained-use discounts", "Preemptible VMs", "machine", "text"])

	# Explode the list of relevant processors into rows
	# E.g. We start with a table that looks like this:
	#   type    | Processors
	#   --------|------------------------------------------
	#   E2      | Skylake\nBroadwell\nHaswell\nAMD EPYC Rome
	# We want instead:
	#   type    | processor
	#   --------|--------------
	#   E2      | Skylake
	#   E2      | Broadwell
	#   E2      | Haswell
	#   E2      | AMD EPYC Rome
	# If we were using a newer version of pandas, we could use "explode", but since we're not
	# we instead use [this black magic](https://stackoverflow.com/a/62211815/14042921)
	#   cleaned.set_index(["type"])["Processors"].astype(str).str.split('\n', expand=True).stack().reset_index(level=-1, drop=True).reset_index(name='processor')
	# 
	# Which means: 
	#   - Use the values from the "type" column as row names (the index)
	#   - Then take the "Processors" column, treat it as a string, and split it on "\n" to expand to new columns
	#   - "stack" this so that we get a multi-level index:
	#       E.g. go from this table: 
	#           (Note: we have 5 columns because that's the max # of families associated with 
	#           any given series -- N1 has 5 possible machine families)
	#           type (index)    | 0         | 1         | 2         | 3             | 4
	#           ----------------|-----------|-----------|-----------|---------------|-----------
	#           E2              | Skylake   | Broadwell | Haswell   | AMD EPYC Rome | None
	#           N2              | Skylake   | Ice Lake  | None      | None          | None
	#       To this weird table: 
	#           type (index)    |   |
	#           ----------------|---|---------
	#           E2              | 0 | Skylake
	#                           | 1 | Broadwell
	#                           | 2 | Haswell
	#                           | 3 | AMD EPYC Rome
	#           N2              | 0 | Skylake
	#                           | 1 | Ice Lake
	#   - Reset the index: in this case, reset the level 1 index ("type" is level 0, the numerals are level 1) and drop it
	#       Since we now only have a single level of indexing, the "type" column no longer has nesting inside it, and thus our table looks like this:
	#           type (index)    |
	#           ----------------|---------
	#           E2              | Skylake
	#           E2              | Broadwell
	#           E2              | Haswell
	#           E2              | AMD EPYC Rome
	#           N2              | Skylake
	#           N2              | Ice Lake
	#   - Reset the index again, officially bringing the processor families into their own column named "family"
	gcp_series = gcp_series.set_index(["type"])["Processors"].astype(str).str.split('\n', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='family')

	# Drop duplicate rows (we have duplicates because E2 and N1 list both "General-purpose" and 
	#   "Shared-core" sets of families, but for each the two lists are the same
	return gcp_series.drop_duplicates()
