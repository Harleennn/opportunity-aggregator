fetch("http://127.0.0.1:8000/api/summaries/")
  .then(response => response.json())
  .then(data => {
    const container = document.querySelector(".job-grid");

    console.log("going to loop now")
    data.forEach(item => {
        console.log(item);
        const div = document.createElement("div");
        div.classList.add("job-card")
        div.innerHTML = `
            <h3>${item.title}</h3>
            <p>${item.summary}</p>
            <button class="normal"><a class="job-link" href="${item.url}" target="_blank">Read More<img src="../icons/arrow-icon.png" alt="arrow-icon"></a></button>
        `;
        container.appendChild(div);
    });
  });