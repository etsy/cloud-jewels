# Generating Cloud Jewels

TODO: goals, background?

This README guides a user through generating Cloud Jewels metrics for Google's server classes based on what we know from the SPEC power database, Google's documentation, and the ever-veridical Wikipedia (to categorize server models into server families).


## The Method

The [SPEC power database](https://www.spec.org/power_ssj2008/results/power_ssj2008.html) provides information about nearly 700 servers' power consumption at both idle and 100% utilization. The database has a broad range of servers in it, not all of which are datacenter-grade or likely to be similar to Google's servers.

Google provides [information about which server families each class of its servers are composed of](https://cloud.google.com/compute/docs/machine-types#machine_type_comparison). For example, the chart says that the `E2` machine series is composed of processors from the `Skylake`, `Broadwell`, `Haswell`, and `AMD EPYC Rome` families. 

We know from Wikipedia [which server models are associated with a given server family](https://en.wikipedia.org/wiki/List_of_Intel_Xeon_processors). We know that Google uses datacenter-grade servers, so we can ignore any servers in the SPEC database that are neither Intel Xeon nor AMD EPYC, as these are the datacenter-grade server brands from Intel and AMD.

Given that we know which processor models are associated with each family of server (e.g. "Intel Xeon Platinum 8380" is part of the "Ice Lake" family), we can filter the SPEC power database per each server family, giving us a set of power records that pertain to servers within a given family. Then we can use each family's set of server samples to generate a Cloud Jewels coefficient for each server family. 

Once we have Cloud Jewels coefficients for each server family, since we know that a given Google class of servers could be any of several server families, we average the Cloud Jewels coefficients for the possible families to get a Cloud Jewels coefficient for each server class. E.g. Since we know that `E2` machines could use `Skylake`, `Broadwell`, `Haswell`, or `AMD EPYC Rome` families, we average each of these families' Cloud Jewels coefficients to get a coefficient for all `E2` servers.

Our billing data _roughly_ breaks down our CPU usage according to which class of servers we have requested, so we're able to apply these server-class Cloud Jewels coefficients to our line items to generate total Cloud Jewels (kWh). E.g. If we used 5 hours of E2 servers, and E2s have a Cloud Jewels coefficient of 2 W, then we have used 10 Wh of energy.

## How to reproduce 2021 Cloud Jewel coefficients

We'll do this in a few steps:
1. Fetch raw data from a few different sources, capture it into a spreadsheet, download it as CSVs.
2. (Optional) Update any filename paths or other variables in `config.py`. 
3. Run the `generate_cloud_jewels.py` script which will: 
    - read in the raw data
    - parse out processor model, make, version, moniker from the SPEC data and the lists of Intel Xeon and AMD EPYC servers
    - join each set of servers in a server family to the SPEC database to pull out relevant rows for each server family
    - calculate Cloud Jewels for each server family (`Skylake`, `Ivy Bridge`, etc.)
    - calculate Cloud Jewels for each Google machine series/class (`E2`, 'N1`, etc.)
    - save power entries relevant to each server family to new CSVs
    - save summary stats about each server family's server to new CSV
    - save the final Cloud Jewels per Google machine series to new CSV

*Note:* The steps listed below are opinionated and explicit about what tools to use, filenames to set, etc. This is to make this work easily replicable, not because these are the only ways to do these tasks. If you're repeating this process, feel free to use your own tools and variable names -- there's info at the end about setting filepaths and such in the config file.

### Create a spreadsheet

Make a new Google spreadsheet, and name it `Cloud Jewels Raw Data`. You'll be copying and pasting all your source data into tabs in this sheet and then downloading each sheet in CSV format.

### Fetch SPEC power data

First we'll collect power consumption data about various servers from the [SPEC power database](https://www.spec.org/power_ssj2008/results/power_ssj2008.html). There's no way to easily download this data, so copy and paste it into a Google spreadsheet, and name the tab `SPEC`. Don't modify it -- the script will handle removing extra header rows and such.

While on this tab, go to File > Download > Comma Separated Values (.csv). It will automatically download this sheet into your Downloads folder.

### Fetch server family data from Wikipedia
As of Jan 4, 2021, the complete set of server families that Google claims to use are:
- Sandy Bridge
- Ivy Bridge
- Haswell
- Broadwell
- Skylake
- Cascade Lake
- Ice Lake
- AMD EPYC Rome
- AMD EPYC Milan
(all the non-AMD families are Intel)

Intel server families and their associated server models are listed [here](https://en.wikipedia.org/wiki/List_of_Intel_Xeon_processors).
AMD server families and their associated server models are listed [here](https://en.wikipedia.org/wiki/Epyc#Products).

Copy each list of servers and paste it into a new tab of the `Cloud Jewels Raw Data` spreadsheet. Name each tabas listed above (e.g. the tab containing the list of Sandy Bridge servers should be named `Sandy Bridge`, and the tab containing the AMD EPYC Rome servers should be named `AMD EPYC Rome`. *Note:* We're intentionally using the exact names that Google uses to avoid munging names later when we join to Google's data.

The data on each of the Intel tabs should just be a single column of model names. The data on the two AMD tabs should be a table with more info. Don't change the headers -- the script assumes that the first row is a header row and that it has a column named `Model`.

For each of these server family tabs, while on the given tab, go to File > Download > Comma Separated Values (.csv). It will automatically download this sheet into your Downloads folder.

### Fetch Google's documentation on machine series and server families

Google [provides a list of what server familes each machine series can be made up of](https://cloud.google.com/compute/docs/machine-types#machine_type_comparison). Copy this chart and paste it into a tab of the `Cloud Jewels Raw Data` spreadsheet. Name the tab `GCP Machine Series`.

While on this tab, go to File > Download > Comma Separated Values (.csv). It will automatically download this sheet into your Downloads folder.

### Move the downloaded CSVs or update config file

When you run the script, it'll need to know where your downloaded data is so that it can read it in. The script currently defaults to looking for data in a folder named `data` within its same directory (i.e. if the script is in `~/development/cloud-jewels` then it will expect the raw data CSVs to be in `~/development/cloud-jewels/data`. If you'd prefer to have the script look for your raw CSVs elsewhere, you can update the `base\_filepath` variable in `config.py`. If you changed the names of the downloaded files or did not use the exact names suggested here, you can also provide individual filenames for the CSVs in `config.py`.

## Generate Cloud Jewels with the script

In the same directory that the script `generate\_cloud\_jewels.py` is in, run:

```
TODO: venv n shit
python generate_cloud_jewels.py
```

This will output several CSVs into a new folder called `results`. The file with the Cloud Jewel coefficients for each Google machine series will be called `cloud\_jewels\_per\_series.csv`. Use these coefficients to apply to your billing data.
