// Browser add-on main.js

// Add-on working
console.log("Alt text add-on working");

// Backend URL
const backendURL = "http://localhost:5000";

// Get the url of the current page
const url = window.location.href;
console.log(url);

// Get whole document
const doc = document.documentElement.outerHTML;
console.log(doc);

// Get images
const images = document.getElementsByTagName("img");
console.log(images);

// Send data to backend
fetch(backendURL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ url: url, doc: doc }),
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Success:", data);

    // Get new images
    //   const images = document.getElementsByTagName("img");
    //   console.log(images);

    // Insert alt text
    for (var i = 0; i < images.length; i++) {
      console.log(images[i].alt);
      console.log(data[i]);
      images[i].alt = data[i];
      console.log(images[i].alt);
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });
