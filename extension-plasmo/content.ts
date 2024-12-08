// Browser add-on main.js
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  run_at: "document_end"
}

// Backend URL
const BACKEND_URL = "https://image-alt-text-ai.onrender.com"
// const BACKEND_URL = "http://localhost:5000"

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
popup.style.overflowY = "auto"
document.body.appendChild(popup)

const images = document.querySelectorAll("img")
let totalImages = 0
let altTexts = {}

// const revealImage = (imgId: string, imgSrc: string) => {
//   const img = document.getElementById(imgId) as HTMLImageElement
//   img.src = imgSrc
// }

const showPopup = (img: HTMLImageElement, content: string) => {
  const viewportOffset = img.getBoundingClientRect()
  const popup = document.getElementById("popup-ai-alt-text")
  popup.style.top = `${viewportOffset.top + img.height + 4}px`
  popup.style.left = `${viewportOffset.left - 4}px`
  popup.style.opacity = "1"
  popup.style.maxWidth = `${img.width + 8 > 300 ? img.width + 8 : 300}px`
  popup.style.maxHeight = `${
    window.innerHeight - viewportOffset.top - img.height - 4
  }px`
  popup.innerHTML = content
}

images.forEach((img) => {
  // Check image format
  // We currently support PNG (.png), JPEG (.jpeg and .jpg), WEBP (.webp), and non-animated GIF (.gif).
  const imgSrc = img.src
  if (
    !imgSrc.endsWith(".png") &&
    !imgSrc.endsWith(".jpeg") &&
    !imgSrc.endsWith(".jpg") &&
    !imgSrc.endsWith(".webp") &&
    !imgSrc.endsWith(".gif")
  ) {
    return
  }
  totalImages++
  // Cover images to simulate blindness
  // img.src =
  //   "https://media.istockphoto.com/id/1265741003/video/pixel-censored-black-censor-bar-concept-censorship-rectangle-abstract-black-and-white-pixels.jpg?s=640x640&k=20&c=xN0KRE3vkdGeddUfkIf_Q_zsTQqMS4Kos7WCaiUYk8M="

  // Ensure images are focusable
  if (!img.hasAttribute("tabindex")) {
    img.setAttribute("tabindex", "1") // Make image focusable
  }

  // Add unique ID to image if it doesn't have one
  if (!img.id) {
    img.id = `img-${Math.random().toString(36).slice(2, 9)}`
  }

  // Add focus and blur event listeners to images
  img.addEventListener("focus", () => img.classList.add("img-focused"))
  img.addEventListener("blur", () => img.classList.remove("img-focused"))

  // Add shortcut to generate alt text (Alt + A)
  img.addEventListener("keydown", (e) => {
    if (e.key === "a" && e.getModifierState("Alt")) {
      e.preventDefault()

      if (altTexts[img.id]) {
        // Set alt text to popup
        showPopup(
          img,
          `<strong>Human:</strong> ${altTexts[img.id].humanAltText}<br><strong>Descriptive AI:</strong> ${altTexts[img.id].descriptiveAltText}<br><strong>Contextual AI:</strong> ${altTexts[img.id].contextualAltText} (${(altTexts[img.id].contextualAltTextConfidence * 100).toFixed(2)}% confidence)`
        )
        return
      }

      // Loading
      showPopup(img, "Generating alt text...")

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
      console.log("AI ALT TEXT: Image src: ", imgSrc)

      // Get the image alt text
      const imgAlt = img.alt
      console.log("AI ALT TEXT: Image alt: ", imgAlt)

      // Get the image attributes
      const imgAttrs = img
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

      // Search 10 levels of previous sibling elements for text and header
      let i = 0
      let imgPrevText = ""
      let imgPrevElements = null
      let imgHeader = ""
      let currElement = img as HTMLElement
      while (i < 20) {
        // If there is a previous sibling, check if it contains text
        imgPrevElements = currElement.previousSibling
        if (
          imgPrevElements &&
          (imgPrevElements.nodeType === 1 || imgPrevElements.nodeType === 3)
        ) {
          console.log("AI ALT TEXT: Previous sibling: ", imgPrevElements)
          if (imgPrevText === "") {
            imgPrevText = imgPrevElements.textContent
          }
          // Search for header element in imgPrevElements
          if (
            imgPrevElements.nodeType === 1 &&
            imgPrevElements.querySelector("h1, h2, h3, h4, h5, h6") !== null
          ) {
            console.log(
              "AI ALT TEXT: Header element found: ",
              imgPrevElements.querySelector("h1, h2, h3, h4, h5, h6")
            )
            imgHeader = imgPrevElements.querySelector(
              "h1, h2, h3, h4, h5, h6"
            ).textContent
          }

          // Clean the previous text (trim, remove new lines, make multiple spaces into one)
          imgPrevText = imgPrevText
            .trim()
            .replace(/\n/g, " ")
            .replace(/\s+/g, " ")
          // Break if text is found
          if (imgPrevText.length > 0 && imgHeader.length > 0) {
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
      console.log("AI ALT TEXT: Previous header: ", imgHeader)

      // Search 10 levels of next sibling elements for text and header
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
        imgAttrs: imgAttrs.outerHTML,
        imgPrevText,
        imgHeader,
        imgNextText
      }

      console.log("AI ALT TEXT: Sending message to server: ", body)

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
          // Save alt text to altTexts
          if (!altTexts[img.id]) {
            altTexts[img.id] = data
          }

          // Set alt text to popup
          showPopup(
            img,
            `<strong>Human:</strong> ${data.humanAltText}<br><strong>Descriptive AI:</strong> ${data.descriptiveAltText}<br><strong>Contextual AI:</strong> ${data.contextualAltText} (${(data.contextualAltTextConfidence * 100).toFixed(2)}% confidence)`
          )
        })
    }
  })

  // Add event listener to remove popup when image is blurred
  img.addEventListener("blur", () => {
    // If selection is not in popup, remove popup
    const popup = document.getElementById("popup-ai-alt-text")
    if (!popup.contains(document.activeElement)) {
      popup.style.opacity = "0"
      popup.textContent = ""
    }
  })
})

console.log(`AI ALT TEXT: ${totalImages} images found`)

// alert(
//   "AI ALT TEXT: Alt text add-on working. Focus on an image and use the shortcut Alt + A to generate the alt text."
// )

export {}
