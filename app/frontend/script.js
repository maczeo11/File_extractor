let lastResponseJSON = null;

async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const output = document.getElementById("output");
    const resultBox = document.getElementById("resultBox");
    const button = document.getElementById("extractBtn");
    const spinner = button.querySelector(".spinner");
    const btnText = button.querySelector(".btn-text");

    if (fileInput.files.length === 0) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // loading state
    btnText.style.display = "none";
    spinner.style.display = "inline-block";
    button.disabled = true;

    output.textContent = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/api/extract", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        lastResponseJSON = data;
        let text = "";

        data.pages.forEach((page, index) => {
            text += `Page ${index + 1}\n`;
            text += "----------------------------------------\n";
            text += page.text + "\n\n";
        });

        output.value = text;


    } catch (error) {
        output.textContent = "❌ Error extracting text";
        resultBox.classList.remove("hidden");
    } finally {
        spinner.style.display = "none";
        btnText.style.display = "inline";
        button.disabled = false;
    }
}

function downloadJSON() {
    if (!lastResponseJSON) {
        alert("No extracted data to download");
        return;
    }

    const blob = new Blob(
        [JSON.stringify(lastResponseJSON, null, 2)],
        { type: "application/json" }
    );

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "extracted_output.json";
    link.click();
}

