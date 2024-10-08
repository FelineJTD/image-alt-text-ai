// Browser add-on main.js

// Add-on working
console.log("Alt text add-on working");

// Get all images
var images = document.getElementsByTagName("img");

// Loop through all images
for (var i = 0; i < images.length; i++) {
  console.log(images[i].alt);
  // If alt text is empty, set it to "Image"
  if (images[i].alt === "This contains an image of: ") {
    images[i].alt = "Image";
  }
  // // Set the src attribute to ""
  // images[i].src = "";
  // // Set the srcset attribute to ""
  // images[i].srcset = "";
  // // Display the alt text
  // images[i].style =
  //   "display: block; width: 100%; height: auto; margin: 0 auto;";
}
