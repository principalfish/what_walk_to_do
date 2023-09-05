import json
import re

from bs4 import BeautifulSoup
import requests


def walkhighlands_blog_url(user):
	return f"https://www.walkhighlands.co.uk/blogs/{user}"

def walkhighlands_munros_url(id):
	return f"https://www.walkhighlands.co.uk/Forum/memberlist.php?u={id}&mode=viewmap"

def get_munro_map_from_blog(blog_url):
	response = requests.get(blog_url)

	soup = BeautifulSoup(response.text, 'lxml')
	response.close()

	# Find the <strong> element with the text "Munros:"
	strong_element = soup.find('strong', string='Munros: ')

	# Find the next sibling element, which is the <a> tag in this case
	link_element = strong_element.find_next_sibling('a')

	link = link_element.get("href")
	match = re.search(r'u=(\d+)', link)
	user_id = match.group(1)
	return walkhighlands_munros_url(user_id)

def generate_outstanding_munros(munros_url, munros_to_include):

	response = requests.get(munros_url)

	# Create a Beautiful Soup object
	soup = BeautifulSoup(response.text, "html.parser")
	response.close()

	# Find all <span> elements with style="color:red;"
	red_spans = soup.find_all('span', style='color:red;')

	# Extract and print the text content of each matching <span> element
	munro_names = []
	for span in red_spans:
		munro_name = span.get_text()	 
		
		if munro_name in munros_to_include:
			munro_names.append(munro_name)
	
	return munro_names

def get_users_outstanding_munros(user, munros_to_include):
	print (f"Fetching outstanding munros for {user}")
	user_blog_url = walkhighlands_blog_url(user)
	user_munro_map_url = get_munro_map_from_blog(user_blog_url)
	print (f"User munro map link: {user_munro_map_url}")
	return generate_outstanding_munros(user_munro_map_url, munros_to_include)
	
def generate_outstanding_munro_frequency_map(munros_outstanding_map):
	
	outstanding_munro_frequencies = {}

	for user in munros_outstanding_map:
		user_munro_list = munros_outstanding_map[user]
		for outstanding_munro in user_munro_list:

			if outstanding_munro not in outstanding_munro_frequencies:
				outstanding_munro_frequencies[outstanding_munro] = [user]
			else:
				outstanding_munro_frequencies[outstanding_munro].append(user)

	frequency_mapping = {}
	for munro in outstanding_munro_frequencies:
		munro_freqency = len(outstanding_munro_frequencies[munro])
		munro_data = {
			"name" : munro,
			"users" : outstanding_munro_frequencies[munro]
		}
  
		if munro_freqency not in frequency_mapping:
			frequency_mapping[munro_freqency] = [munro_data]
		else:
			frequency_mapping[munro_freqency].append(munro_data)
	
	return frequency_mapping

def get_munros_to_include(munros, regions_to_include):
    munros_copy = munros.copy()
    for munro in munros_copy.keys():
    	if munros_copy[munro]["region"] not in regions_to_include:
           del munros[munro]
    
    return munros
        
    
