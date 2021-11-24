# SriLankan Kings Search
This repository contains the source code for the Sri Lankan Kings search engine which is implemented using Elasticsearch and Python. 

## File Structure
```
├── csv_to_json.py : python sctrip for convert scraped CSV file into JSON file
├── elasticseaech_commands.txt : contains the commands used for the indexing and loading the data
├── search.py : contains function to map user phrases and elasticsearch queries
├── load_csv.conf : logstach file which is used to load the data into elastic search index
├── sl-kings.csv : file which contains the scraped data
├── sl-kings.json : converted JSON file from sl-kings.csv file
```
## Getting Started
### Installation and Starting of Elasticsearch Cluster Server
Use official [Elasticsearch](https://www.elastic.co/elastic-stack/) website for the installation.
### Indexing
Clone the repository into your local machine and open the terminal from `SriLankanKingsSearch` directory.
Use following curl command for create an index name `kings`
```
curl -XPUT "http://localhost:9200/kings"
```
Use following command to load `sl-kings.csv` into elasticsearch index `kings`
```
/usr/share/logstash/bin/logstash -f sl-kings.conf
```
### Searching
Simply run the `search.py` python script to start the search engine.
```
python3 search.py
```
## Data Fields
Dataset was scraped manually from Wikipedia page, which contained with details of history of Sri Lankan Kings. Each data record consist with following data fields.
1. name (ex: මහා දුට්ඨගාමිණී අභය)
2. clan (ex: විජය රාජවංශය)
3. kingdom (ex: අනුරාධපුර රාජධානිය)
4. reign_start (ex: 161 BC)
5. reign_end (ex: 137 BC)
6. predecessor_relation (ex: කාවන්ිස්ස රජුයේ වැඩිමහල් පුත්රයායි. මුලින් රුහුයේ පාලකයා විය)
7. reign_details (ex: යමතුමා රජරට පාලකයාව සිටි ආක්රමණික එළාර රජ පරදා ය ෝළ අධිරාජ්යයයන් ලාංකීය ජනතාව රැක ගත්හ.)

## Supported Queries
Search system supports for the following queries,
- Search by a specific field (ex: [‘name’ :  'තිස්ස'])
- Range search by reign years (ex: 100 BC to 100 AD)
- Search by full text ( ex: ‘තිස්ස ලම්බකර්ණ අනුරාධපුර රාජධානිය වැඩිමහල්ම’)
- Multi field search (ex: [‘name’ : 'තිස්ස',  ‘clan’ : 'ලම්බකර්ණ',  ‘kingdom’ : 'අනුරාධපුර', ‘predecessor_relation’ : 'රජුගේ වැඩිමහල්ම සොහොයුරායි'])

## Advanced Features
Intent classification
- Extract the intention of the search text and show relevant results
(‘අඩුම කාලයක් පාලනය කල රජවරු 50’ will return the list of 50 kings who have the shortest reign period.)

Faceted search
- Search by a specific field
- Search by multiple fields

Ordering methods
- Reigning time
`Oldest first, Newest first, Longest first, Shortest first`

