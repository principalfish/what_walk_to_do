from bs4 import BeautifulSoup
import requests

import json

def get_munro_data(link, name, region, height):
    print (f"Fetching data for {name}")
    munro_data = {
        'link': f"https://www.walkhighlands.co.uk/munros/{link}",
        'name': name,
        'region': region,
        'height': height
    }

    munro_page_content = requests.get(munro_data["link"])
    soup = BeautifulSoup(munro_page_content.text, "lxml")
    munro_page_content.close()

    # Find the <h2> element with the text 'Detailed route description and map'
    h2_element = soup.find('h2', string='Detailed route description and map')

    # Find the <h3> element with the text 'Other routes and challenges'
    h3_element = soup.find('h3', string='Other routes and challenges')



    walks = []
    
    current_element = h2_element.find_next_sibling()
    while current_element and current_element != h3_element:
   
        if current_element.name == 'p':
            a_element = current_element.find('a')           
            walk_name = a_element.get_text()     
            
            walk_href = a_element.get('href')
         
            walks.append({"walk" : walk_name, "link": walk_href})
        current_element = current_element.find_next_sibling()
 
        
   
    munro_data["walks"] = walks

    rating_element = soup.find('li', class_='current-rating')
    rating_text = rating_element.get_text(strip=True)
    
    # Parse the rating value from the text (assuming it's in the format "Currently X.XX/5")
    rating_start = rating_text.find("Currently ") + len("Currently ")
    rating_end = rating_text.find("/5")
    rating_value = rating_text[rating_start:rating_end]
    munro_data["rating"] = rating_value
    return munro_data


def fetch_munros():

    munros_url = "https://www.walkhighlands.co.uk/munros/munros-a-z"

    response = requests.get(munros_url)
    soup = BeautifulSoup(response.text, 'lxml')
    response.close()

    munro_data = {}
    walk_data = {}

    # Find all tables with class "table1"
    tables = soup.find_all('table', class_='table1')


    # Loop through the tables
    for table in tables:
        # Find all <tr> elements inside the <tbody>
        tbody = table.find('tbody')
        if tbody:
            tr_elements = tbody.find_all('tr')
            
            # Loop through the <tr> elements
            for tr in tr_elements:
                td_elements = tr.find_all('td')
                
                # Extract information from the <td> elements
                if len(td_elements) >= 3:
                    link = td_elements[0].find('a')               
                    link_href = link.get('href')
                    munro_name = link.get_text()              
                    region = td_elements[1].get_text()
                    height = td_elements[2].get_text()                    

                   # if munro_name == "A' Chailleach (Fannichs)":
                    scraped_munro_data  = get_munro_data(link_href, munro_name, region, height)
                
                    munro_data[munro_name] = scraped_munro_data
                
                    for walk in scraped_munro_data["walks"]:
                    
                        walk_name = walk["walk"]
                        if walk_name not in walk_data:
                            to_add = {
                                "name" : walk_name,
                                "link" : walk["link"],
                                "munros" : [munro_name],
                                "region" : region
                            }
                            walk_data[walk_name] = to_add
                        else:
                            walk_data[walk_name]["munros"].append(munro_name)
                    

    munro_data_out = {
        "munros" : munro_data,
        "walks" : walk_data
    }
                
    # Now, the `extracted_data` list contains dictionaries with the extracted information
    # You can further process or display this data as needed
    with open("munro_data.json", "w", encoding="utf-8") as json_out:
        json.dump(munro_data_out, json_out, ensure_ascii=False)

if __name__=="__main__":
    fetch_munros()