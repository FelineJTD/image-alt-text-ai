input_file = './website_url_data/builtwith-top1m-20240621-random.csv'
output_file = './output/output.json'
progress_file = './progress_aut.txt'
number_of_websites = 2


# LOADING WEBSITES

# Open ./website_url_data/builtwith-top1m-20240621.csv and read all the URLs
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
import os
from selenium import webdriver
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Initialize the index of the website
i_website = 0

for i in range(i_website, len(websites)):
    website_info = {}
    try:
        # Set up Chrome options to run in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")  # Optional: Disable GPU acceleration
        # chrome_options.add_argument("--no-sandbox")   # Optional: Required for some environments
        # chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: Overcome limited resource problems

        # Initialize the WebDriver with the headless options
        driver = webdriver.Chrome(service=Service(), options=chrome_options)

        # Load the website
        driver.get(websites[i])

        # Get the page source after interactions
        page = driver.page_source
        # Open the URL in a new tab for reference while labelling
        # driver = webdriver.Chrome()
        # driver.get(websites[i])# Get the page source after interactions
        # page = driver.page_source
        # Skip website?
        # skip = input("Skip website? (input anything to skip): ")
        # if skip == 'q':
        #     # Save the progress
        #     with open("progress.txt", "w") as f:
        #         f.write(str(i_website))
        #     driver.quit()
        #     break
        # if skip:
        #     i_website += 1
        #     continue

        # Initialize the list to store the image data
        images_info = []
        # Get the HTML content of the page
        # page = requests.get(websites[i])

        # Parse the HTML content
        soup = BeautifulSoup(page, "html.parser")# Extract data using Beautiful Soup methods

        # Get all text in the page
        text = soup.get_text()
        website_info['text'] = text

        # Create a folder in ./images/ with the name of the website
        # os.makedirs(f"./images/{websites[i].split('//')[1].replace('/', '-')}", exist_ok=True)

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
                print("Image URL: ", image_url)
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
                print("Parent <a> or <button> found: ", a_button_parent_found)
                print("Parent tag: ", a_button_parent)

                # NEAREST TEXT FROM IMAGE FOR TEXT CONTEXT
                previous_texts = []
                curr_element = image
                # Gather 5 previous texts
                for _ in range(5):
                    previous_text = curr_element.find_previous(["a", "p", "h1", "h2", "h3", "h4", "h5", "h6"])
                    if previous_text:
                        previous_texts.append(str(previous_text))
                        curr_element = previous_text
                    else:
                        break
                print("Previous texts: ", previous_texts)

                next_texts = []
                curr_element = image
                # Gather 5 next texts
                for _ in range(5):
                    next_text = curr_element.find_next(["p", "h1", "h2", "h3", "h4", "h5", "h6"])
                    if next_text:
                        next_texts.append(str(next_text))
                        curr_element = next_text
                    else:
                        break

                # The image file name
                # file_name = f"{websites[i].split('//')[1].replace('/', '-')}-image_{i_image}.jpg"

                # LABELLING (ROLE AND ALT TEXT)
                # Label the image manually
                # data = label_image(image_url, image_alt, file_name)
                # if data == 'q':
                #     # Save the progress
                #     with open("progress.txt", "w") as f:
                #         f.write(str(i_website))
                #         f.write("\n")
                #         f.write(str(i_image))
                #     break
                # if data is None:
                #     continue

                # Write the data (image and labels) to a file
                images_info.append({
                    "src": image_url,
                    "alt": image_alt,
                    "attrs": image_attrs,
                    "a_button_parent": str(a_button_parent),
                    "previous_texts": previous_texts,
                    "next_texts": next_texts,
                })
                print("Data saved")
                
            except KeyError:
                # Put to log file
                with open("error.log", "a") as f:
                    f.write(f"Error at image {i_image} of website {i_website}: Key error")
                    if image_url:
                        f.write(f"Image URL: {image_url}\n")
            except requests.exceptions.MissingSchema:
                # Put to log file
                with open("error.log", "a") as f:
                    f.write(f"Error at image {i_image} of website {i_website}: Missing schema\n")
                    if image_url:
                        f.write(f"Image URL: {image_url}\n")
            except Exception as e:
                print(f"An error occurred: {e}")
                # Put to log file
                with open("error.log", "a") as f:
                    f.write(f"Error at image {i_image} of website {i_website}: {e}\n")
                    if image_url:
                        f.write(f"Image URL: {image_url}\n")

            i_image += 1

        website_info['images'] = images_info
        # Step 4: Write the list to a file in JSON format
        with open(output_file, "a") as f:
            json.dump(images_info, f, indent=4)

        i_website += 1

    except Exception as e:
        print(f"An error occurred: {e}")
        i_website += 1
        # Put to log file
        with open("error.log", "a") as f:
            f.write(f"Error at website {i_website}: {e}\n")