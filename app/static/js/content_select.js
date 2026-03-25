function showTab(tabName) {
  document
    .querySelectorAll(".tab-content")
    .forEach((c) => (c.style.display = "none"));

  document
    .querySelectorAll(".tab-button")
    .forEach((b) => b.classList.remove("active"));

  document.getElementById(tabName).style.display = "block";
  document
    .querySelector(`.tab-button[onclick="showTab('${tabName}')"]`)
    .classList.add("active");
}
