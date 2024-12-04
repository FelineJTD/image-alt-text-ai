// Browser add-on main.js
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  run_at: "document_end"
}

// Add-on working
console.log("AI ALT TEXT: Alt text add-on working")

// Backend URL
const BACKEND_URL = "http://localhost:5000"

// Inject CSS to change focused element to have a purple border
const style = document.createElement("style")
style.textContent = `
  .img-focused {
    outline: 4px solid purple !important;
    outline-offset: 3px !important;
  }
`
document.head.appendChild(style)

// Inject pop-up for alt text
const popup = document.createElement("div")
popup.id = "popup-ai-alt-text"
popup.style.position = "fixed"
popup.ariaLive = "assertive"
popup.style.backgroundColor = "white"
popup.style.border = "1px solid black"
popup.style.padding = "8px"
popup.style.zIndex = "1000"
popup.style.display = "none"
document.body.appendChild(popup)

const images = document.querySelectorAll("img")
console.log("AI ALT TEXT: Found ", images.length, " images")

images.forEach((img) => {
  // Ensure images are focusable
  if (!img.hasAttribute("tabindex")) {
    img.setAttribute("tabindex", "0") // Make image focusable
  }

  // Add focus and blur event listeners to images
  img.addEventListener("focus", () => img.classList.add("img-focused"))
  img.addEventListener("blur", () => img.classList.remove("img-focused"))

  // Add shortcut to generate alt text (Ctrl + Alt + A)
  img.addEventListener("keydown", (e) => {
    if (e.key === "a" && e.ctrlKey && e.getModifierState("Alt")) {
      console.log("AI ALT TEXT: Generating alt text")
      // Send image URL to backend
      // fetch(`${BACKEND_URL}/image`, {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json"
      //   },
      //   body: JSON.stringify({
      //     url: img.src
      //   })
      // })
      //   .then((response) => response.json())
      //   .then((data) => {
      //     console.log(data)
      //     // Set alt text to image
      //     img.alt = data.alt
      //   })
      // Add pop up window directly above or below the image

      const altText = "Dummy alt text"

      // Change the position of the popup based on the position of the image
      const viewportOffset = img.getBoundingClientRect()
      const popup = document.getElementById("popup-ai-alt-text")
      popup.textContent = altText
      popup.style.top = `${viewportOffset.top + img.height + 4}px`
      popup.style.left = `${viewportOffset.left - 4}px`
      popup.style.display = "block"
    }
  })

  // Add event listener to remove popup when image is blurred
  img.addEventListener("blur", () => {
    const popup = document.getElementById("popup-ai-alt-text")
    popup.style.display = "none"
  })
})

// Make all images focusable and with purple border when focused whenever there is an update to the DOM
const observer = new MutationObserver((mutations) => {
  console.log("AI ALT TEXT: DOM updated")
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node instanceof HTMLImageElement) {
        console.log("AI ALT TEXT: Image added")
        node.tabIndex = 0
        node.addEventListener("focus", () => {
          node.classList.add("img-focused")
        })
        node.addEventListener("blur", () => {
          node.classList.remove("img-focused")
        })
      }
    })
  })
})

// Detect if user focuses on an image
document.addEventListener(
  "focus",
  (e) => {
    if (e.target instanceof HTMLImageElement) {
      console.log("AI ALT TEXT: Image focused")
      // Get the image src
      const src = e.target.src
      console.log("AI ALT TEXT: Image src: ", src)
      // Send image URL to backend
      //   fetch(`${BACKEND_URL}/image`, {
      //     method: "POST",
      //     headers: {
      //       "Content-Type": "application/json"
      //     },
      //     body: JSON.stringify({
      //       url: e.target.src
      //     })
      //   })
      //     .then((response) => response.json())
      //     .then((data) => {
      //       console.log(data)
      //       // Set alt text to image
      //       e.target.alt = data.alt
      //     })
      // }
    }
  },
  true
)

export {}
