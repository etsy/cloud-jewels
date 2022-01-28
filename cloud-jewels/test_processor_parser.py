import unittest
from processor_parser import *

class TestSafeSearch(unittest.TestCase):
    def test_safe_search(self):
        reg = r"some|string|test"
        check = "is there some string here?"
        actual = safe_search(reg, check)
        self.assertEqual("some", actual)

class TestRemoveJunk(unittest.TestCase):
    def test_remove_junk(self):
        test_str = "dell xeon 2345 cpu 5 processor"
        actual = remove_junk(test_str)
        self.assertEqual(" xeon 2345  5 ", actual)

class TestSplitOffParents(unittest.TestCase):
    def test_split_off_parens(self):
        test_str = "important (not important)"
        actual = split_off_parens(test_str)
        self.assertEqual("important ", actual)

class TestCleanDescription(unittest.TestCase):
    def test_clean_description(self):
        test_str = "Intel Xeon 2345 CPU 5 (@ 4 GHz)"
        actual = clean_description(test_str)
        self.assertEqual("intel xeon 2345  5 ", actual) 

class TestGenerateProcessor(unittest.TestCase):
    def extract_processor_pieces(self, processor):
        return [
            processor.original_description,
            processor.brand,
            processor.model,
            processor.moniker,
            processor.version
        ]
    def test_generate_processor(self):
        test_cases = [
            "2.6 GHz AMD Opteron 2435",
            "AMD EPYC 7551P 2.0 GHz",
            "AMD EPYC 7601 L 2.20 GHz, Dell SKU [338-BNCG]",
            "AMD Opteron 6262 HE",
            "ARM Cortex A53(1GHz) 24 Cores: SOCIONEXT SC2A11 ARM SoC",
            "Intel Core i5-4570",
            "Intel Core i7 610E",
            "Intel Pentium D Processor 930",
            "Intel Xeon Platinum 8176 v7 CPU 2.10 GHz (Intel Turbo Boost Technology up to 2.80 GHz)",
            "Intel Xeon Platinum 8180 2.50 GHz (Intel Turbo Boost Technology up to 3.8GHz)",
            "Intel Xeon Platinum 8280v2 @ 2.70GHz",
            "Intel Xeon Platinum 8380l v4 2.3GHz",
            "Intel Xeon X7560",
            "Intel(R) Xeon(R) Silver 4210 CPU @ 2.20GHz",
            "Six-Core AMD Opteron(r) Processor 8425 HE",
            "Xeon L5420",
            "Intel 6799L"
        ]
        expected_results = [
            # description, brand, model, moniker, version
            # ignores 2.6 GHz at beginning
            ["2.6 GHz AMD Opteron 2435", "opteron", "2435", "", ""],
            # ignores 2.0 GHz at end
            ["AMD EPYC 7551P 2.0 GHz", "epyc", "7551", "p", ""],
            # ignores Dell SKU ...
            ["AMD EPYC 7601 L 2.20 GHz, Dell SKU [338-BNCG]", "epyc", "7601", "l", ""],
            # parses out moniker: he
            ["AMD Opteron 6262 HE", "opteron", "6262", "he", ""],
            # ignores stuff after parens
            ["ARM Cortex A53(1GHz) 24 Cores: SOCIONEXT SC2A11 ARM SoC", "cortex", "a53", "", ""],
            # handles i*- stuff with a dash
            ["Intel Core i5-4570", "core", "i5-4570", "", ""],
            # handles i* stuff without a dash
            ["Intel Core i7 610E", "core", "i7 610", "e", ""],
            # ignores pentium (we don't care)
            ["Intel Pentium D Processor 930", "pentium", "930", "d", ""],
            # snags version, ignores "CPU"
            ["Intel Xeon Platinum 8176 v7 CPU 2.10 GHz (Intel Turbo Boost Technology up to 2.80 GHz)", "xeon", "8176", "", "v7"],
            # ignores stuff after parens, doesn't capture "2.50" as moniker or version
            ["Intel Xeon Platinum 8180 2.50 GHz (Intel Turbo Boost Technology up to 3.8GHz)", "xeon", "8180", "", ""],
            # ignores @ and snags just the version with no moniker
            ["Intel Xeon Platinum 8280v2 @ 2.70GHz", "xeon", "8280", "", "v2"],
            # snags both moniker and version
            ["Intel Xeon Platinum 8380l v4 2.3GHz", "xeon", "8380", "l", "v4"],
            # includes letters BEFORE model numbers as part of model
            ["Intel Xeon X7560", "xeon", "x7560", "", ""],
            # removes (R)
            ["Intel(R) Xeon(R) Silver 4210 CPU @ 2.20GHz", "xeon", "4210", "", ""],
            # known failure: looks for first model name ("core") -- don't care that this doesn't work
            ["Six-Core AMD Opteron(r) Processor 8425 HE", "core", "8425", "he", ""],
            # doesn't mind if company missing
            ["Xeon L5420", "xeon", "l5420", "", ""],
            # doesn't mind if brand missing
            ["Intel 6799L", "", "6799", "l", ""],
        ]
        processors = []
        for t in test_cases:
            processors.append(generate_processor(t))
        actual = []
        for p in processors:
            actual.append(self.extract_processor_pieces(p))
        self.assertEqual(expected_results, actual)


if __name__ == "__main__":
    unittest.main()
