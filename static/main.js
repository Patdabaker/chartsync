let omit = [];
let songs = [];
let name = '';
function buildPayload(form, omit) {
    // collect data from html form
    let formName = form.playlistName.value;
    if (formName === '') {
        formName = name;
    }
    return {
        chart: form.chart.value,
        start: form.startDate.value,
        end: form.endDate.value,
        name: formName,
        amount: Number(form.songAmount.value),
        omit: omit,
        songs: songs
    };
}
document.addEventListener("DOMContentLoaded", (event) => {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const select = document.getElementById('chart');
    const form = document.getElementById('form');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    const buttons = document.getElementById('buttons');
    const startDateInput = document.getElementById('startDateInput');
    const endDateInput = document.getElementById('endDateInput');

    async function generatePlaylist(payload) {
        // show loading message
        loading.style.display = 'block';
        loading.innerHTML = '<p>Generating Playlist... Please Wait</p>';

        // send data to python route
        const res = await fetch("/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        // receive data from python route
        const data = await res.json();

        if (!res.ok) {
            results.innerHTML = `<p class="error">Server error. Try again.</p>`;
            return;
        }

        // hide form
        form.style.display = 'none';

        // show results
        results.style.display = 'block';
        buttons.style.display = 'block';
        loading.style.display = 'none';

        if (!data.success) {
            // show error
            results.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        name = data.playlistName;
        songs = data.songs;

        results.innerHTML = `
            <h2>${data.playlistName}</h2>
            <p>Fine-tune your playlist: remove tracks with the checkboxes and regenerate, or save your curated version to Spotify</p>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Img</th>
                        <th>Title</th>
                        <th>Artist</th>
                        <th>Delete?</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.songs.map(song => `
                    <tr>
                        <td>${song[0]}</td>
                        <td><img src=${song[1]} alt="album art" width="50" height="50"></td>
                        <td class="title">${song[2]}</td>
                        <td class="artist">${song[3]}</td>
                        <td><input type="checkbox" class="song-checkbox"></td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        // Highlight whole row if checkbox is checked
        document.addEventListener("change", e => {
        if (e.target.classList.contains('song-checkbox')) {
            const row = e.target.closest("tr");
            if (e.target.checked) {
                row.classList.add("highlighted");
            } else {
                row.classList.remove("highlighted");
            }
        }
    });

};

    select.addEventListener("change", () => {
        if (select.value !== "") {
            startDate.hidden = false;
            endDate.hidden = false;
            let chart = select.value;
            startDateInput.value = '';
            endDateInput.value = '',
            startDateInput.setAttribute('min', chartRanges[chart]['min']);
            startDateInput.setAttribute('max', chartRanges[chart]['max']);
            endDateInput.setAttribute('min', chartRanges[chart]['min']);
            endDateInput.setAttribute('max', chartRanges[chart]['max']);
        } 
    });

    // reset fields
    form.addEventListener("reset", () => {
        form.reset();
        startDate.hidden = true;
        endDate.hidden = true;
    });

    form.addEventListener("submit", async (e) => {
        const sdi = startDateInput.value;
        const edi = endDateInput.value;

        if (sdi && edi && sdi > edi) {
            e.preventDefault();
            alert("Start date must be before end date");
            return;
        }
        // prevent form submit and page reload
        e.preventDefault();

        generatePlaylist(buildPayload(form, omit));
    });
                
    // hides deleted rows based on checked checkboxes
    document.getElementById("deleteChecked").addEventListener("click", () => {
        const checkboxes = document.querySelectorAll(".song-checkbox:checked");

        checkboxes.forEach(checkbox => {
            checkbox.closest("tr").style.display = 'none';            
        });

        const rows = document.querySelectorAll("table tr");

        rows.forEach(row => {
            if (row.style.display === 'none') {
                const title = row.querySelector(".title").textContent;
                const artist = row.querySelector(".artist").textContent;
                omit.push([title, artist]);
            }
        });
    });
    
    // Add back button
    const back = document.getElementById('back');
    back.addEventListener("click", () => {
        results.style.display = 'none';
        form.style.display = 'block';
        results.innerHTML = '';
        buttons.style.display = 'none';
        back.innerHTML = 'Back';
        omit = [];
        name = '';
    });

    // Regenerate playlist with deleted in mind
    document.getElementById('regenerate').addEventListener("click", () => {
        generatePlaylist(buildPayload(form, omit));
    });

    // Add playlist to spotify
    document.getElementById('add').addEventListener("click", async () => {
        // show loading message
        loading.style.display = 'block';
        loading.innerHTML = '<p>Adding Playlist... Please Wait</p>';
        
        // send data to python route
        const res = await fetch("/add", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(buildPayload(form, omit))
        });

        // receive data from python route
        const data = await res.json();
        if (!res.ok) {
            results.innerHTML = `<p class="error">Server error. Try again.</p>`;
            return;
        }

        if (!data.success) {
            // show error
            results.innerHTML = `<p class="error">${data.error}</p`;
            return;
        }
        
        results.innerHTML = `
            <p>Successfully added, check Spotify account!</p>
            `
        let failedSongs = document.getElementById('failedSongs');
        failedSongs.style.display = 'block';
        failedSongs.innerHTML = `
            <br>
            <p>Failed to add these songs, consider adding them manually</p>
            <table>
                <thead>
                    <tr>
                        <th>Img</th>
                        <th>Title</th>
                        <th>Artist</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.failed.map(song => `
                    <tr>
                        <td><img src=${song[0]} alt="album art" width="50" height="50"></td>
                        <td class="title">${song[1]}</td>
                        <td class="artist">${song[2]}</td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        if (data.failed.length === 0) {
            failedSongs.style.display = 'none';
            failedSongs.innerHTML = '';
        }
        loading.style.display = 'none';
        loading.innerHTML = '';
        buttons.style.display = 'none';
        let gap = document.getElementById('gap');
        gap.hidden = false;
        gap.addEventListener("click", () => {
            results.style.display = 'none';
            form.style.display = 'block';
            results.innerHTML = '';
            buttons.style.display = 'none';
            back.innerHTML = 'Back';
            failedSongs.style.display = 'none';
            gap.hidden = true;
            form.reset();
            startDate.hidden = true;
            endDate.hidden = true;
            omit = [];
        });
    });
});