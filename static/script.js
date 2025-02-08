function organizeFiles() {
    let folderPath = document.getElementById("folderPath").value;
    let messageElement = document.getElementById("message");

    if (!folderPath) {
        messageElement.innerText = "Please enter a folder path.";
        return;
    }

    fetch("/organize", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ folderPath: folderPath })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            messageElement.innerText = "Error: " + data.error;
        } else {
            messageElement.innerText = "Success: " + data.success;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        messageElement.innerText = "An error occurred.";
    });
}