The code in this repo scrapes walk highlands to find the best walks for a given set of users in a given set of regions to maximise munros bagged and emjoyment had.
The code quality is abysmal, please don't judge.

Walks are scored as (average munro rating (walk highlands))^2 * sqrt(average new munros per user)
If you wish to change this scoring system change 
``` 
avg_rating = total_rating / len(walk_data["munros"])
average_new_munros_per_user = total_new_munros / num_users
walk_score = math.pow(avg_rating, 2) * math.sqrt(average_new_munros_per_user)
```
in generate_walk_list()

Needs python3 and pip3

In command line run `pip3 install -r requirements.txt` to install libs

Add user names to query to `user_names.txt`, one per line 

Add regions to include to `regions_to_include.txt`
Regions are walk highlands regions, full list at bottom of this doc.

To run script
`python3 munros.py`
in the directory of the repository.

Some data is output to terminal. The useful info on munros / walks is written into `output.txt`

To update `munro_data.json` run `python3 scrape_munro_data.py`
This may take some time and there shouldn't really be much reason to do this.

The code has no error handling, no tests and may get you rate limited on walk highlands. Use at your own peril

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
