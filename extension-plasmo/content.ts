// Browser add-on main.js
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  run_at: "document_end"
}

// Backend URL
// const BACKEND_URL = "https://image-alt-text-ai.onrender.com"
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

// Injext alt+i shortcut to focus on next image, alt+shift+i to focus on previous image
document.addEventListener("keydown", (e) => {
  if ((e.key === "i" || e.key === "u") && e.getModifierState("Alt")) {
    e.preventDefault()
    // Get the currently focused element
    try {
      const focusedElement = document.activeElement || document.body
      console.log("focusedElement: ", focusedElement)

      if (focusedElement) {
        // Get the previous sibling of the focused element
        if (e.key === "u") {
          console.log("Searching for previous image.")
          let prevElement
          if (focusedElement.tagName.toLowerCase() === "img") {
            if (focusedElement.previousElementSibling !== null) {
              prevElement = focusedElement.previousElementSibling
            } else {
              prevElement = focusedElement.parentElement
              while (
                prevElement &&
                prevElement.previousElementSibling === null
              ) {
                prevElement = prevElement.parentElement
              }
              prevElement = prevElement.previousElementSibling
            }
          } else {
            prevElement = focusedElement
          }

          // Traverse DOM until the previous <img> element is found
          while (prevElement) {
            // If the current element is an <img>, stop the loop
            if (prevElement.tagName.toLowerCase() === "img") {
              ;(prevElement as HTMLImageElement).focus()
              prevElement.scrollIntoView({
                behavior: "smooth",
                block: "center"
              })
              break
            }

            // If the current element's children contain an <img>, find it
            const imageChild = prevElement.querySelector("img")
            if (imageChild) {
              prevElement = imageChild
              ;(prevElement as HTMLImageElement).focus()
              prevElement.scrollIntoView({
                behavior: "smooth",
                block: "center"
              })
              break
            }

            // Move to the previous sibling or go up to the parent element
            if (!prevElement.previousElementSibling) {
              prevElement = prevElement.parentElement
              while (prevElement.previousElementSibling === null) {
                prevElement = prevElement.parentElement
              }
              prevElement = prevElement.previousElementSibling
            } else {
              prevElement = prevElement.previousElementSibling
            }
          }
        } else {
          let nextElement
          if (focusedElement.tagName.toLowerCase() === "img") {
            if (focusedElement.nextElementSibling !== null) {
              nextElement = focusedElement.nextElementSibling
            } else {
              nextElement = focusedElement.parentElement
              while (nextElement && nextElement.nextElementSibling === null) {
                nextElement = nextElement.parentElement
              }
              nextElement = nextElement.nextElementSibling
            }
          } else {
            nextElement = focusedElement
            // if (focusedElement.querySelector("img") !== null) {
            //   nextElement = focusedElement.querySelector("img")
            // } else {
            //   if (focusedElement.nextElementSibling !== null) {
            //     nextElement = focusedElement.nextElementSibling
            //   } else {
            //     nextElement = focusedElement.parentElement
            //     while (nextElement.nextElementSibling === null) {
            //       nextElement = nextElement.parentElement
            //     }
            //     nextElement = nextElement.nextElementSibling
            //   }
            // }
          }
          // focusedElement.tagName.toLowerCase() === "image"
          //   ? focusedElement.nextElementSibling ??
          //     focusedElement.parentElement.nextElementSibling
          //   : focusedElement.querySelector("img")

          // Traverse DOM until the previous <img> element is found
          while (nextElement) {
            // If the current element is an <img>, stop the loop
            if (nextElement.tagName.toLowerCase() === "img") {
              ;(nextElement as HTMLImageElement).focus()
              nextElement.scrollIntoView({
                behavior: "smooth",
                block: "center"
              })
              break
            }

            // If the current element's children contain an <img>, find it
            const imageChild = nextElement.querySelector("img")
            if (imageChild) {
              nextElement = imageChild
              ;(nextElement as HTMLImageElement).focus()
              nextElement.scrollIntoView({
                behavior: "smooth",
                block: "center"
              })
              break
            }

            // Move to the previous sibling or go up to the parent element
            if (!nextElement.nextElementSibling) {
              nextElement = nextElement.parentElement
              while (nextElement.nextElementSibling === null) {
                nextElement = nextElement.parentElement
              }
              nextElement = nextElement.nextElementSibling
            } else {
              nextElement = nextElement.nextElementSibling
            }
          }
        }
      } else {
        // TODO: delete this
        // Focus on the first image of the document
        const firstImage = document.querySelector("img")
        if (firstImage) {
          firstImage.focus()
        } else {
          console.log("No image found")
        }
      }
    } catch (e) {
      console.log(e)
    }
  }
})

