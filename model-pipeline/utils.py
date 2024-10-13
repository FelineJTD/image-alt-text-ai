from bs4 import BeautifulSoup

text_elements = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

def parse_image(image):
    pass

# Parse a string of html with beautifulsoup and return all needed information
def parse_document(doc: str):
    website_info = {}
    try:
        # Parse the HTML content
        soup = BeautifulSoup(doc, "html.parser")

        # Get all text in the page
        text = soup.get_text()
        website_info['text'] = text

        # Get the document's title
        title = soup.title.string if soup.title else "No title"
        website_info['title'] = title

        # Get the document's description
        description = soup.find("meta", {"name": "description"})
        if description:
            description = description["content"]
        website_info['description'] = description

        # Find all 'img' tags
        images = soup.find_all("img")
        # Remove duplicates
        images = set(images)

        print(f"Found {len(images)} images")

        images_info = []
        i_image = 1
        for image in images:
            try:
                # GET RELEVANT DATA OF THE IMAGE

                # The 'src' attribute of the image
                image_url = image["src"]

                # The 'alt' attribute of the image
                image_alt = image.get("alt", "No alt attribute")  # Use a default value if 'alt' is missing

                # OTHER IMAGE ATTRIBUTES
                image_attrs = image.attrs

                # Find out if image has <a> parent or <button> parent, potentially indicating a functional image
                # Loop up to 3 levels up the hierarchy
                current_tag = image
                a_button_parent = None
                for _ in range(3):
                    # Try to find a parent <a> tag or <button> tag
                    a_button_parent = current_tag.find_parent(["a", "button"])
                    if a_button_parent:
                        # If an <a> or <button> parent is found, break the loop
                        break
                    else:
                        # If not found, move up to the next parent
                        current_tag = current_tag.parent
                        # If the current tag is None (top of the tree), break the loop
                        if current_tag is None:
                            break

                # NEAREST TEXT FROM IMAGE FOR TEXT CONTEXT
                next_text = image.find_next(text_elements)

                if not next_text:
                    next_text = "No next text found"
                elif next_text.text:
                    next_text = f'{next_text.name}: {next_text.text}'

                # Write the data (image and labels) to a file
                images_info.append({
                    "src": image_url,
                    "alt": image_alt,
                    "attrs": image_attrs,
                    "a_button_parent": str(a_button_parent),
                    "next_text": next_text,
                })
                
            except Exception as e:
                print(f"An error occurred: {e}")

            i_image += 1

        website_info['images'] = images_info
        return website_info

    except Exception as e:
        print(f"An error occurred: {e}")