import pandas as pd
import re


# known failure scenarios:
# Six-Core AMD Opteron(r) Processor 8425 HE ==> assumes "core" is the brand because it comes first# and "core" is a valid brand for other companies. oh well -- google doesn't use amd opteron's anyway

# company brand [style] model [moniker] [version]
# ex: intel xeon platinum 8180 l v3
# we ignore ghz
class Processor:
    def __init__(self,
                 original_description = "",
                 clean_description = "",
                 pieces = [],
                 company = "",
                 brand = "",
                 style = "",
                 model = "",
                 moniker = "",
                 version = ""):
        
        self.original_description = original_description
        self.clean_description = clean_description
        self.pieces = pieces
        self.company = company
        self.brand = brand
        self.style = style
        self.model = model
        self.moniker = moniker
        self.version = version


cases = [
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

# this is confusing stuff that we strip out
junk = [
    # there's one descripion that includes ", Dell SKU [338-BNCG]" at the end
    # remove all that (but we can't just strip after comma because there's a
    # comma in another description that has useful stuff afterwards :rolls_eyes:
    "dell",
    "sku",
    "\[[a-z0-9\-]+\]",
    ",",
    # i know we're talking about CPUs here, thanks
    "cpu",
    # often used before #.## GHz. we don't care.
    "@",
    # remove the remains of the registered trademark symbol (r) 
    "\(r\)",
    # ya i know we're talking about processors, thanks
    "processor",
    # we don't care about ghz -- gotta simplify somewhere!
    "ghz"
]
# i.e. find any of these terms ('|' means 'or')
junk_regex = r"|".join(junk)

# these are the only companies we see
companies = [
    "intel",
    "amd",
    "arm"
]
# i.e. find any of these terms ('|' means 'or')
company_regex = r"|".join(companies)

# these are the only brands we see
brands = [
    "opteron",
    "epyc",
    "core",
    "pentium",
    "xeon",
    "cortex"
]
# i.e. find any of these terms ('|' means 'or')
brand_regex = r"|".join(brands)

# these are the only makes we see
makes = [
    "gold",
    "silver",
    "platinum",
    "six-core",
    "quad-core"
]
# i.e. find any of these terms ('|' means 'or')
make_regex = r"|".join(makes)

# hooooo boy. models can look like: 'e3-2456m' or 'i7 8965' or 'x6890v3' or 'a53' or '7f24' or just '8965'
# REGEX DECRYPTED:
# look for a space (so we know we're dealing with a separate "word") \s
# then capture: (...)
#   maybe one number [0-9]?
#   maybe one letter [a-z]?
#   maybe one number [0-9]?
#   maybe a '-' or a ' ' [\-\s]?
#   DEFINITELY 2 to 4 digits [0-9]{2,4}
#   maybe one letter [a-z]?
#   maybe one number [0-9]?
raw_model_regex = r"\s([0-9]?[a-z]?[0-9]?[\-\s]?[0-9]{2,4}[a-z]?[0-9]?)"

# now take what we know about models and strip off the optional letters 
# (and any number after that) so we get JUST the model number (minus versions or monikers).
# e.g. if we have 'e4-2485m' give me just 'e4-2385', or from '8876v3' give me just '8876'
# REGEX DECRYPTED:
# look for a space (so we know we're dealing with a separate "word") \s
# then capture: (...)
#   maybe one number [0-9]?
#   maybe one letter [a-z]?
#   maybe one number [0-9]?
#   maybe a '-' or a ' ' [\-\s]?
#   DEFINITELY 2 to 4 digits [0-9]{2,4}
#   maybe one letter [a-z]?
#   maybe one number [0-9]?
#   THIS TIME STOP HERE so we don't get any letters or numbers tacked on the end
clean_model_regex = r"\s([0-9]?[a-z]?[0-9]?[\-\s]?[0-9]{2,4})"

# find us a version if it's sitting by itself, e.g. from 'xeon 2345 v4 2.2' give me 'v4'
# REGEX DECRYPTED:
# look for a space (so we know we're dealing with a separate "word") \s
# capture: (...)
#   the letter v
#   one number [0-9]{1}
standalone_version_regex = r"\s(v[0-9]{1})"

# find us a moniker off by its lonesome, e.g. from 'xeon 2345 he 2.0' give me just 'he'
# REGEX DECRYPTED:
# look for a space (so we know we're dealing with a separate "word") \s
# capture: (...)
#   1 or 2 letters [a-z]{1,2}
# followed by a space \s
# OR
# capture: (...)
#   1 or 2 letters [a-z]{1,2}
# at the end of the line $
standalone_moniker_regex = r"\s([a-z]{1,2})[\s]|([a-z]{1,2})$"

# snag the version if it's tagged onto the end of the model, e.g. from '4567v4' fetch 'v4'
# REGEX DECRYPTED:
# capture: (...)
#   the letter v
#   1 number [0-9]{1}
# at the end of the string we're processing (in this case we've fed this regex JUST the model string, not the whole description)
model_version_regex = r"(v[0-9]{1}$)"

# snag the moniker if it's tagged onto the end of the model, e.g. from '4567m' fetch 'm'
# REGEX DECRYPTED:
# capture: (...)
#   1 letter [a-z]{1}
# at the end of the string we're processing (in this case we've fed this regex JUST the model string, not the whole description)
model_moniker_regex = r"([a-z]{1}$)"


# remove all the distracting bits we don't need
def remove_junk(description):
    return re.sub(junk_regex, "", description)


# many descriptions have important stuff then "(blah turbo etc)" which is distracting
def split_off_parens(description):
    splitted = description.split("(")
    if splitted > 0:
        return splitted[0]
    else:
        return description


# remove what we can ignore and make lowercase to simplify searching
# "Intel Xeon Processor CPU 3446 l 2.0 @ GHz" --> "intel xeon 3446 l 2.0" 
def clean_description(description):
    return split_off_parens(remove_junk(description.lower())) 


# wrapper around regex to return empty string if nothing found
def safe_search(regex, check_string):
    found = re.search(regex, check_string)
    if found:
        return found.group(0)
    return ""


def generate_processor(description):
    processor = Processor(original_description = description) 
    processor.clean_description = clean_description(processor.original_description) 
    processor.company = safe_search(company_regex, processor.clean_description)
    processor.brand = safe_search(brand_regex, processor.clean_description)
    processor.make = safe_search(make_regex, processor.clean_description)
    raw_model = safe_search(raw_model_regex, processor.clean_description)
    processor.model = safe_search(clean_model_regex, raw_model)
    model_moniker = safe_search(model_moniker_regex, raw_model)
    model_version = safe_search(model_version_regex, raw_model)
    standalone_moniker = safe_search(standalone_moniker_regex, processor.clean_description)
    standalone_version = safe_search(standalone_version_regex, processor.clean_description)
    processor.version = model_version if model_version else standalone_version
    processor.moniker = model_moniker if model_moniker else standalone_moniker
    return processor

