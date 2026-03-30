document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.querySelector(".comment-input-wrapper textarea");

  function autoExpand(el) {
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";
  }

  autoExpand(textarea);

  textarea.addEventListener("input", function () {
    autoExpand(this);
  });
});

document.querySelectorAll(".checkbox").forEach((cb) => {
  cb.addEventListener("change", () => {
    const discussionId = cb.dataset.discussion;

    const container = cb.closest(".heart-container");
    const celebrate = container.querySelector(".svg-celebrate");
    celebrate.classList.add("animate");
    setTimeout(() => celebrate.classList.remove("animate"), 800);

    fetch(`/discussion/${discussionId}/favorite`, { method: "POST" });
  });
});
