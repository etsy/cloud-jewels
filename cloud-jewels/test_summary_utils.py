import unittest
import pandas as pd
import numpy as np
from summary_utils import *

data = {
    "Model": ["Xeon 1234", "AMD 2345", "Xeon 3456"],
    "launch_date": [2014, "2015", "hello"], # test cleans numbers
    "Cores": [2, 2, 1], # used in calculations
    "Total Threads": [7, 2, 3], # used in calculations
    "avg. watts @ active idle": [14, 5, 3], # used in calculations
    "avg. watts @ 100%": [21, 8, 6], # used in calculations
    # we don't really use these fields:
    "Nodes": [4, "5", 7], 
    "Chips": [1, 2, 3],
    "MHz": [100, 200, 150],
    "Total Memory (GB)": [5, 4, 2],
}
test_df = pd.DataFrame(data)

class TestGetSafeFloat(unittest.TestCase):
    def test_remove_commas(self):
        result = get_safe_float("2,000")
        self.assertEqual(2000, result, "removes commas")

    def test_returns_float(self):
        result = get_safe_float("4")
        self.assertTrue(isinstance(result, float), "returns float")
    def leaves_numbers_alone(self):
        result = get_safe_float(5)
        self.assertEqual(5, result, "leaves numbers alone")

class TestCleanNumericField(unittest.TestCase):
    def test_remove_non_numbers(self):
        result = clean_numeric_field("hello")
        self.assertTrue(pd.isna(result), "removes non-numeric values")
    
    def test_returns_a_float(self):
        result = clean_numeric_field("5")
        self.assertTrue(isinstance(result, float), "returns a float")

class TestSafeDivide(unittest.TestCase):
    def test_divides_numbers(self):
        result = safe_divide(10, 5)
        self.assertEqual(2, result, "divides two numbers")

    def test_divides_as_floats(self):
        result = safe_divide(7, 2)
        self.assertEqual(3.5, result, "divides as floats")

    def test_handles_zero_denom(self):
        result = safe_divide(5, 0)
        self.assertEqual(0, result, "handles zero in denominator")

class TestApplyCleaningFxn(unittest.TestCase):
    def test_applies_clean_numeric_field(self):
        copy_df = test_df
        result = apply_cleaning_fxn(copy_df, "Nodes")
        self.assertListEqual([4, 5, 7], result["Nodes"].tolist(), "applies cleaning fxn to row")

class TestCleanNumericFields(unittest.TestCase):
    def test_clean_numeric_fields(self):
        copy_df = test_df
        result = clean_numeric_fields(copy_df)
        # check two separate rows to make sure we've cleaned both 
        self.assertEqual([4, 5, 7], result["Nodes"].tolist(), "cleans Nodes row")
        # since the non-number-like text "hello" is in launch_date, it'll return a NaN which we can't test as equality
        # we're therefore going to test the first two values (2014, "2015") separately from the third value ("hello")
        self.assertEqual([2014, 2015], result["launch_date"].tolist()[:2])
        self.assertTrue(np.isnan(result["launch_date"].tolist()[2]))
        self.assertEqual(["Xeon 1234", "AMD 2345", "Xeon 3456"], result["Model"].tolist(), "does not change text columns")

class TestGetWattsAndThreadStats(unittest.TestCase):
    def test_get_watts_and_thread_stats(self):
        copy_df = test_df
        result = get_watts_and_thread_stats(copy_df)
        # Manually copying the test data into a comment so it's easier to read here
        # "Cores": [2, 2, 1],
        # "Total Threads": [7, 2, 3],
        # "avg. watts @ active idle": [14, 5, 3],
        # "avg. watts @ 100%": [21, 8, 6],

        # watts / thread @ idle
        self.assertEqual([2, 2.5, 1], result["watts per thread idle"].tolist(), "watts per thread at idle calculates correctly")
        # watts / thread @ 100%
        self.assertEqual([3, 4, 2], result["watts per thread max"].tolist(), "watts per thread at 100% calculates correctly")
        # watts / core @ idle
        self.assertEqual([7, 2.5, 3], result["watts per core idle"].tolist(), "watts per core at idle calculates correctly")
        # watts / core @ 100%
        self.assertEqual([10.5, 4, 6], result["watts per core max"].tolist(), "watts per core at 100% calculates correctly")
        # threads / core
        self.assertEqual([3.5, 1, 3], result["threads per core"].tolist(), "threads per core calculates correctly")

class TestCloudJewels(unittest.TestCase):
    def test_cloud_jewels(self):
        result = cloud_jewels(5, 7)
        self.assertEqual(5.8, result, "correctly calculates cloud jewels at default utilization of 40%")

    def test_cloud_jewels_other_utilization(self):
        result = cloud_jewels(5, 7, .75)
        self.assertEqual(6.5, result, "correctly calculates cloud jewels at designated utilization")

