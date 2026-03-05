const avatarBtn = document.getElementById("avatar-btn");
const avatarMenu = document.getElementById("avatar-menu");

avatarBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  avatarMenu.style.display =
    avatarMenu.style.display === "block" ? "none" : "block";
});

document.addEventListener("click", () => {
  avatarMenu.style.display = "none";
});
