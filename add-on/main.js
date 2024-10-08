// Browser add-on main.js

// Add-on working
console.log("Alt text add-on working");

// Listen if there is a change in the DOM
document.addEventListener("DOMSubtreeModified", function () {
  // Get all images
  var images = document.getElementsByTagName("img");

  // Loop through all images
  for (var i = 0; i < images.length; i++) {
    console.log(images[i].alt);
    // If alt text is empty, set it to "Image"
    if (images[i].alt === "This contains an image of: ") {
      images[i].alt = "Image";
    }
  }
});
