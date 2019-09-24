<img align="right" src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/project_icon_1024.png" width="128">

# google-analytics-cookie-parser
A WIP forensics tool for Windows written in Python, for parsing Google Analytics cookies.
## Always manually verify any results from this tool which you wish to use as evidence. 

### [Download latest version here](https://github.com/pbeart/google-analytics-cookie-parser/releases/latest)

## Instructions for GUI use:

<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example1.png" width="350">

#### Loading cookies
+ Select the browser and browser version you're using from the dropdown at the top
+ Find the cookies file using the instructions for your browser
+ Click 'Process'

#### Viewing and exporting
+ You can view information for a given domain by selecting that domain with the Domain dropdown after loading a cookie file
+ You can also export all Google Analytics cookies in a parsed format to .csv files in a chosen directory by clicking the 'Output to .csv' button

## Instructions for CLI use:

<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example_cli_1.png" width="350">

+ Every command requires both an input file path (`-i` or `--input`) and a browser name (`-b` or `--browser`) to be specified. Currently, `-b`/`--browser` can only be `firefox.3+` or `csv`

#### Viewing cookie info
+ The `info` command, which does not require any additional parameters, will show the number of GA cookies found and the number of unique domains for which any cookies were found

<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example_cli_info.png">

#### Listing domains
+ The `list-domains` command, which does not require any additional parameters, will list all domains for which GA cookies were found

<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example_cli_list_domains.png">

#### Viewing domain information
+ The `domain-info` command, which requires the additional parameter `-d` or `--domain`, will list a parsed version of all available information for the given domain. **The domain should be given in the format in which it is found with `list-domains`**

<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example_cli_domain_info.png">

#### Exporting all cookie information to .csv
+ The `export-csv` command, which requires the additional parameter `-o` or `--output` which should be a directory path of the output directory, will export all found cookie data to .csv files in the given directory. The `-f` or `--force-overwrite` option can be given to automatically overwrite files if they exist without prompting the user.


<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example_cli_export_csv.png">

## GACP currently supports:
* Reading and parsing cookies.sqlite from Firefox v3+ and any browser from which you can retrieve cookies as a .csv file
* Analysing and parsing all relevant Google Analytics cookies (\_ga, \_\_utma, \_\_utmb, \_\_utmz)
* Presenting all available information for a given domain
* Exporting GA cookie information to a .csv file

### GACP is currently only tested on Firefox v3+ and .csv, and as always any critical evidence should be double-checked by manually inspecting the relevant cookies

## Acknowledgements
I would like to thank Kevin Ripa, for being such an excellent instructor and mentor, and providing the inspiration to create this tool.
