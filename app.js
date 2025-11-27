// Create API Gateway client using SDK1
// Make sure apigClientFactory is available from apigClient.js
const apigClient = apigClientFactory.newClient({
  apiKey: "",
});
// Base URL is already inside SDK via endpoint, but we must use correct stage (V1)

// ===== SEARCH =====
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const searchResultsDiv = document.getElementById("search-results");

searchButton.addEventListener("click", async () => {
  const query = searchInput.value.trim();
  searchResultsDiv.innerHTML = "Searching...";

  const params = {
    q: query,
  };
  const body = {};
  const additionalParams = {};

  try {
    // method name pattern from SDK: {path}{Method}
    // Path is /search with GET -> searchGet
    const result = await apigClient.searchGet(params, body, additionalParams);

    // result.data should be whatever your Lambda returns (array or {results: [...]})
    const data = result.data;

    searchResultsDiv.innerHTML = "";

    const results = Array.isArray(data) ? data : data.results || [];

    if (!results.length) {
      searchResultsDiv.textContent = "No results.";
      return;
    }

    results.forEach((item) => {
      // Assume your index has objectKey and bucket, so S3 URL:
      const url = `https://${item.bucket}.s3.amazonaws.com/${item.objectKey}`;
      const img = document.createElement("img");
      img.src = url;
      img.alt = (item.labels || []).join(", ");
      searchResultsDiv.appendChild(img);
    });
  } catch (err) {
    console.error(err);
    searchResultsDiv.textContent = "Error during search. Check console.";
  }
});

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
