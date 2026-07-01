const OpenSetting = document.getElementById("setting-btn");
const CloseSetting = document.getElementById("close-setting-modal");
const modal = document.getElementById("setting-modal");

if (OpenSetting && modal) {
  OpenSetting.addEventListener("click", () => {
    modal.classList.add("open");

    fetch("/user/verify/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ action: "open_settings" }),
    })
      .then((response) => {
        if (!response.ok) {
          console.error("verify failed", response.status);
        }
      })
      .catch((error) => {
        console.error("verify action error", error);
      });
  });
}

if (CloseSetting && modal) {
  CloseSetting.addEventListener("click", () => {
    modal.classList.remove("open");
  });
}
