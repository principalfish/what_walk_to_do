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
	for user in user_names:
		munros_outstanding = get_users_outstanding_munros(user, munros_to_include)
		munros_outstanding_map[user] = munros_outstanding
		print (f"User {user} has {len(munros_outstanding)} munros remaining")
	
	munro_frequency_map = generate_outstanding_munro_frequency_map(munros_outstanding_map)
	num_users = len(user_names)

	frequencies_to_check = []
	munro_freq_mapping = {}
 	
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
	walk_string = ""
	for f in frequencies_to_check:	
     
		munros_to_check = munro_frequency_map[f]
		
		for munro_info in munros_to_check:
			
			munro_name = munro_info["name"]
			current_munro_data = munros_data[munro_name]
			walks_to_munro = current_munro_data["walks"]

			for walk_to_munro in walks_to_munro:
				walk_name = walk_to_munro["walk"]
				print (walk_name)
				walk_data = walks_data[walk_name]
				print (walk_data)
				total_rating = 0
				total_num_users_not_done = 0
				for munro_in_walk in walk_data["munros"]:
					total_rating += current_munro_data[munro_in_walk]["rating"]
					total_num_users_not_done += munro_freq_mapping[munro_in_walk]

				avg_rating = total_rating / len(walk_data["munros"])
				avg_num_users_not_done = total_num_users_not_done / len(walk_data["munros"])
				score = avg_rating * avg_num_users_not_done
				print (avg_rating, avg_num_users_not_done, score)
				
    
	output_string = munro_output_string + "\n" + walk_string
	
	return output_string

if __name__ == "__main__":
	with open("user_names.txt") as f:
		user_names = f.read().split("\n")
  
	with open("regions_to_include.txt") as f:
		regions_to_include = f.read().split("\n")
	

	print (f"Generating munro walks for walkhighlands users: {', '.join(user_names)}")
	print (f"Generating walks in the following regions: {','.join(regions_to_include)}")
	
	with open("output.txt", "w", encoding="utf-8") as out_file:
		out_file.write(generate_walk_list(user_names, regions_to_include))

	print ("Outstanding munro list and best matched walk info written to output.txt")
