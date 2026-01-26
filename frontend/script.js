async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const output = document.getElementById("output");
    const loader = document.getElementById("loader");

    if (fileInput.files.length === 0) {
        alert("Please select a file first!");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    loader.style.display = "block";
    output.textContent = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/api/extract", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Extraction failed");
        }

        const data = await response.json();
        output.textContent = JSON.stringify(data, null, 2);

    } catch (error) {
        output.textContent = "❌ Error: " + error.message;
    } finally {
        loader.style.display = "none";
    }
}
