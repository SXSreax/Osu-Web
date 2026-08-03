document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("file");
  const selectedFileName = document.getElementById("selected-file-name");
  const uploadMessage = document.getElementById("upload-message");

  if (!fileInput || !selectedFileName || !uploadMessage) {
    return;
  }

  fileInput.addEventListener("change", function () {
    const fileName =
      this.files && this.files.length > 0
        ? this.files[0].name
        : "No file selected";
    selectedFileName.textContent = fileName;
    uploadMessage.textContent = "File selected";
  });
});
