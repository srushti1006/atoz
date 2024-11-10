document.getElementById("fetch-btn").addEventListener("click", async () => {
    const url = document.getElementById("post-url").value;
    const responseContainer = document.getElementById("response-container");
    const imageContainer = document.getElementById("image-container");
    const captionContainer = document.getElementById("caption");
    const videoContainer = document.getElementById("video-container");
    const commentsContainer = document.getElementById("comments-container");

    // Clear previous data
    imageContainer.innerHTML = "";
    captionContainer.innerHTML = "";
    videoContainer.innerHTML = "";
    commentsContainer.innerHTML = "";

    if (!url) {
        alert("Please enter a valid Instagram URL");
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/process-url/?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (data.error) {
            alert(`Error fetching data: ${data.error}`);
            return;
        }

        // Display the image if available
        if (data.image_url) {
            const img = document.createElement("img");
            img.src = data.image_url;
            img.alt = "Instagram Post Image";
            img.style.maxWidth = "100%";
            imageContainer.appendChild(img);
        }

        // Display the caption if available
        if (data.caption) {
            captionContainer.textContent = data.caption;
        }

        // Display the video URL if available
        if (data.video_url) {
            const videoLink = document.createElement("a");
            videoLink.href = data.video_url;
            videoLink.target = "_blank";
            videoLink.textContent = "Watch Video";
            videoContainer.appendChild(videoLink);
        }

        // Display the comments if available
        if (data.comments && data.comments.length > 0) {
            commentsContainer.innerHTML = "<strong>Comments:</strong><br>";
            data.comments.forEach(comment => {
                const commentElement = document.createElement("p");
                commentElement.textContent = comment;
                commentsContainer.appendChild(commentElement);
            });
        } else {
            commentsContainer.textContent = "No comments available.";
        }

    } catch (error) {
        alert(`Error fetching data: ${error.message}`);
    }
});