def generate_walk_list(user_names, regions_to_include):
	
	with open("munro_data.json", "r", encoding="utf-8") as json_in:
		current_munro_data = json.load(json_in)
		munros_data = current_munro_data["munros"]
		walks_data = current_munro_data["walks"]
	
  
	munros_to_include = get_munros_to_include(munros_data, regions_to_include)
		
	munros_outstanding_map = {}
	users_info_string = ""
	for user in user_names:
		munros_outstanding = get_users_outstanding_munros(user, munros_to_include)
		munros_outstanding_map[user] = munros_outstanding
		user_string = f"User {user} has {len(munros_outstanding)} munros remaining in given regions"
		users_info_string += user_string + "\n"
		print (user_string)
	
	munro_frequency_map = generate_outstanding_munro_frequency_map(munros_outstanding_map)
	num_users = len(user_names)

	frequencies_to_check = []
	munro_freq_mapping = {key:0 for key in munros_data}
 	
	print ("Generating outstanding munro list")
	munro_output_string = ""
	for i in range(num_users, -1, -1):
		if i in munro_frequency_map:
			frequencies_to_check.append(i)
			munros_all_users = []
			munro_output_string += f"Munros that {i} users have not done:\n"
			for j in range(len(munro_frequency_map[i])):				
				munro_output_string += f"{munro_frequency_map[i][j]['name']} : {','.join(munro_frequency_map[i][j]['users'])}\n"
				munro_freq_mapping[munro_frequency_map[i][j]['name']] = len(munro_frequency_map[i][j]['users'])
				if i == num_users:
					munros_all_users.append(munro_frequency_map[i][j]['name'])
			munro_output_string += "\n"
		
				
			if i == num_users:
				print (f"All users have not the following munros: {','.join(munros_all_users)}")
		
	print ("Generating best walk list")
	
	walks_to_do_info = []
	walks_parsed = {}
	for f in frequencies_to_check:	
     
		munros_to_check = munro_frequency_map[f]
		
		for munro_info in munros_to_check:
			
			munro_name = munro_info["name"]
			current_munro_data = munros_data[munro_name]
			walks_to_munro = current_munro_data["walks"]

			for walk_to_munro in walks_to_munro:
				walk_name = walk_to_munro["walk"]	

				if walk_name in walks_parsed:
					continue
				
				walks_parsed[walk_name] = True
				walk_data = walks_data[walk_name]				
				total_rating = 0
				total_num_users_not_done = 0
				for munro_in_walk in walk_data["munros"]:
					total_rating += float(munros_data[munro_in_walk]["rating"])
					total_num_users_not_done += munro_freq_mapping[munro_in_walk]

				avg_rating = total_rating / len(walk_data["munros"])
				avg_num_users_not_done = total_num_users_not_done / (num_users)
				walk_score = avg_rating * avg_num_users_not_done
				munros_in_walk = ", ".join(walk_data["munros"])
				walk_link = f"https://www.walkhighlands.co.uk/{walk_data['link']}"
    
				walk_info = {
					"name" : walk_name, 
					"link" : walk_link,
					"munros_in_walk" : munros_in_walk,
					"avg_munro_rating": round(avg_rating, 2),
					"avg_num_users_not_done" : round(avg_num_users_not_done, 2),
					"score" : round(walk_score, 2)
				}

				walks_to_do_info.append(walk_info)
    
	walk_string = "Suggested walks in order of best match for given users: \n\n"
	walks_sorted = sorted(walks_to_do_info, key=lambda x: x['score'], reverse=True) 
	for walk in walks_sorted:
		walk_string += f"Walk: {walk['name']} " + "\n"
		walk_string += f"Link: {walk['link']} " + "\n"
		walk_string += f"Munros Included: {walk['munros_in_walk']} " + "\n"
		walk_string += f"Average Munro Rating: {walk['avg_munro_rating']}" + "\n"
		walk_string += f"Average number of new munros per user: {walk['avg_num_users_not_done']} " + "\n"
		walk_string += f"Walk score (rating * new munros): {walk['score']} " + "\n"
		walk_string += "\n"
	
		
	output_string = "For users:" + ",".join(user_names) + "\n" + "In regions:" + ",".join(regions_to_include) +  "\n\n" + users_info_string + "\n\n" + munro_output_string + "\n\n" + walk_string
	
	return output_string

if __name__ == "__main__":
	with open("user_names.txt") as f:
		user_names = f.read().split("\n")
  
	with open("regions_to_include.txt") as f:
		regions_to_include = f.read().split("\n")	

	print (f"Generating munro walks for walkhighlands users: {', '.join(user_names)}")
	print (f"Only checking munros/walks in the following regions: {','.join(regions_to_include)}")
	output_string = generate_walk_list(user_names, regions_to_include)
	with open("output.txt", "w", encoding="utf-8") as out_file:
		out_file.write(output_string)

	print ("Outstanding munro list and best matched walk info written to output.txt")
