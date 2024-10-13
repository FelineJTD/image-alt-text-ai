// Browser add-on main.js

// Add-on working
console.log("Alt text add-on working");

// Backend URL
const backendURL = "http://localhost:5000";

// Listen if there is a change in the DOM
// document.addEventListener("DOMSubtreeModified", function () {
// Get the url of the current page
const url = window.location.href;
console.log(url);

// Get whole document
const doc = document.documentElement.outerHTML;
console.log(doc);

// Get new images
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
  })
  .catch((error) => {
    console.error("Error:", error);
  });

// Loop through all images
// for (var i = 0; i < images.length; i++) {
//   console.log(images[i].alt);
//   // If alt text is empty, set it to "Image"
//   if (images[i].alt === "") {
//     images[i].alt = "Image";
//   }
// }
// });
