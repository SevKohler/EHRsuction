
# EHRsuction
Downloads all Compositions from an openEHR platform and exports it into
EHR_UID/composition-name.json structure.
Also supports FLAT using the view provided in resources for Better, needs to uploaded there first.
Contact your Better support to know how. 

Ehrbase only CANONICAL export is supported so far. 

## Requirements:
* Running openEHR server
* python3

## Use
1. Download dependencies
   `pip install -r requirements.txt`
2. Modify config.yaml to your liking
3. Run EHRsuction
   `python3 ehrsuction.py`

