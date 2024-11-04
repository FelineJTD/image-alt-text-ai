const handleToggleClick = () => {
  console.log("Button clicked");
};

// Add event listener to the button
const button = document.getElementById("toggle");
button.addEventListener("click", async () => {
  // Get the current tab
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });

  // Send a message to the content script in the current tab
  browser.tabs.sendMessage(tab.id, { action: "generateAltText" });
});
