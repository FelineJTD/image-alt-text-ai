// Browser add-on main.js

// Add-on working
console.log("Alt text add-on working");

// Backend URL
const BACKEND_URL = "http://localhost:5000";

const MAX_IMAGES = 30;

// Parse Document
const parseDocument = (doc) => {
  let websiteInfo = {};

  const parser = new DOMParser();
  const parsed = parser.parseFromString(doc, "text/html");

  const title = parsed.querySelector("title");
  websiteInfo["title"] = title ? title.textContent : "No title";

  const descriptionMeta = parsed.querySelector("meta[name='description']");
  const description = descriptionMeta
    ? descriptionMeta.content
    : "No description";
  websiteInfo["description"] = description;

  const images = Array.from(new Set(parsed.querySelectorAll("img"))); // Remove duplicates

  console.log(`Found ${images.length} images`);

  const imagesInfo = [];

  images.slice(0, MAX_IMAGES).forEach((image, i_image) => {
    try {
      // GET RELEVANT DATA OF THE IMAGE

      // The 'src' attribute of the image
      const imageUrl = image.getAttribute("src");

      // The 'alt' attribute of the image
      const imageAlt = image.getAttribute("alt") || "No alt attribute";

      // OTHER IMAGE ATTRIBUTES
      const imageAttrs = {};
      for (const attr of image.attributes) {
        imageAttrs[attr.name] = attr.value;
      }

      // Find out if the image has <a> or <button> parent, potentially indicating a functional image
      let currentTag = image;
      let aButtonParent = null;
      for (let i = 0; i < 3 && currentTag; i++) {
        aButtonParent = currentTag.closest("a, button");
        if (aButtonParent) break;
        currentTag = currentTag.parentElement;
      }

      // NEAREST TEXT FROM IMAGE FOR TEXT CONTEXT
      const nextText =
        image.nextSibling && image.nextSibling.textContent
          ? image.nextSibling.textContent.trim()
          : "No next text found";

      // Write the data (image and labels) to the images array
      imagesInfo.push({
        src: imageUrl,
        alt: imageAlt,
        attrs: imageAttrs,
        a_button_parent: aButtonParent
          ? aButtonParent.outerHTML
          : "No a/button parent",
        next_text: nextText,
      });
    } catch (error) {
      console.error(`Error processing image ${i_image}:`, error);
    }
  });

  websiteInfo["images"] = imagesInfo;

  console.log(websiteInfo);

  return websiteInfo;
};

// Get the url of the current page
const generateAltTexts = () => {
  console.log("Generating alt texts...");
  const url = window.location.href;
  console.log("url: ", url);

  // Get whole document
  const doc = document.documentElement.outerHTML;
  const parsedDoc = parseDocument(doc);

  // Get images
  const images = document.getElementsByTagName("img");
  console.log(images);

  // Send data to backend
  fetch(BACKEND_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url: url, data: parsedDoc }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        throw new Error(data.error);
      }
      console.log("Success:", data);

      // Insert alt text
      for (var i = 0; i < images.length; i++) {
        console.log(data[i]);
        if (data[i] != "undefined") images[i].alt = data[i];
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

browser.runtime.onMessage.addListener((message) => {
  if (message.action === "generateAltText") {
    generateAltTexts();
  }
});
