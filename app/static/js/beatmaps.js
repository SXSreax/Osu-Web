document.addEventListener("DOMContentLoaded", function () {
  const playButtons = document.querySelectorAll(".play-button");
  const audioPlayer = document.getElementById("audio-player");
  let previewTimeout = null;

  playButtons.forEach((button) => {
    button.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const card = button.closest(".beatmap-card");
      const beatmapId = card.dataset.beatmapId;

      try {
        audioPlayer.pause();
        if (previewTimeout) {
          clearTimeout(previewTimeout);
          previewTimeout = null;
        }

        const response = await fetch(`/get-beatmap-audio/${beatmapId}`);
        const data = await response.json();

        if (data.audio_url) {
          audioPlayer.src = data.audio_url;
          audioPlayer.currentTime = 0;
          await audioPlayer.play();
          previewTimeout = setTimeout(() => {
            audioPlayer.pause();
            previewTimeout = null;
          }, 15000);
        } else {
          alert("No audio found for this beatmap");
        }
      } catch (err) {
        console.error("Error loading audio:", err);
        alert("Error loading audio");
      }
    });
  });

  applyStarColors();
});

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

  for (const segment of gradients) {
    if (rating >= segment.start && rating <= segment.end) {
      const t = (rating - segment.start) / (segment.end - segment.start);
      return lerpColor(segment.color1, segment.color2, t);
    }
  }

  return lerpColor(
    gradients[gradients.length - 1].color2,
    gradients[gradients.length - 1].color2,
    1,
  );
}

function applyStarColors() {
  document.querySelectorAll(".star-segment").forEach((segment) => {
    const star = parseFloat(segment.dataset.star);
    if (!isNaN(star)) {
      segment.style.backgroundColor = getStarColor(star);
    }
  });
}

document.querySelectorAll(".star-badge").forEach((badge) => {
  const star = parseFloat(badge.dataset.star);
  badge.style.backgroundColor = getStarColor(star);
});

document.addEventListener("DOMContentLoaded", () => {
  let expandedCard = null;
  let hoverTimeout = null;

  const cards = document.querySelectorAll(".beatmap-card");

  cards.forEach((card) => {
    const starBar = card.querySelector(".beatmap-star-bar");

    if (!starBar) return;

    starBar.addEventListener("mouseenter", () => {
      if (hoverTimeout) clearTimeout(hoverTimeout);

      hoverTimeout = setTimeout(() => {
        if (expandedCard && expandedCard !== card) {
          expandedCard.classList.remove("expanded");
        }

        card.classList.add("expanded");
        expandedCard = card;
      }, 300);
    });

    starBar.addEventListener("mouseleave", () => {
      if (hoverTimeout) {
        clearTimeout(hoverTimeout);
        hoverTimeout = null;
      }
    });

    card.addEventListener("mouseleave", () => {
      card.classList.remove("expanded");

      if (expandedCard === card) {
        expandedCard = null;
      }
    });
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".beatmap-card")) {
      if (expandedCard) {
        expandedCard.classList.remove("expanded");
        expandedCard = null;
      }
    }
  });
});
