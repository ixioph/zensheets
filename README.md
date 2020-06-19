# Zensheets
A module for exporting Zendesk search queries to spreadsheets. The long-term goal for the project is to easily pull and format Zendesk tickets, based on a search query, and transform the data into interactive spreadsheets, custom dashboards, etc.

## Requirements
pygsheets v
pandas v

## Usage
You need to store two config files in root, 'config.ini' and 'presets.ini'. 'config.ini' contains your Zendesk domain, base64 encrypted API key, and GSheets service file. 'presets.ini' contains your labeled preset queries, for easy repeating. These files are formatted as follows:

config.ini
<pre><code>#config.ini
[zendesk]
Domain = "yourzendeskdomain"
Credentials = "youremailandzendeskapib64encrypted"

[gsheets]
ServiceFile = "./path/to/gsheetsservicefile.json"</code></pre>

presets.ini
<pre><code>#presets.ini
[DEFAULT]
SortBy = "created_at"
SortOrder = "desc"
OutPage = 0
Period = "W"

[billing_paypal]
SheetName = "Gsheets Test v1.33.7"
Tags = "paypal"
Form = "Billing"</code></pre>

From there, you simply <pre><code>python run.py name_of_preset</code><pre> and the target SheetName will be updated based on your preferences.

### Limitations
Functionality is continually being added to this module to support more use-cases. Currently, the following features are of the highest priority for implementation:
  * Dynamic Field Input
  * Preset and Dynamic Field Output
