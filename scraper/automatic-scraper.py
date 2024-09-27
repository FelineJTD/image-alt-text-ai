input_file = './website_url_data/builtwith-top1m-20240621-random.csv'
output_file = './output/output.json'
progress_file = './progress_aut.txt'
error_log_file = './error_aut.log'
text_elements = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
is_chrome_headless = True
number_of_websites = 100
website_per_batch = 10


# LOADING WEBSITES

# Open the CSV file and read the URLs
import pandas as pd
df = pd.read_csv(input_file)
websites = df['url'].tolist()[0:number_of_websites]

# Append http:// to each URL
websites = ['http://' + url for url in websites]

# Print the first 5 URLs
print("Website URLs loaded:")
for i in range(min(5, len(websites))):
    print(websites[i], end=', ')
print('...\n')


# SCRAPING IMAGES

import requests
from bs4 import BeautifulSoup
import json
from IPython.display import clear_output
from selenium import webdriver
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Initialize the index of the website
i_website = 1
# Load the progress
try:
    with open(progress_file, "r") as f:
        i_website = int(f.readline())
except FileNotFoundError:
    pass

for i in range(i_website, min(i_website + website_per_batch, len(websites))):
    website_info = {}
    try:
        # Set up Chrome options to run in headless mode
        chrome_options = Options()
        if is_chrome_headless:
            chrome_options.add_argument("--headless")

        # Initialize the WebDriver with the headless options
        driver = webdriver.Chrome(service=Service(), options=chrome_options)

        # Load the website
        driver.get(websites[i])

        # Get the page source after interactions
        page = driver.page_source

        # Initialize the list to store the image data
        images_info = []

        # Parse the HTML content
        soup = BeautifulSoup(page, "html.parser") # Extract data using Beautiful Soup methods

        # Get all text in the page
        text = soup.get_text()
        website_info['text'] = text

        # Find all 'img' tags
        images = soup.find_all("img")
        # Remove duplicates
        images = set(images)


        i_image = 1
        for image in images:
            try:
                # GET RELEVANT DATA OF THE IMAGE
                # Clear the output before displaying the next image to avoid an overly big notebook size
                clear_output(wait=True)
                
                print(f"Image {i_image} of {len(images)}, website {i_website} of {len(websites)}")

                # The 'src' attribute of the image
                image_url = image["src"]
                # Relative path handling
                if not image_url.startswith(('http://', 'https://')):
                    image_url = urljoin(websites[i], image_url)

                # The 'alt' attribute of the image
                image_alt = image.get("alt", "No alt attribute")  # Use a default value if 'alt' is missing

                # OTHER IMAGE ATTRIBUTES
                image_attrs = image.attrs

                # Find out if image has <a> parent or <button> parent, potentially indicating a functional image
                a_button_parent_found = False
                # Loop up to 3 levels up the hierarchy
                current_tag = image
                a_button_parent = None
                for _ in range(3):
                    # Try to find a parent <a> tag or <button> tag
                    a_button_parent = current_tag.find_parent(["a", "button"])
                    if a_button_parent:
                        # If an <a> or <button> parent is found, set the flag to True and break the loop
                        a_button_parent_found = True
                        break
                    else:
                        # If not found, move up to the next parent
                        current_tag = current_tag.parent
                        # If the current tag is None (top of the tree), break the loop
                        if current_tag is None:
                            break

                # NEAREST TEXT FROM IMAGE FOR TEXT CONTEXT
                previous_texts = []
                curr_element = image
                previous_texts_cutoff_by_image_index = -1

                # Gather 5 previous texts
                prev_i = 0
                while len(previous_texts) < 5:
                    to_search = text_elements + ['img']
                    previous_text = curr_element.find_previous(to_search)
                    if previous_text:
                        if previous_text.name == "img" and previous_texts_cutoff_by_image_index == -1:
                            previous_texts_cutoff_by_image_index = prev_i
                        elif previous_text.text:
                            previous_texts.append(f'{previous_text.name}: {previous_text.text}')
                        curr_element = previous_text
                    else:
                        break
                    prev_i += 1

                next_texts = []
                curr_element = image
                next_texts_cutoff_by_image_index = -1

                # Gather 5 next texts
                next_i = 0
                while len(next_texts) < 5:
                    to_search = text_elements + ['img']
                    next_text = curr_element.find_next(to_search)
                    if next_text:
                        if next_text.name == "img" and next_texts_cutoff_by_image_index == -1:
                            next_texts_cutoff_by_image_index = next_i
                        elif next_text.text:
                            next_texts.append(f'{next_text.name}: {next_text.text}')
                        curr_element = next_text
                    else:
                        break
                    next_i += 1

                # Write the data (image and labels) to a file
                images_info.append({
                    "src": image_url,
                    "alt": image_alt,
                    "attrs": image_attrs,
                    "a_button_parent": str(a_button_parent),
                    "previous_texts": previous_texts,
                    "previous_texts_cutoff_by_image_index": previous_texts_cutoff_by_image_index,
                    "next_texts": next_texts,
                    "next_texts_cutoff_by_image_index": next_texts_cutoff_by_image_index
                })
                
            except KeyError:
                # Put to log file
                with open(error_log_file, "a") as f:
                    f.write(f"Error at image {i_image} of website {i_website}: Key error")
                    if image_url:
                        f.write(f"Image URL: {image_url}\n")
            except requests.exceptions.MissingSchema:
                # Put to log file
                with open(error_log_file, "a") as f:
                    f.write(f"Error at image {i_image} of website {i_website}: Missing schema\n")
                    if image_url:
                        f.write(f"Image URL: {image_url}\n")
            except Exception as e:
                print(f"An error occurred: {e}")
                # Put to log file
                with open(error_log_file, "a") as f:
                    f.write(f"Error at image {i_image} of website {i_website}: {e}\n")
                    if image_url:
                        f.write(f"Image URL: {image_url}\n")

            i_image += 1

        # Step 4: Write the list to a file in JSON format
        with open(output_file, "a") as f:
            json.dump(images_info, f, indent=4)

        i_website += 1

        # Write the progress to a file
        with open(progress_file, "w") as f:
            f.write(f"{i_website}")

    except Exception as e:
        print(f"An error occurred: {e}")
        i_website += 1
        # Put to log file
        with open(error_log_file, "a") as f:
            f.write(f"Error at website {i_website}: {e}\n")