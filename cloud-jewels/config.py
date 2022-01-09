
# USER-DEFINED VARIABLES:

# If you named your spreadsheet or tabs or files differently or have them in another directory, you can set those here:

# by default, the script will read IN raw data from this directory:
BASE_FILEPATH = "./data/"

# The script assumes that all the raw data files are named similarly -- with the spreadsheet name then " - " then the tab name, and that they end in CSV.
# For example, if the spreadsheet is named "Raw Data" and the tab containing data about the Sandy Bridge family is named "sandy", and you set those variables but don't change the FILENAME_DELIMITER, the script will look for the Sandy Bridge data in a file called `Raw Data - sandy.csv`.
# I.e. the filenames are generated as:
# BASE_FILENAME + FILENAME_DELIMITER + SPECIFIC_TAB_NAME + .csv
BASE_FILENAME = "Cloud Jewels Raw Data"
FILENAME_DELIMITER = " - "
SPEC = "SPEC"
SANDY_BRIDGE = "Sandy Bridge"
IVY_BRIDGE = "Ivy Bridge"
HASWELL = "Haswell"
BROADWELL = "Broadwell"
SKYLAKE = "Skylake"
CASCADE_LAKE = "Cascade Lake"
ICE_LAKE = "Ice Lake"
AMD_EPYC_ROME = "AMD EPYC Rome"
AMD_EPYC_MILAN = "AMD EPYC Milan"
MACHINE_FAMILIES = "machine families"

OUTPUT_DIRECTORY = "./results/"

# -------------------------------------------------

# GOOGLE'S FAMILIES (subject to change each year)
GOOGLE_MACHINE_FAMILIES = [
    "AMD EPYC Milan",
    "AMD EPYC Rome",
    "Haswell",
    "Broadwell",
    "Cascade Lake",
    "Ice Lake",
    "Skylake",
    "Ivy Bridge",
    "Sandy Bridge",
]

# Currently the format of the AMD family data is different than Intel data
AMD_FAMILIES = [
    "AMD EPYC Milan",
    "AMD EPYC Rome",
]	
