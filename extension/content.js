// content.js
// This script runs in the context of the web page.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractText") {
    // Extracting the innerText of the body as a simple starting point.
    // In a more advanced version, we could use a library like Readability.js.
    const pageText = document.body.innerText;
    const pageUrl = window.location.href;
    
    sendResponse({ text: pageText, url: pageUrl });
  }
  return true; // Keep the message channel open for sendResponse
});
