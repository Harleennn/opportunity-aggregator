fetch("http://127.0.0.1:8000/api/summaries/")
  .then(response => response.json())
  .then(data => {
    const container = document.querySelector(".job-grid");

    // Loop through keys (URLs)
    for (const [url, summary] of Object.entries(data)) {
        const div = document.createElement("div");
        div.classList.add("job-card")
        div.innerHTML = `
            <p>${summary}</p>
            <button class="normal"><a class="job-link" href="${url}" target="_blank">Read More<img src="../icons/arrow-icon.png" alt="arrow-icon"></a></button>
        `;
        container.appendChild(div);
    } 
})