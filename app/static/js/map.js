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

document.addEventListener("DOMContentLoaded", () => {
  applyStarColors();
  applyCoverImage();
});

function applyCoverImage() {
  const wrapper = document.querySelector(".map-content-wrapper");
  if (wrapper && wrapper.dataset.coverImage) {
    wrapper.style.backgroundImage = `url(${wrapper.dataset.coverImage})`;
  }
}

function lerpColor(color1, color2, t) {
  const r = Math.round(color1[0] + (color2[0] - color1[0]) * t);
  const g = Math.round(color1[1] + (color2[1] - color1[1]) * t);
  const b = Math.round(color1[2] + (color2[2] - color1[2]) * t);
  return `rgb(${r}, ${g}, ${b})`;
}

function getStarColor(starRating) {
  const rating = Math.max(0, Math.min(8, starRating));

  const gradients = [
    { start: 0.0, end: 2.0, color1: [0, 255, 255], color2: [0, 255, 0] },
    { start: 2.0, end: 2.7, color1: [0, 255, 0], color2: [255, 255, 0] },
    { start: 2.7, end: 4.0, color1: [255, 255, 0], color2: [255, 200, 0] },
    { start: 4.0, end: 5.3, color1: [255, 165, 0], color2: [255, 0, 127] },
    { start: 5.3, end: 6.5, color1: [255, 0, 127], color2: [200, 0, 255] },
    { start: 6.5, end: 8.0, color1: [200, 0, 255], color2: [100, 0, 255] },
  ];

  for (const circle of gradients) {
    if (rating >= circle.start && rating <= circle.end) {
      const t = (rating - circle.start) / (circle.end - circle.start);
      return lerpColor(circle.color1, circle.color2, t);
    }
  }

  return lerpColor(
    gradients[gradients.length - 1].color2,
    gradients[gradients.length - 1].color2,
    1,
  );
}

document.addEventListener("DOMContentLoaded", () => {
  const display = document.getElementById("star-info");
  let selectedCircle = null;

  document.querySelectorAll(".star-circle").forEach((circle) => {
    const star = parseFloat(circle.dataset.star);
    if (!isNaN(star)) {
      circle.style.backgroundColor = getStarColor(star);
    }

    const nameSpan = display.querySelector(".star-name");
    const rateSpan = display.querySelector(".star-rate");
    const hpSpan = display.querySelector(".hp");
    const odSpan = display.querySelector(".od");
    const csSpan = display.querySelector(".cs");
    const arSpan = display.querySelector(".ar");
    const kcSpan = display.querySelector(".kc");

    const showInfo = () => {
      nameSpan.textContent = circle.dataset.name;
      rateSpan.textContent = "Star Rate" + " " + circle.dataset.star;
      hpSpan.innerHTML = circle.dataset.hp
        ? `<span class="label">HP Drain</span> <span class="value">${circle.dataset.hp}</span>`
        : "";

      odSpan.innerHTML = circle.dataset.od
        ? `<span class="label">Accuracy</span> <span class="value">${circle.dataset.od}</span>`
        : "";

      csSpan.innerHTML = circle.dataset.cs
        ? `<span class="label">Circle Size</span> <span class="value">${circle.dataset.cs}</span>`
        : "";

      arSpan.innerHTML = circle.dataset.ar
        ? `<span class="label">Approach Rate</span> <span class="value">${circle.dataset.ar}</span>`
        : "";

      kcSpan.innerHTML = circle.dataset.kc
        ? `<span class="label">Key Count</span> <span class="value">${circle.dataset.kc}</span>`
        : "";
    };

    circle.addEventListener("mouseenter", showInfo);

    circle.addEventListener("click", () => {
      selectedCircle = circle;
      showInfo();
    });

    circle.addEventListener("mouseleave", () => {
      if (selectedCircle !== circle) {
        nameSpan.textContent = "";
        rateSpan.textContent = "";
        hpSpan.textContent = "";
        odSpan.textContent = "";
        csSpan.textContent = "";
        arSpan.textContent = "";
        kcSpan.textContent = "";
      }
    });
  });
});

document.querySelectorAll(".checkbox").forEach((cb) => {
  cb.addEventListener("change", () => {
    const mapId = cb.dataset.map;

    const container = cb.closest(".heart-container");
    const celebrate = container.querySelector(".svg-celebrate");
    celebrate.classList.add("animate");
    setTimeout(() => celebrate.classList.remove("animate"), 800);

    fetch(`/map/${mapId}/favorite`, { method: "POST" });
  });
});
