// Create API Gateway client using SDK1
// Make sure apigClientFactory is available from apigClient.js
const apigClient = apigClientFactory.newClient({
  apiKey: "GKLoyNNltr6wqagH21qV71wEN9x97fN08m9Gx7IR",
});
// Base URL is already inside SDK via endpoint, but we must use correct stage (V1)

// ===== SEARCH =====
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const searchResultsDiv = document.getElementById("search-results");

searchButton.addEventListener("click", async () => {
  const query = searchInput.value.trim();
  if (!query) {
    searchResultsDiv.textContent = "Please enter a query.";
    return;
  }

  searchResultsDiv.innerHTML = "Searching...";

  const params = { q: query };
  const body = {};
  var additionalParams = {
    headers: {
      'Content-Type': 'application/json'
    }
  };

  try {
    const result = await apigClient.searchGet(params, body, additionalParams);
    console.log(result)
    const data = result.data;

    searchResultsDiv.innerHTML = "";

    const results = Array.isArray(data) ? data : data.results || [];

    console.log("results",results)

    if (!results.length) {
      searchResultsDiv.textContent = "No results.";
      return;
    }

    results.forEach((item) => {
      const REGION = "us-east-1";
      const imgUrl = `https://${
        item.bucket
      }.s3.${REGION}.amazonaws.com/${encodeURIComponent(item.key)}`;
      // If your bucket is a website bucket instead, use this:
      // const imgUrl = `http://${item.bucket}.s3-website-us-east-1.amazonaws.com/${encodeURIComponent(item.objectKey)}`;

      console.log("url",imgUrl)

      // Create a container for this result
      const card = document.createElement("div");
      card.className = "photo-card";
      card.style.display = "inline-block";
      card.style.margin = "10px";
      card.style.textAlign = "center";

      // Create the <img>
      const img = document.createElement("img");
      img.src = imgUrl;
      img.alt = (item.labels || []).join(", ") || item.key;
      img.style.maxWidth = "200px";
      img.style.maxHeight = "200px";
      img.style.display = "block";
      img.style.marginBottom = "5px";

      // If image fails to load, show a little message
      img.onerror = () => {
        img.style.display = "none";
        const errorMsg = document.createElement("div");
        errorMsg.textContent =
          "Image not accessible (check S3 permissions/URL)";
        card.appendChild(errorMsg);
      };

      // Caption: filename + labels
      const caption = document.createElement("div");
      caption.className = "photo-caption";
      const labelsText = (item.labels || []).join(", ");
      caption.textContent = `File: ${item.key}${
        labelsText ? " | Labels: " + labelsText : ""
      }`;

      card.appendChild(img);
      card.appendChild(caption);
      searchResultsDiv.appendChild(card);
    });
  } catch (err) {
    console.error(err);
    searchResultsDiv.textContent = "Error during search. Check console.";
  }
});

// ===== UPLOAD (BinaryString Version for uploadPut) =====
const fileInput = document.getElementById("file-input");
const labelsInput = document.getElementById("labels-input");
const uploadButton = document.getElementById("upload-button");
const uploadStatusDiv = document.getElementById("upload-status");

uploadButton.addEventListener("click", () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatusDiv.textContent = "Please choose a file first.";
    return;
  }

  const labelsRaw = labelsInput.value.trim();
  const labelsArray = labelsRaw
    ? labelsRaw.split(",").map((s) => s.trim()).filter((s) => s)
    : [];

  const customLabelsHeader = labelsArray.join(", "); // "cat, beach, sunset"

  uploadStatusDiv.textContent = "Uploading...";

  // ---- Read file as binary string (required for your Lambda logic) ----
  const reader = new FileReader();
  reader.readAsBinaryString(file);

  reader.onload = async function (e) {
    try {
      const binary = e.target.result;      // binary string
      const body = btoa(binary);           // base64 encoding
      console.log("Encoded length:", body.length);

      // --- build apigClient ---
      const apigClient = apigClientFactory.newClient({
        apiKey: "GKLoyNNltr6wqagH21qV71wEN9x97fN08m9Gx7IR",
      });

      // ===== IMPORTANT =====
      // uploadPut() takes:
      // uploadPut(params, body, additionalParams)
      // params = {}          (your SDK ignores them)
      // body = base64 string
      // additionalParams = headers
      // =====================

      const additionalParams = {
        headers: {
          "Content-Type": file.type || "application/octet-stream",
          "x-amz-meta-customLabels": customLabelsHeader,
        },
      };

      const params = { filename: file.name };
      const result = await apigClient.uploadPut(params, body, additionalParams);


      console.log("Upload result:", result);
      uploadStatusDiv.textContent = "Upload successful!";
      labelsInput.value = "";
    } catch (err) {
      console.error(err);
      uploadStatusDiv.textContent = "Upload failed. Check console.";
    }
  };
});
