function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function setupHeader() {
  const header = document.querySelector("#site-header");
  if (!header) return;

  const toggle = header.querySelector(".nav-toggle");
  const navigation = header.querySelector(".header-nav");
  const progress = document.querySelector("#scroll-progress");
  const setOpen = (isOpen) => {
    header.classList.toggle("nav-open", isOpen);
    toggle?.setAttribute("aria-expanded", String(isOpen));
  };
  const updateScrollState = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = scrollableHeight > 0 ? Math.min(window.scrollY / scrollableHeight, 1) : 0;
    progress?.style.setProperty("transform", `scaleX(${ratio})`);
  };

  window.addEventListener("scroll", updateScrollState, { passive: true });
  window.addEventListener("resize", updateScrollState, { passive: true });

  toggle?.addEventListener("click", () => {
    setOpen(toggle.getAttribute("aria-expanded") !== "true");
  });
  navigation?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });
  document.addEventListener("click", (event) => {
    if (!header.contains(event.target)) setOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });

  updateScrollState();
}

function setupEvolutionControls() {
  const evolution = document.querySelector(".context-evolution");
  const buttons = [...document.querySelectorAll("[data-evolution-step]")];
  if (!evolution || !buttons.length) return;

  const stageDuration = 4500;
  const cycleDuration = stageDuration * buttons.length;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let timelineOrigin = performance.now();
  let activeStage = 0;

  const updateActiveStage = (index) => {
    activeStage = index;
    evolution.dataset.activeStage = String(index);
    buttons.forEach((button, buttonIndex) => {
      button.setAttribute("aria-pressed", String(buttonIndex === index));
    });
  };

  const jumpToStage = (index) => {
    const normalizedIndex = (index + buttons.length) % buttons.length;
    updateActiveStage(normalizedIndex);
    if (reducedMotion.matches) return;

    const phase = normalizedIndex * stageDuration + 350;
    evolution.style.setProperty("--evolution-offset", `${phase / 1000}s`);
    evolution.classList.add("is-resetting");
    void evolution.offsetWidth;
    evolution.classList.remove("is-resetting");
    timelineOrigin = performance.now() - phase;
  };

  buttons.forEach((button, index) => {
    button.addEventListener("click", () => jumpToStage(index));
    button.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const direction = event.key === "ArrowRight" ? 1 : -1;
      const nextIndex = (index + direction + buttons.length) % buttons.length;
      buttons[nextIndex].focus();
      jumpToStage(nextIndex);
    });
  });

  const syncStage = (now) => {
    if (!reducedMotion.matches) {
      const elapsed = ((now - timelineOrigin) % cycleDuration + cycleDuration) % cycleDuration;
      const nextStage = Math.floor(elapsed / stageDuration);
      if (nextStage !== activeStage) updateActiveStage(nextStage);
    }
    window.requestAnimationFrame(syncStage);
  };

  reducedMotion.addEventListener("change", () => jumpToStage(activeStage));
  jumpToStage(0);
  window.requestAnimationFrame(syncStage);
}

function setupCitationCopy() {
  const button = document.querySelector(".citation-copy");
  const citation = document.querySelector("#citation-text");
  const status = document.querySelector("#citation-copy-status");
  if (!button || !citation) return;

  const citationText = citation.textContent.trim();
  button.disabled = !citationText;
  button.setAttribute("aria-label", citationText ? "Copy citation" : "Citation not available yet");
  button.title = citationText ? "Copy citation" : "Citation not available yet";
  if (!citationText) return;

  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(citationText);
      button.classList.add("is-copied");
      button.setAttribute("aria-label", "Citation copied");
      if (status) status.textContent = "Citation copied";
      window.setTimeout(() => {
        button.classList.remove("is-copied");
        button.setAttribute("aria-label", "Copy citation");
        if (status) status.textContent = "";
      }, 1600);
    } catch {
      if (status) status.textContent = "Citation could not be copied";
    }
  });
}

setupHeader();
setupEvolutionControls();
setupCitationCopy();
refreshIcons();
