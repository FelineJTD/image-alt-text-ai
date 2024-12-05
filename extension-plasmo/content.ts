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

      // Get the current URL
      const docUrl = window.location.href
      console.log("AI ALT TEXT: Current URL: ", docUrl)

      // Get the website's title
      const docTitle = document.title
      console.log("AI ALT TEXT: Website title: ", docTitle)

      // Get the website description
      const docDescription = document
        .querySelector('meta[name="description"]')
        ?.getAttribute("content")
      console.log("AI ALT TEXT: Website description: ", docDescription)

      // Get all text in the document
      const docText = document.body.innerText
      console.log("AI ALT TEXT: Document text: ", docText)

      // Get the image src
      const imgSrc = img.src
      console.log("AI ALT TEXT: Image src: ", imgSrc)

      // Get the image alt text
      const imgAlt = img.alt
      console.log("AI ALT TEXT: Image alt: ", imgAlt)

      // Get the image attributes
      const imgAttrs = img.attributes
      console.log("AI ALT TEXT: Image attributes: ", imgAttrs)

      // Search 3 levels of parent elements for an <a> or <button> tag
      let imgAnchorOrButtonParent = null
      let parent = img.parentElement
      for (let i = 0; i < 3; i++) {
        if (parent.tagName === "A" || parent.tagName === "BUTTON") {
          imgAnchorOrButtonParent = parent
          break
        }
        parent = parent.parentElement
      }
      console.log(
        "AI ALT TEXT: Parent with <a> or <button> tag: ",
        imgAnchorOrButtonParent
      )

      // Search 10 levels of previous sibling elements for text
      let i = 0
      let imgPrevText = ""
      let currElement = img as HTMLElement
      while (i < 10) {
        // If there is a previous sibling, check if it contains text
        if (currElement.previousSibling) {
          console.log(
            "AI ALT TEXT: Previous sibling: ",
            currElement.previousSibling
          )
          imgPrevText = currElement.previousSibling.textContent

          // Clean the previous text (trim, remove new lines, make multiple spaces into one)
          imgPrevText = imgPrevText
            .trim()
            .replace(/\n/g, " ")
            .replace(/\s+/g, " ")
          // Break if text is found
          if (imgPrevText.length > 0) {
            break
          }
          currElement = currElement.previousSibling as HTMLElement
          i++
        } else {
          // Search parent element for text
          currElement = currElement.parentElement as HTMLElement
          // If parent is <body>, break
          if (currElement.tagName === "BODY") {
            break
          }
        }
      }
      console.log("AI ALT TEXT: Previous text: ", imgPrevText)

      // Search 10 levels of next sibling elements for text
      i = 0
      let imgNextText = ""
      currElement = img as HTMLElement
      while (i < 10) {
        // If there is a next sibling, check if it contains text
        if (currElement.nextSibling) {
          console.log("AI ALT TEXT: Next sibling: ", currElement.nextSibling)
          imgNextText = currElement.nextSibling.textContent

          // Clean the next text (trim, remove new lines, make multiple spaces into one)
          imgNextText = imgNextText
            .trim()
            .replace(/\n/g, " ")
            .replace(/\s+/g, " ")
          // Break if text is found
          if (imgNextText.length > 0) {
            break
          }
          currElement = currElement.nextSibling as HTMLElement
          i++
        } else {
          // Search parent element for text
          currElement = currElement.parentElement as HTMLElement
          // If parent is <body>, break
          if (currElement.tagName === "BODY") {
            break
          }
        }
      }
      console.log("AI ALT TEXT: Next text: ", imgNextText)

      // Combine all context
      const body = {
        docUrl,
        docTitle,
        docDescription,
        docText,
        imgSrc,
        imgAlt,
        imgAnchorOrButtonParent: imgAnchorOrButtonParent?.outerHTML,
        imgAttrs,
        imgPrevText,
        imgNextText
      }

      // Send image data to backend
      fetch(BACKEND_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("AI ALT TEXT: Received message from server: ", data)
          // Set alt text to image
          img.alt = data.contextualAltText

          // Set alt text to popup
          const viewportOffset = img.getBoundingClientRect()
          const popup = document.getElementById("popup-ai-alt-text")
          popup.style.top = `${viewportOffset.top + img.height + 4}px`
          popup.style.left = `${viewportOffset.left - 4}px`
          popup.style.opacity = "1"
          popup.textContent = `Descriptive: ${data.descriptiveAltText}\nContextual: ${data.contextualAltText}`
        })
    }
  })

  // Add event listener to remove popup when image is blurred
  img.addEventListener("blur", () => {
    const popup = document.getElementById("popup-ai-alt-text")
    popup.textContent = ""
    popup.style.opacity = "0"
  })
})

export {}
