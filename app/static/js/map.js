const downloadModal = document.getElementById("download-modal");
const downloadTrigger = document.getElementById("download-trigger-btn");
const closeModalBtn = document.getElementById("close-modal-btn");
const modalOverlay = document.querySelector(".download-modal-overlay");

downloadTrigger.addEventListener("click", () => {
  downloadModal.classList.add("active");
});

closeModalBtn.addEventListener("click", () => {
  downloadModal.classList.remove("active");
});

modalOverlay.addEventListener("click", () => {
  downloadModal.classList.remove("active");
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    downloadModal.classList.remove("active");
  }
});
