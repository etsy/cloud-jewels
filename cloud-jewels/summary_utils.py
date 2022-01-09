import pandas as pd
from processor_parser import generate_processor

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

# Make sure all dates are floats (one of them is the text "HTML" :sigh:)
def clean_date_field(row):
    launch_date = row["launch_date"]
    try:
        float(launch_date)
    except ValueError:
        launch_date = "NaN"
    return float(launch_date)

# Remove commas from numbers :grimacing:
def get_safe_float(val):
    return float(str(val).replace(",",""))

# Given a row, return the watts per [thread or core] at [idle or 100%]
#def watts_per_unit_util(row, unit, util):
def watts_per_unit_util(unit_val, util_val):
    if get_safe_float(unit_val) > 0:
        return round(get_safe_float(util_val)/get_safe_float(unit_val),2)
    else:
        return 0

def clean_node_field(row):
    nodes = row["Nodes"]
    try:
        float(nodes)
    except ValueError:
        nodes = "NaN"
    return float(nodes)

def clean_numeric_field(field_value):
    try:
        float(field_value)
    except ValueError:
        field_value = "NaN"
    return float(field_value)

# Get the threads per core ratio
# This is almost always 1 or 2
# But since 1 vCPU is ROUGHLY == 1 thread, this is a good ratio to know
def threads_per_core(row):
    if get_safe_float(row["Cores"]) > 0:
        return round(get_safe_float(row["Total Threads"])/get_safe_float(row["Cores"]), 2)
    else:
        return 0

# Add some summary columns:
# (we consider 1 thread to be *close enough* to 1 vCPU)
#   - watts per thread at idle (we use this to calculate Cloud Jewels)
#   - watts per thread at max (we use this to calculate Cloud Jewels)
#   - watts per core at idle (we don't use this but it's good to look at)
#   - watts per core at max (we don't use this but it's good to look at)
#   - threads per core (this is almost always either 1 or 2, but it varies, so it's good to look at the avg)
#   - clean up the date field while we're munging
def get_watts_and_thread_stats(df):
    df["launch_date"] = df.apply(lambda row: clean_date_field(row), axis=1)
    df["Nodes"] = df.apply(lambda row: clean_numeric_field(row["Nodes"]), axis=1)
    df["Cores"] = df.apply(lambda row: clean_numeric_field(row["Cores"]), axis=1)
    df["Chips"] = df.apply(lambda row: clean_numeric_field(row["Chips"]), axis=1)
    df["MHz"] = df.apply(lambda row: clean_numeric_field(row["MHz"]), axis=1)
    df["watts per thread idle"] = df.apply(lambda row: watts_per_unit_util(row["Total Threads"], row["avg. watts @ active idle"]), axis=1)
    df["watts per thread max"] = df.apply(lambda row: watts_per_unit_util(row["Total Threads"], row["avg. watts @ 100%"]), axis=1)
    df["watts per core idle"] = df.apply(lambda row: watts_per_unit_util(row["Cores"], row["avg. watts @ active idle"]), axis=1)
    df["watts per core max"] = df.apply(lambda row: watts_per_unit_util(row["Cores"], row["avg. watts @ 100%"]), axis=1)
    df["threads per core"] = df.apply(lambda row: threads_per_core(row), axis=1)
    return df

# cloud jewels (estimated watts per hour) = watts per hour when idle + 
# average utilization * (watts per hour at 100% utilization - watts per hour when idle)
def cloud_jewels(watts_idle, watts_max, avg_util = .5):
    return watts_idle + avg_util*(watts_max - watts_idle)

# generate a set of summary stats + cloud jewels for this set of servers
def get_summary(df):
    df_with_watts = get_watts_and_thread_stats(df)
    summary = df_with_watts[["Nodes", "Chips", "MHz", "Total Memory (GB)", "Cores", "Total Threads", "avg. watts @ active idle", "avg. watts @ 100%","watts per thread idle", "watts per thread max", "watts per core idle", "watts per core max", "threads per core"]].mean()
    summary["cloud jewels"] = cloud_jewels(summary["watts per thread idle"], summary["watts per thread max"])
    summary["minimum year"] = df["launch_date"].min()
    summary["maximum year"] = df["launch_date"].max()
    summary["median year"] = df["launch_date"].median()
    return summary

