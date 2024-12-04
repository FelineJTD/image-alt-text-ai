// Browser add-on main.js
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  run_at: "document_end"
}

// Backend URL
const BACKEND_URL = "http://localhost:5000"

// Add-on working
console.log("AI ALT TEXT: Alt text add-on working")

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
popup.style.color = "black"
popup.style.border = "1px solid black"
popup.style.padding = "8px"
popup.style.zIndex = "1000"
popup.style.opacity = "0"
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

      const url = window.location.href
      console.log("AI ALT TEXT: Current URL: ", url)

      // src: imageUrl,
      // alt: imageAlt,
      // attrs: imageAttrs,
      // a_button_parent: aButtonParent
      //   ? aButtonParent.outerHTML
      //   : "None",
      // prev_text: prevText,
      // next_text: nextText,

      // Get the image src
      const src = img.src
      console.log("AI ALT TEXT: Image src: ", src)

      // Get the image alt text
      const alt = img.alt
      console.log("AI ALT TEXT: Image alt: ", alt)

      // Get the image attributes
      const attrs = img.attributes
      console.log("AI ALT TEXT: Image attributes: ", attrs)

      // Search 3 levels of parent elements for an <a> or <button> tag
      let aButtonParent = null
      let parent = img.parentElement
      for (let i = 0; i < 3; i++) {
        if (parent.tagName === "A" || parent.tagName === "BUTTON") {
          aButtonParent = parent
          break
        }
        parent = parent.parentElement
      }
      console.log(
        "AI ALT TEXT: Parent with <a> or <button> tag: ",
        aButtonParent
      )

      // Search 5 levels of previous sibling elements for text
      let i = 0
      let prevText = ""
      let currElement = img as HTMLElement
      while (i < 5) {
        // If there is a previous sibling, check if it contains text
        if (currElement.previousSibling) {
          console.log(
            "AI ALT TEXT: Previous sibling: ",
            currElement.previousSibling
          )
          prevText = currElement.previousSibling.textContent

          // Clean the previous text (trim, remove new lines, make multiple spaces into one)
          prevText = prevText.trim().replace(/\n/g, " ").replace(/\s+/g, " ")
          // Break if text is found
          if (prevText.length > 0) {
            break
          }
          currElement = currElement.previousSibling as HTMLElement
          i++
        } else {
          // Search parent element for text
          currElement = currElement.parentElement as HTMLElement
        }
      }
      console.log("AI ALT TEXT: Previous text: ", prevText)

      // Search 5 levels of next sibling elements for text
      i = 0
      let nextText = ""
      currElement = img as HTMLElement
      while (i < 5) {
        // If there is a next sibling, check if it contains text
        if (currElement.nextSibling) {
          console.log("AI ALT TEXT: Next sibling: ", currElement.nextSibling)
          nextText = currElement.nextSibling.textContent

          // Clean the next text (trim, remove new lines, make multiple spaces into one)
          nextText = nextText.trim().replace(/\n/g, " ").replace(/\s+/g, " ")
          // Break if text is found
          if (nextText.length > 0) {
            break
          }
          currElement = currElement.nextSibling as HTMLElement
          i++
        } else {
          // Search parent element for text
          currElement = currElement.parentElement as HTMLElement
        }
      }
      console.log("AI ALT TEXT: Next text: ", nextText)

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
      popup.style.opacity = "1"
    }
  })

  // Add event listener to remove popup when image is blurred
  img.addEventListener("blur", () => {
    const popup = document.getElementById("popup-ai-alt-text")
    popup.textContent = ""
    popup.style.opacity = "0"
  })
})

// Detect if user focuses on an image
// document.addEventListener(
//   "focus",
//   (e) => {
//     if (e.target instanceof HTMLImageElement) {
//       console.log("AI ALT TEXT: Image focused")
//       // Get the image src
//       const src = e.target.src
//       console.log("AI ALT TEXT: Image src: ", src)
//       // Send image URL to backend
//       //   fetch(`${BACKEND_URL}/image`, {
//       //     method: "POST",
//       //     headers: {
//       //       "Content-Type": "application/json"
//       //     },
//       //     body: JSON.stringify({
//       //       url: e.target.src
//       //     })
//       //   })
//       //     .then((response) => response.json())
//       //     .then((data) => {
//       //       console.log(data)
//       //       // Set alt text to image
//       //       e.target.alt = data.alt
//       //     })
//       // }
//     }
//   },
//   true
// )

export {}
