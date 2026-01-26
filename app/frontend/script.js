let lastUploadedFile = null;

async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const output = document.getElementById("output");

    if (fileInput.files.length === 0) {
        alert("Please select a file");
        return;
    }

    lastUploadedFile = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", lastUploadedFile);

    output.value = "Extracting text...";

    const response = await fetch("http://127.0.0.1:8000/api/extract", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    output.value = data.extracted_text;
}

async function downloadJSON() {
    if (!lastUploadedFile) {
        alert("Please extract a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", lastUploadedFile);

    const response = await fetch("http://127.0.0.1:8000/api/extract/json", {
        method: "POST",
        body: formData
    });

    const jsonData = await response.json();

    const blob = new Blob(
        [JSON.stringify(jsonData, null, 2)],
        { type: "application/json" }
    );

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "extracted_output.json";
    link.click();
}