class TestGetSummary(unittest.TestCase):
    def test_get_summary(self):
        # Manually copying the test data into a comment so it's easier to read here
        # "Model": ["Xeon 1234", "AMD 2345", "Xeon 3456"],
        # "launch_date": [2014, "2015", "hello"], # test cleans numbers
        # "Cores": [2, 2, 1], # used in calculations
        # "Total Threads": [7, 2, 3], # used in calculations
        # "avg. watts @ active idle": [14, 5, 3], # used in calculations
        # "avg. watts @ 100%": [21, 8, 6], # used in calculations
        # # we don't really use these fields:
        # "Nodes": [4, "5", 7], 
        # "Chips": [1, 2, 3],
        # "MHz": [100, 200, 150],
        # "Total Memory (GB)": [5, 4, 2]
        copy_df = test_df
        result = get_summary(copy_df).to_frame()
        expected = pd.Series({
            "Nodes": 16.0/3.0,
            "Chips": 2.0,
            "MHz": 150.0,
            "Total Memory (GB)": 11.0/3.0,
            "Cores": 5.0/3.0,
            "Total Threads": 4.0,
            "avg. watts @ active idle": 22.0/3.0,
            "avg. watts @ 100%": 35.0/3.0,
            "watts per thread idle": 5.5/3.0,
            "watts per thread max": 3.0,
            "watts per core idle": 12.5/3.0,
            "watts per core max": 20.5/3.0,
            "threads per core": 7.5/3.0,
            "cloud jewels": (5.5/3) + .4*(3 - 5.5/3),
            "minimum year": 2014,
            "maximum year": 2015,
            "median year": 2014.5
        }).to_frame()
        # `eq` will return a dataframe of columns and whether the corresponding rows are the same or not, like:
        #           0
        # Nodes     True
        # Chips     False
        compared = result.eq(expected)
        # We are interested in column "0" -- the list of booleans
        comparison_results = compared[0].tolist()
        # Check that ALL the values are true, meaning our two dataframes matched
        self.assertTrue(all(comparison_results))

class TestCleanSpecData(unittest.TestCase):
    def test_clean_spec_data(self):
        columns = [
            "Hardware Vendor\nTest Sponsor", 
            "System\nEnclosure (if applicable)", 
            "Nodes", 
            "JVM Vendor", 
            "CPU Description", 
            "MHz", 
            "Chips", 
            "Cores", 
            "Total\nThreads", 
            "Total\nMemory (GB)", 
            "ssj_ops\n@ 100%", 
            "avg. watts\n@ 100%", 
            "avg. watts\n@ active idle", 
            "Result\n(Overall ssj_ops/watt)"
        ]
        rows = [
            [
                "ASUSTeK Computer Inc.", 
                "RS720-E9/RS8\nDec 6, 2018 | HTML | Text",
                1,
                "Oracle Corporation",
                "Intel Xeon Platinum 8180", 
                2500,
                2,
                56, 
                112, 
                192,
                "5,386,401",
                385,
                48.2,
                "12,727"
            ],
            [
                "ASUSTeK Computer Inc.",
                "RS720Q-E9-RS8\nNone\nMay 10, 2019 | HTML | Text", 
                4,
                "Oracle Corporation",
                "Intel Xeon Platinum 8176M",
                2100,
                8,
                224,
                448,
                768,
                "19,257,841", 
                "1,417",
                193,
                "11,935"
            ],
            [
                "Hardware Vendor\nTest Sponsor", 
                "System\nEnclosure (if applicable)", 
                "Nodes", 
                "JVM Vendor", 
                "CPU Description", 
                "MHz", 
                "Chips", 
                "Cores", 
                "Total\nThreads", 
                "Total\nMemory (GB)", 
                "ssj_ops\n@ 100%", 
                "avg. watts\n@ 100%", 
                "avg. watts\n@ active idle", 
                "Result\n(Overall ssj_ops/watt)"
            ],
            [
                "Dell Inc.",
                "PowerEdge R620 (Intel Xeon E5-2660, 2.20 GHz)\nSep 5, 2012 | HTML | Text", 
                1,
                "IBM Corporation", 
                "Intel Xeon E5-2660 2.20 GHz (Intel Turbo Boost Technology up to 3.00 GHz)",
                2200, 
                2,
                16,
                32,
                24,
                "NC",
                "NC",
                "NC",
                "NC",
            ],
        ]
        expected_columns = [
            "Nodes", 
            "processor", 
            "MHz", 
            "Chips", 
            "Cores", 
            "Total Threads", 
            "Total Memory (GB)", 
            "avg. watts @ 100%", 
            "avg. watts @ active idle", 
            "launch_date",
        ]
        expected_rows = [
            [
                1,
                "Intel Xeon Platinum 8180", 
                2500,
                2,
                56, 
                112, 
                192,
                385,
                48.2,
                "2018",
            ],
            [
                4,
                "Intel Xeon Platinum 8176M",
                2100,
                8,
                224,
                448,
                768,
                "1,417",
                193, 
                "2019",
            ],
        ]
        result_df = clean_spec_data(pd.DataFrame(rows, columns = columns))
        expected_df = pd.DataFrame(expected_rows, columns = expected_columns)
        # `eq` will return a dataframe of columns and whether the corresponding rows are the same or not, like:
        # Nodes     processor   MHz     Chips
        # -------|------------|------|--------
        # False     True        True    True
        # True      True        True    False
        # The above output would indicate that the values for Nodes in the first row do not match, and the values for Chips in the second row do not match
        compared = result_df.eq(expected_df)
        # DataFrame.all() tests that all values in each column are True
        # Output of compared.all() will be one row for each column and whether all its values are True
        # Nodes     True
        # processor True
        # MHz       True
        # Chips     False # <-- would indicate that not all rows in `Chips` are True, meaning there's a difference between the two dataframes somewhere in this column
        # Finally, wrap this output DF in all(), which will check that the values in each row are True, i.e. our two dataframes match entirely
        self.assertTrue(all(compared.all()))

