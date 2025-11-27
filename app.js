// Create API Gateway client using SDK1
const apigClient = apigClientFactory.newClient({
  apiKey: "YOUR_API_KEY_HERE", // <-- paste your real key
});

// ... search code stays the same ...

// ===== UPLOAD =====
const fileInput = document.getElementById("file-input");
const labelsInput = document.getElementById("labels-input");
const uploadButton = document.getElementById("upload-button");
const uploadStatusDiv = document.getElementById("upload-status");

uploadButton.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatusDiv.textContent = "Please choose a file first.";
    return;
  }

  const labelsRaw = labelsInput.value.trim();
  const labelsArray = labelsRaw
    ? labelsRaw
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0)
    : [];
  const customLabelsHeader = labelsArray.join(", "); // "Sam, Sally"

  uploadStatusDiv.textContent = "Uploading...";

  const params = {
    filename: file.name, // maps to ?filename=...
  };

  const body = file;

  const additionalParams = {
    headers: {
      "Content-Type": file.type || "application/octet-stream",
      "x-amz-meta-customLabels": customLabelsHeader,
    },
  };

  try {
    // PATH IS /upload with PUT -> method name is uploadPut
    const result = await apigClient.uploadPut(params, body, additionalParams);
    console.log(result);
    uploadStatusDiv.textContent = "Upload successful!";
  } catch (err) {
    console.error(err);
    uploadStatusDiv.textContent = "Upload failed. Check console.";
  }
});
