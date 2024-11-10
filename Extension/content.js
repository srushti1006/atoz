// content.js
const postImage = document.querySelector("img[srcset]")?.src;
const caption = document.querySelector("div.C4VMK > span")?.innerText;
chrome.storage.local.set({ postImage, caption });  