class TestGetFamilySpecData(unittest.TestCase):
    def test_get_family_spec_data(self):
        # Intentionally using empty strings for missing values because pandas's `eq` will not compare Nones
        spec_columns = ["brand", "make", "model", "moniker", "version", "watts"]
        spec_rows = [
            ["xeon", "silver", 2380, "l", "v3", 7],
            ["epyc", "", 7790, "", "", 9],
            ["opteron", "platinum", 460, "", "", 6],
        ]
        mock_spec = pd.DataFrame(spec_rows, columns=spec_columns)
        family_columns = ["name", "brand", "make", "model", "moniker", "version"]
        family_rows = [
            ["first", "xeon", "silver", 2380, "l", "v3"],
            ["second", "epyc", "", 7790, "", ""],
            ["third","pentium", "platinum", 460, "", ""],
        ]
        mock_family = pd.DataFrame(family_rows, columns=family_columns)
        expected_columns = ["brand", "make", "model", "moniker", "version", "watts", "name"]
        expected_rows = [
            ["xeon", "silver", 2380, "l", "v3", 7, "first"],
            ["epyc", "", 7790, "", "", 9, "second"],
        ]
        expected = pd.DataFrame(expected_rows, columns=expected_columns)
        result = get_family_spec_data(mock_family, mock_spec)
        # `eq` will return a dataframe of columns and whether the corresponding rows are the same or not, like:
        # name      brand   make    model
        # -------|--------|-------|--------
        # False     True    True    True
        # True      True    True    False
        # The above output would indicate that the values for processor in the first row do not match, and the values for model in the second row do not match
        compared = result.eq(expected)
        # DataFrame.all() tests that all values in each column are True
        # Output of compared.all() will be one row for each column and whether all its values are True
        # name   True
        # brand  True
        # make   True
        # model  False # <-- would indicate that not all rows in `model` are True, meaning there's a difference between the two dataframes somewhere in this column
        # Finally, wrap this output DF in all(), which will check that the values in each row are True, i.e. our two dataframes match entirely
        self.assertTrue(all(compared.all()))

class TestCleanGcpMachineSeriesData(unittest.TestCase):
    def test_clean_gcp_machine_series_data(self):
        mock_series_columns = ["Machine series", "vCPUs", "Memory (per vCPU)", "Processors", "Custom VMs", "Local SSDs", "Sustained-use discounts", "Preemptible VMs"]
        mock_series_rows = [
            ["E2 General-purpose", 3, 10, "Skylake\nBroadwell", "Yes", "No", "No", "Yes"],
            ["E2 Shared-core", 4, 8, "Broadwell\nAMD EPYC Rome", "No", "Yes", "Yes", "No"],
            ["N2", 3, 7, "Skylake\nIce Lake", "No", "Yes", "No", "No"],
        ]
        mock_series = pd.DataFrame(mock_series_rows, columns=mock_series_columns)
        expected_columns = ["type", "family"]
        expected_rows = [
            ["E2", "Skylake"],
            ["E2", "Broadwell"],
            ["E2", "AMD EPYC Rome"],
            ["N2", "Skylake"],
            ["N2", "Ice Lake"],
        ]
        expected = pd.DataFrame(expected_rows, columns=expected_columns)
        # We'll be dropping a duplicate row for "E2 | Broadwell" since it's listed twice, so we have to remove a row and re-index
        expected.index = [0,1,3,4,5]
        result = clean_gcp_machine_series_data(mock_series)
        # `eq` will return a dataframe of columns and whether the corresponding rows are the same or not, like:
        # type      family
        # -------|----------
        # False     True   
        # True      True    
        # The above output would indicate that the values type in the first row do not match
        compared = result.eq(expected)
        # DataFrame.all() tests that all values in each column are True
        # Output of compared.all() will be one row for each column and whether all its values are True
        # type   True
        # family  False # <-- would indicate that not all rows in `family` are True, meaning there's a difference between the two dataframes somewhere in this column
        # Finally, wrap this output DF in all(), which will check that the values in each row are True, i.e. our two dataframes match entirely
        self.assertTrue(all(compared.all()))
        

        


# TODO: combine get_summary_df into get_summary
# TODO: combine processor fxn at top into parse_out_processors

if __name__ == "__main__":
    unittest.main()
