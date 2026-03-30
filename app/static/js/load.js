document.addEventListener("DOMContentLoaded", () => {
  const containers = document.querySelectorAll(".list-container");

  containers.forEach((container) => {
    const isDiscussion = container.closest("#discussion") !== null;
    const cards = isDiscussion
      ? container.querySelectorAll("a")
      : container.querySelectorAll(".beatmap-wrap");
    const showMoreBtn = container.querySelector(".show-more");
    const showLessBtn = container.querySelector(".show-less");

    let visibleCount = isDiscussion ? 3 : 6;
    const increment = isDiscussion ? 3 : 12;

    function updateView() {
      cards.forEach((card, index) => {
        card.style.display = index < visibleCount ? "block" : "none";
      });

      showMoreBtn.style.display =
        visibleCount >= cards.length ? "none" : "inline-block";

      showLessBtn.style.display =
        visibleCount > (isDiscussion ? 3 : 6) ? "inline-block" : "none";
    }

    showMoreBtn.addEventListener("click", () => {
      visibleCount += increment;
      updateView();
    });

    showLessBtn.addEventListener("click", () => {
      visibleCount -= increment;
      if (visibleCount < (isDiscussion ? 3 : 6))
        visibleCount = isDiscussion ? 3 : 6;
      updateView();
    });

    updateView();
  });
});
