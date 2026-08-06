document.addEventListener("DOMContentLoaded", function () {
  const quill = new Quill("#editor", {
    theme: "snow",
    placeholder: "Write your discussion...",
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ["bold", "italic", "underline", "strike"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["blockquote", "code-block"],
        ["link"],
        ["clean"],
      ],
    },
  });

  const contentField = document.getElementById("content");
  const discussionForm = document.getElementById("discussion-form");

  if (contentField) {
    quill.root.innerHTML = contentField.value;
  }

  if (discussionForm) {
    discussionForm.addEventListener("submit", function () {
      if (contentField) {
        contentField.value = quill.root.innerHTML;
      }
    });
  }
});