function beep() {
  var snd = new Audio(
    "data:audio/wav;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU="
  )
  snd.play()
}
beep()

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

const processImage = (img: HTMLImageElement) => {
  // Check image format
  // We currently support PNG (.png), JPEG (.jpeg and .jpg), WEBP (.webp), and non-animated GIF (.gif).
  const imgSrc = img.src
  if (
    imgSrc.endsWith(".webp") ||
    imgSrc.endsWith(".svg") ||
    imgSrc.endsWith(".svgz") ||
    imgSrc.endsWith(".bmp") ||
    imgSrc.endsWith(".ico") ||
    imgSrc.endsWith(".cur") ||
    imgSrc.endsWith(".apng") ||
    imgSrc.endsWith(".avif") ||
    imgSrc.endsWith(".tiff") ||
    imgSrc.endsWith(".tif") ||
    imgSrc.endsWith(".jfif") ||
    imgSrc.endsWith(".pjpeg") ||
    imgSrc.endsWith(".pjp") ||
    imgSrc.endsWith(".pdf")
    // !imgSrc.endsWith(".png") &&
    // !imgSrc.endsWith(".jpeg") &&
    // !imgSrc.endsWith(".jpg") &&
    // !imgSrc.endsWith(".webp") &&
    // !imgSrc.endsWith(".gif")
  ) {
    return
  }
  totalImages++
  // Cover images to simulate blindness
  // img.src =
  //   "https://media.istockphoto.com/id/1265741003/video/pixel-censored-black-censor-bar-concept-censorship-rectangle-abstract-black-and-white-pixels.jpg?s=640x640&k=20&c=xN0KRE3vkdGeddUfkIf_Q_zsTQqMS4Kos7WCaiUYk8M="

  // Remove alt text
  img.alt = ""

  // Ensure images are focusable
  if (!img.hasAttribute("tabindex")) {
    img.setAttribute("tabindex", "0") // Make image focusable
  }

  // Add unique ID to image if it doesn't have one
  if (!img.id) {
    img.id = `img-${Math.random().toString(36).slice(2, 9)}`
  }

  // Add focus and blur event listeners to images
  img.addEventListener("focus", () => {
    img.classList.add("img-focused")
    beep()
  })
  img.addEventListener("blur", () => {
    img.classList.remove("img-focused")
  })

  // Add shortcut to generate alt text (Alt + A)
  img.addEventListener("keydown", (e) => {
    if (e.key === "a" && e.getModifierState("Alt")) {
      e.preventDefault()

      if (altTexts[img.id]) {
        // Set alt text to popup
        showPopup(
          img,
          `${altTexts[img.id].contextualAltText} (${(altTexts[img.id].contextualAltTextConfidence * 100).toFixed(2)}% confidence)`
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
            `${data.contextualAltText} (${(data.contextualAltTextConfidence * 100).toFixed(2)}% confidence)`
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
}

images.forEach((img) => {
  processImage(img as HTMLImageElement)
})

function eachNode(rootNode, callback) {
  if (!callback) {
    const nodes = []
    eachNode(rootNode, (node) => {
      nodes.push(node)
    })
    return nodes
  }

  if (callback(rootNode) === false) {
    return false
  }

  if (rootNode.hasChildNodes()) {
    for (const node of rootNode.childNodes) {
      if (eachNode(node, callback) === false) {
        return
      }
    }
  }
}

// Add mutation observer to process new images
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node instanceof HTMLImageElement) {
        console.log("AI ALT TEXT: New image found: ", node)
        processImage(node)
      } else {
        eachNode(node, (node) => {
          if (node instanceof HTMLImageElement) {
            console.log("AI ALT TEXT: New image found: ", node)
            processImage(node)
          }
        })
      }
    })
  })
})
observer.observe(document.body, {
  childList: true,
  subtree: true
})

console.log(`AI ALT TEXT: ${totalImages} images found`)

// alert(
//   "AI ALT TEXT: Alt text add-on working. Focus on an image and use the shortcut Alt + A to generate the alt text."
// )

export {}
