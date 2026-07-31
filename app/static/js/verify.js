const OpenSetting = document.getElementById("setting-btn");
const CloseSetting = document.getElementById("close-setting-modal");
const modal = document.getElementById("setting-modal");

if (OpenSetting && modal) {
  OpenSetting.addEventListener("click", () => {
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
          throw new Error(`verify failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.verified && data.redirect) {
          window.location.href = data.redirect;
          return;
        }

        if (data.success) {
          modal.classList.add("open");
        } else {
          console.error("verify action failed", data.message);
          alert("Could not send verification email. Please try again later.");
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
