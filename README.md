<img align="right" src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/project_icon_1024.png" width="128">

# google-analytics-cookie-parser
A WIP forensics tool for Windows written in Python, for parsing Google Analytics cookies.
## Always manually verify any results from this tool which you wish to use as evidence. 

### [Download latest version here](https://github.com/pbeart/google-analytics-cookie-parser/releases/latest)


<img src="https://raw.githubusercontent.com/pbeart/google-analytics-cookie-parser/master/docs/example_images/example1.png" width="400">


## Instructions for use:
#### Loading cookies
+ Select the browser and browser version you're using from the dropdown at the top
+ Find the cookies file using the instructions for your browser
+ Click 'Process'

#### Viewing and exporting
+ You can view information for a given domain by selecting that domain with the Domain dropdown after loading a cookie file
+ You can also export all Google Analytics cookies in a parsed format to .csv files in a chosen directory by clicking the 'Output to .csv' button


## GACP currently supports:
* Reading and parsing cookies.sqlite from Firefox v3+ and any browser from which you can retrieve cookies as a .csv file
* Analysing and parsing all relevant Google Analytics cookies (\_ga, \_\_utma, \_\_utmb, \_\_utmz)
* Presenting all available information for a given domain
* Exporting GA cookie information to a .csv file

### GACP is currently only tested on Firefox v3+ with \_ga cookies, and as always any critical evidence should be double-checked by manually inspecting the relevant cookies

## Acknowledgements
I would like to thank Kevin Ripa, for being such an excellent instructor and mentor, and providing the inspiration to create this tool.
