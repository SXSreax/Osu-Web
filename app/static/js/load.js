document.addEventListener("DOMContentLoaded", () => {
  const containers = document.querySelectorAll(".list-container");

  containers.forEach((container) => {
    const cards = container.querySelectorAll(".beatmap-wrap");
    const showMoreBtn = container.querySelector(".show-more");
    const showLessBtn = container.querySelector(".show-less");

    let visibleCount = 6;

    function updateView() {
      cards.forEach((card, index) => {
        card.style.display = index < visibleCount ? "block" : "none";
      });

      showMoreBtn.style.display =
        visibleCount >= cards.length ? "none" : "inline-block";

      showLessBtn.style.display = visibleCount > 6 ? "inline-block" : "none";
    }

    showMoreBtn.addEventListener("click", () => {
      visibleCount += 12;
      updateView();
    });

    showLessBtn.addEventListener("click", () => {
      visibleCount -= 12;
      if (visibleCount < 6) visibleCount = 6;
      updateView();
    });

    updateView();
  });
});
