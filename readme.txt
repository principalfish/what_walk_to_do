Needs python3 and pip3
pip3 install requirements.txt

Add user names to query to user_names.txt, one per line 

Add regions to include to regions_to_include
Regions are walk highlands regions, full list at bottom of this doc.

To run script
python3 munros.py

Some data is output to terminal. The useful info on munros / walks is dumped into output.txt

To update munro_data.json run python3 scrape_munro_data.py 
This may take some time and there shouldn't really be much reason to do this.

The code has no error handling, no test and may get you rate limited on walk highlands. Use at your own peril

Full list of possible regions 
Angus
Argyll
Cairngorms
Fort William
Isle of Mull
Isle of Skye
Kintail
Loch Lomond
Loch Ness
Perthshire
Sutherland
Torridon
Ullapool