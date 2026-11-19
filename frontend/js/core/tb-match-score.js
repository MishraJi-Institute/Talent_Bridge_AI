/**
 * Illustrative AI candidate matching showcase.
 * Demo profiles only — not live AI matching or real platform users.
 * Orbit → approach → select → cinematic zoom state machine.
 */
(function () {
  "use strict";

  var SCENE_SEL = "[data-tb-match-showcase]";

  // True 360° circular revolution (equal radius). Keep 14–18s per lap.
  var ORBIT_PERIOD_MS = 16000;
  var APPROACH_MS = 1000;
  var FADE_MS = 600;
  var ZOOM_IN_MS = 2800;
  var ZOOM_OUT_MS = 2000;
  var HOLD_MS = 650;
  var SCORE_MS = 900;
  var ZOOM_PEAK = 1.28;

  var PHASE = {
    ORBITING: "ORBITING",
    APPROACHING: "APPROACHING",
    SELECTING: "SELECTING",
    ACTIVE: "ACTIVE",
    ZOOMING_IN: "ZOOMING_IN",
    ZOOMING_OUT: "ZOOMING_OUT",
    WAITING_FOR_NEXT: "WAITING_FOR_NEXT"
  };

  var CANDIDATES = [
    {
      id: "rahil",
      name: "Rahil Sharma",
      role: "Python Developer",
      skills: "Python, Django, REST APIs",
      experience: "5 Years",
      education: "M.S. Computer Science",
      softSkills: "Leadership, Communication",
      chips: ["+15% Python", "+12% Django", "+10% experience"],
      score: 98,
      fitLabel: "Excellent fit",
      image: "/images/tb-match-rahil.jpg?v=2",
      alt: "Illustrative demo portrait of Rahil Sharma, Python Developer",
      objectPosition: "50% 28%",
      zoomOrigin: "50% 26%"
    },
    {
      id: "ananya",
      name: "Ananya Verma",
      role: "Data Scientist",
      skills: "Python, Machine Learning, SQL",
      experience: "4 Years",
      education: "M.Sc. Data Science",
      softSkills: "Analytics, Storytelling",
      chips: ["+14% ML", "+12% Python", "+9% SQL"],
      score: 94,
      fitLabel: "Strong fit",
      image: "/images/tb-match-ananya.jpg?v=2",
      alt: "Illustrative demo portrait of Ananya Verma, Data Scientist",
      objectPosition: "50% 22%",
      zoomOrigin: "50% 24%"
    },
    {
      id: "arjun",
      name: "Arjun Mehta",
      role: "Full Stack Developer",
      skills: "React, Node.js, PostgreSQL",
      experience: "6 Years",
      education: "B.Tech Computer Science",
      softSkills: "Collaboration, Ownership",
      chips: ["+13% React", "+11% Node.js", "+10% experience"],
      score: 91,
      fitLabel: "Great fit",
      image: "/images/tb-match-arjun.jpg?v=3",
      alt: "Illustrative demo portrait of Arjun Mehta, Full Stack Developer",
      objectPosition: "50% 30%",
      zoomOrigin: "50% 28%"
    },
    {
      id: "priya",
      name: "Priya Singh",
      role: "UI/UX Designer",
      skills: "Figma, UX Research, Design Systems",
      experience: "5 Years",
      education: "B.Des.",
      softSkills: "Empathy, Facilitation",
      chips: ["+15% Figma", "+12% research", "+10% systems"],
      score: 96,
      fitLabel: "Excellent fit",
      image: "/images/tb-match-priya.jpg?v=2",
      alt: "Illustrative demo portrait of Priya Singh, UI/UX Designer",
      objectPosition: "50% 24%",
      zoomOrigin: "50% 26%"
    },
    {
      id: "karan",
      name: "Karan Patel",
      role: "Cloud Engineer",
      skills: "AWS, Docker, Kubernetes",
      experience: "4 Years",
      education: "B.Tech Information Technology",
      softSkills: "Reliability, Mentoring",
      chips: ["+14% AWS", "+11% Kubernetes", "+9% Docker"],
      score: 93,
      fitLabel: "Strong fit",
      image: "/images/tb-match-karan.jpg?v=2",
      alt: "Illustrative demo portrait of Karan Patel, Cloud Engineer",
      objectPosition: "50% 20%",
      zoomOrigin: "50% 22%"
    }
  ];

  var state = {
    index: 0,
    nextIndex: 1,
    phase: PHASE.ACTIVE,
    busy: false,
    started: false,
    visible: true,
    angle: -Math.PI / 2,
    orbitSpeed: 1,
    orbitRaf: null,
    scoreRaf: null,
    holdTimer: null,
    phaseTimer: null,
    zoomAnim: null,
    approachAnim: null,
    flyer: null,
    lastOrbitTs: 0,
    nodes: [],
    scene: null
  };

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function clampScore(value) {
    var n = Number(value);
    if (!isFinite(n)) return 0;
    return Math.max(0, Math.min(100, Math.round(n)));
  }

  function qs(root, sel) {
    return root.querySelector(sel);
  }

  function setText(el, value) {
    if (el) el.textContent = value;
  }

  function clearHold() {
    if (state.holdTimer) {
      window.clearTimeout(state.holdTimer);
      state.holdTimer = null;
    }
  }

  function clearPhaseTimer() {
    if (state.phaseTimer) {
      window.clearTimeout(state.phaseTimer);
      state.phaseTimer = null;
    }
  }

  function cancelScoreRaf() {
    if (state.scoreRaf) {
      window.cancelAnimationFrame(state.scoreRaf);
      state.scoreRaf = null;
    }
  }

  function cancelOrbitRaf() {
    if (state.orbitRaf) {
      window.cancelAnimationFrame(state.orbitRaf);
      state.orbitRaf = null;
    }
    state.lastOrbitTs = 0;
  }

  function cancelZoom() {
    if (state.zoomAnim) {
      try {
        state.zoomAnim.cancel();
      } catch (e) {
        /* ignore */
      }
      state.zoomAnim = null;
    }
    if (!state.scene) return;
    var img = qs(state.scene, '[data-tb-match-field="image"]');
    if (img) {
      img.classList.remove("is-zooming", "is-popout");
      img.style.removeProperty("transform");
      img.style.removeProperty("box-shadow");
    }
    var photo = qs(state.scene, ".tb-match-profile__photo");
    var profile = qs(state.scene, ".tb-match-profile");
    if (photo) photo.classList.remove("is-popout-active");
    if (profile) profile.classList.remove("is-popout-active");
  }

  function cancelApproach() {
    if (state.approachAnim) {
      try {
        state.approachAnim.cancel();
      } catch (e) {
        /* ignore */
      }
      state.approachAnim = null;
    }
    if (state.flyer && state.flyer.parentNode) {
      state.flyer.parentNode.removeChild(state.flyer);
    }
    state.flyer = null;
  }

  function preloadImages() {
    CANDIDATES.forEach(function (candidate) {
      var img = new Image();
      img.decoding = "async";
      img.src = candidate.image;
    });
  }

  function renderChips(container, chips) {
    if (!container) return;
    container.textContent = "";
    (chips || []).forEach(function (label) {
      var span = document.createElement("span");
      span.textContent = label;
      container.appendChild(span);
    });
  }

  function setPhase(phase) {
    state.phase = phase;
    if (state.scene) state.scene.setAttribute("data-tb-orbit-phase", phase);
  }

  function orbitMetrics(scene) {
    var rect = scene.getBoundingClientRect();
    var profile = qs(scene, ".tb-match-profile");
    var photo = qs(scene, ".tb-match-profile__photo");
    var profileRect = profile ? profile.getBoundingClientRect() : null;
    var photoRect = photo ? photo.getBoundingClientRect() : null;
    var mobile = window.innerWidth <= 768;
    var tablet = window.innerWidth <= 1024;
    var nodeSize = mobile ? 38 : tablet ? 44 : 50;

    // Orbit centre = main PROFILE CARD centre (not the photo alone).
    var cx = profileRect
      ? profileRect.left - rect.left + profileRect.width / 2
      : rect.width * 0.28;
    var cy = profileRect
      ? profileRect.top - rect.top + profileRect.height / 2
      : rect.height * 0.42;

    // Outside-card clearance (corner of rectangle + avatar half-size + gap).
    var halfW = profileRect ? profileRect.width / 2 : 110;
    var halfH = profileRect ? profileRect.height / 2 : 160;
    var pad = nodeSize / 2 + (mobile ? 16 : tablet ? 18 : 22);
    var clearR = Math.sqrt(halfW * halfW + halfH * halfH) + pad;

    // TRUE CIRCLE: equal horizontal and vertical radius (never elliptical).
    // Keep just outside the card so the full 360° path stays readable in-hero.
    var r = clearR * (mobile ? 1.01 : tablet ? 1.02 : 1.03);

    // Prefer fitting inside the scene when the scene is large enough to keep
    // avatars outside the card. If not, keep clearR and rely on overflow:visible
    // so the path stays a real circle outside the card (no edge clamping).
    var inset = nodeSize / 2 + 4;
    var maxR = Math.min(
      Math.max(0, cx - inset),
      Math.max(0, rect.width - cx - inset),
      Math.max(0, cy - inset),
      Math.max(0, rect.height - cy - inset)
    );
    if (maxR >= clearR) {
      r = Math.min(r, maxR);
    } else {
      r = clearR;
    }

    // Approach target remains the portrait frame centre.
    var targetX = photoRect
      ? photoRect.left - rect.left + photoRect.width / 2
      : cx;
    var targetY = photoRect
      ? photoRect.top - rect.top + photoRect.height / 2
      : cy - halfH * 0.35;

    return {
      cx: cx,
      cy: cy,
      targetX: targetX,
      targetY: targetY,
      sceneW: rect.width,
      sceneH: rect.height,
      r: r,
      rx: r,
      ry: r,
      nodeSize: nodeSize,
      maxNodes: mobile ? 3 : 4
    };
  }

  function orbitPoint(metrics, angle) {
    var radius = metrics.r != null ? metrics.r : metrics.rx;
    return {
      x: metrics.cx + radius * Math.cos(angle),
      y: metrics.cy + radius * Math.sin(angle)
    };
  }

  function updateOrbitTrail(scene, metrics) {
    var ellipse = qs(scene, ".tb-match-orbit__trail ellipse");
    if (!ellipse || !metrics.sceneW || !metrics.sceneH) return;
    ellipse.setAttribute("cx", ((metrics.cx / metrics.sceneW) * 100).toFixed(2));
    ellipse.setAttribute("cy", ((metrics.cy / metrics.sceneH) * 100).toFixed(2));
    ellipse.setAttribute("rx", ((metrics.rx / metrics.sceneW) * 100).toFixed(2));
    ellipse.setAttribute("ry", ((metrics.ry / metrics.sceneH) * 100).toFixed(2));
  }

  function updateLink(scene, metrics, point, active) {
    var link = qs(scene, "[data-tb-orbit-link]");
    if (!link) return;
    if (!active || !point) {
      link.setAttribute("d", "M50 50 L50 50");
      link.classList.remove("is-active");
      return;
    }
    var rect = scene.getBoundingClientRect();
    // Link from portrait target (centre) to approaching orbit avatar.
    var x1 = ((metrics.targetX || metrics.cx) / rect.width) * 100;
    var y1 = ((metrics.targetY || metrics.cy) / rect.height) * 100;
    var x2 = (point.x / rect.width) * 100;
    var y2 = (point.y / rect.height) * 100;
    link.setAttribute("d", "M" + x1.toFixed(2) + " " + y1.toFixed(2) + " L" + x2.toFixed(2) + " " + y2.toFixed(2));
    link.classList.add("is-active");
  }

  function placeNode(node, metrics, angle, opts) {
    opts = opts || {};
    var point = orbitPoint(metrics, angle);
    var size = metrics.nodeSize * (opts.scale || 1);
    var half = size / 2;
    // Exact circular coordinates — do not clamp (would flatten the circle).
    var x = point.x;
    var y = point.y;
    node.style.width = size + "px";
    node.style.height = size + "px";
    node.style.left = x - half + "px";
    node.style.top = y - half + "px";
    // Keep photographs upright (position-only orbit; no rotate on the node).
    node.style.transform = "none";
    node.style.opacity = opts.opacity == null ? "1" : String(opts.opacity);
    node._orbitAngle = angle;
    node._orbitPoint = { x: x, y: y };
    return node._orbitPoint;
  }

  function rebuildOrbitNodes(scene) {
    var wrap = qs(scene, "[data-tb-orbit-nodes]");
    if (!wrap) return;
    wrap.textContent = "";
    state.nodes = [];

    var metrics = orbitMetrics(scene);
    var orbiting = [];
    var preferredNext = (state.nextIndex == null ? (state.index + 1) % CANDIDATES.length : state.nextIndex);
    CANDIDATES.forEach(function (candidate, index) {
      if (index === state.index) return;
      orbiting.push({ candidate: candidate, index: index });
    });
    if (orbiting.length > metrics.maxNodes) {
      orbiting.sort(function (a, b) {
        var ap = a.index === preferredNext ? 0 : 1;
        var bp = b.index === preferredNext ? 0 : 1;
        if (ap !== bp) return ap - bp;
        return a.index - b.index;
      });
      orbiting = orbiting.slice(0, metrics.maxNodes);
    }

    orbiting.forEach(function (item, i) {
      var node = document.createElement("button");
      node.type = "button";
      node.className = "tb-match-orbit__node";
      node.dataset.index = String(item.index);
      node.dataset.id = item.candidate.id;
      node.setAttribute("aria-label", "Select demo candidate " + item.candidate.name);
      node.tabIndex = -1;

      var img = document.createElement("img");
      img.src = item.candidate.image;
      img.alt = "";
      img.width = metrics.nodeSize;
      img.height = metrics.nodeSize;
      img.loading = "eager";
      img.decoding = "async";
      img.onerror = function () {
        img.onerror = null;
        img.src = "/images/tb-hero-candidate.svg";
      };
      node.appendChild(img);

      node.addEventListener("click", function () {
        goTo(scene, item.index, { manual: true });
      });

      wrap.appendChild(node);
      var angle = state.angle + (i / Math.max(1, orbiting.length)) * Math.PI * 2;
      placeNode(node, metrics, angle);
      state.nodes.push(node);
    });
  }

  function tickOrbit(ts) {
    if (!state.scene || !state.visible || prefersReducedMotion()) {
      state.orbitRaf = null;
      return;
    }

    if (!state.lastOrbitTs) state.lastOrbitTs = ts;
    var dt = Math.min(48, ts - state.lastOrbitTs);
    state.lastOrbitTs = ts;

    var speed = state.orbitSpeed;
    if (state.phase === PHASE.APPROACHING) speed *= 0.28;
    if (
      state.phase === PHASE.SELECTING ||
      state.phase === PHASE.ZOOMING_IN ||
      state.phase === PHASE.ZOOMING_OUT
    ) {
      speed *= 0.55;
    }

    state.angle += (dt / ORBIT_PERIOD_MS) * Math.PI * 2 * speed;
    if (state.angle > Math.PI * 2) state.angle -= Math.PI * 2;

    var metrics = orbitMetrics(state.scene);
    updateOrbitTrail(state.scene, metrics);
    var approachingPoint = null;
    var live = [];
    state.nodes.forEach(function (node) {
      if (node.classList.contains("is-approaching") || node.classList.contains("is-hidden")) return;
      live.push(node);
    });

    live.forEach(function (node, i) {
      var angle = state.angle + (i / Math.max(1, live.length)) * Math.PI * 2;
      var point = placeNode(node, metrics, angle);
      if (node.classList.contains("is-next")) approachingPoint = point;
    });

    updateLink(
      state.scene,
      metrics,
      approachingPoint,
      state.phase === PHASE.APPROACHING || state.phase === PHASE.WAITING_FOR_NEXT
    );

    state.orbitRaf = window.requestAnimationFrame(tickOrbit);
  }

  function startOrbitLoop() {
    if (prefersReducedMotion() || state.orbitRaf) return;
    state.lastOrbitTs = 0;
    state.orbitRaf = window.requestAnimationFrame(tickOrbit);
  }

  function stopOrbitLoop() {
    cancelOrbitRaf();
  }

  function markNextNode(scene, nextIndex) {
    state.nodes.forEach(function (node) {
      var isNext = Number(node.dataset.index) === nextIndex;
      node.classList.toggle("is-next", isNext);
    });
  }

  function showSelectionPulse(scene, metrics) {
    var pulse = qs(scene, "[data-tb-orbit-pulse]");
    if (!pulse) return;
    pulse.hidden = false;
    pulse.classList.remove("is-on");
    pulse.style.left = (metrics.targetX || metrics.cx) + "px";
    pulse.style.top = (metrics.targetY || metrics.cy) + "px";
    void pulse.offsetWidth;
    pulse.classList.add("is-on");
    window.setTimeout(function () {
      pulse.classList.remove("is-on");
      pulse.hidden = true;
    }, 700);
  }

  function setRing(ring, score, animate, fromScore) {
    var progress = qs(ring, ".tb-match-ring__progress");
    var count = qs(ring, "[data-tb-match-count]");
    var target = clampScore(score);
    var startScore = clampScore(fromScore == null ? target : fromScore);

    ring.setAttribute("data-score", String(target));
    ring.classList.add("is-ready");
    ring.classList.toggle("is-complete", !animate);

    if (!progress || !count) return;
    progress.style.strokeDasharray = "100";

    if (!animate || prefersReducedMotion() || startScore === target) {
      progress.style.strokeDashoffset = String(100 - target);
      count.textContent = String(target);
      ring.classList.add("is-complete");
      return;
    }

    ring.classList.remove("is-complete");
    cancelScoreRaf();
    var start = null;

    function frame(ts) {
      if (start === null) start = ts;
      var t = Math.min(1, (ts - start) / SCORE_MS);
      var eased = 1 - Math.pow(1 - t, 3);
      var current = startScore + (target - startScore) * eased;
      count.textContent = String(Math.round(current));
      progress.style.strokeDashoffset = String(100 - current);
      if (t < 1) {
        state.scoreRaf = window.requestAnimationFrame(frame);
      } else {
        state.scoreRaf = null;
        count.textContent = String(target);
        progress.style.strokeDashoffset = String(100 - target);
        ring.classList.add("is-complete");
      }
    }

    state.scoreRaf = window.requestAnimationFrame(frame);
  }

  function applyCandidateFields(scene, candidate, options) {
    options = options || {};
    var img = qs(scene, '[data-tb-match-field="image"]');
    var ring = qs(scene, "[data-tb-match-ring]");
    var result = qs(scene, ".tb-match-result");

    scene.setAttribute("data-active-candidate", candidate.id || "");

    setText(qs(scene, '[data-tb-match-field="name"]'), candidate.name);
    setText(qs(scene, '[data-tb-match-field="role"]'), candidate.role);
    setText(qs(scene, '[data-tb-match-field="skills"]'), candidate.skills);
    setText(qs(scene, '[data-tb-match-field="experience"]'), candidate.experience);
    setText(qs(scene, '[data-tb-match-field="education"]'), candidate.education);
    setText(qs(scene, '[data-tb-match-field="softSkills"]'), candidate.softSkills);
    setText(qs(scene, '[data-tb-match-field="fitLabel"]'), candidate.fitLabel);
    renderChips(qs(scene, '[data-tb-match-field="chips"]'), candidate.chips);

    if (img) {
      img.src = candidate.image;
      img.alt = candidate.alt;
      img.style.setProperty("--tb-photo-pos", candidate.objectPosition || "50% 28%");
      img.style.setProperty("--tb-photo-origin", candidate.zoomOrigin || "50% 30%");
      img.style.transformOrigin = candidate.zoomOrigin || "50% 30%";
      img.onerror = function () {
        img.onerror = null;
        img.src = "/images/tb-hero-candidate.svg";
      };
    }

    if (result) {
      result.setAttribute(
        "aria-label",
        "Illustrative match score " + candidate.score + " percent for " + candidate.name
      );
    }

    if (ring) {
      setRing(ring, candidate.score, !!options.animateScore, options.fromScore);
    }

    updateDots(scene);
  }

  function runZoom(scene, candidate) {
    var img = qs(scene, '[data-tb-match-field="image"]');
    if (!img) {
      enterWaiting(scene);
      return;
    }

    cancelZoom();
    img.style.setProperty("--tb-photo-pos", candidate.objectPosition || "50% 28%");
    img.style.setProperty("--tb-photo-origin", candidate.zoomOrigin || "50% 30%");
    img.style.transformOrigin = candidate.zoomOrigin || "50% 30%";

    var photo = img.closest(".tb-match-profile__photo");
    var profile = img.closest(".tb-match-profile");

    if (prefersReducedMotion()) {
      img.style.transform = "scale(1)";
      enterWaiting(scene);
      return;
    }

    setPhase(PHASE.ZOOMING_IN);
    var total = ZOOM_IN_MS + ZOOM_OUT_MS;
    var peakOffset = ZOOM_IN_MS / total;
    var shadowRest = "0 8px 18px rgba(16, 42, 86, 0.12)";
    var shadowPeak = "0 24px 48px rgba(16, 42, 86, 0.32), 0 8px 18px rgba(37, 99, 235, 0.2)";

    function finishZoom() {
      if (photo) photo.classList.remove("is-popout-active");
      if (profile) profile.classList.remove("is-popout-active");
      img.classList.remove("is-zooming", "is-popout");
      enterWaiting(scene);
    }

    if (typeof img.animate === "function") {
      img.classList.add("is-zooming", "is-popout");
      if (photo) photo.classList.add("is-popout-active");
      if (profile) profile.classList.add("is-popout-active");

      state.zoomAnim = img.animate(
        [
          {
            transform: "perspective(900px) translateZ(0px) scale(1)",
            boxShadow: shadowRest,
            offset: 0,
            easing: "cubic-bezier(0.22, 0.61, 0.36, 1)"
          },
          {
            transform: "perspective(900px) translateZ(42px) scale(" + ZOOM_PEAK + ")",
            boxShadow: shadowPeak,
            offset: peakOffset,
            easing: "cubic-bezier(0.33, 0, 0.2, 1)"
          },
          {
            transform: "perspective(900px) translateZ(0px) scale(1)",
            boxShadow: shadowRest,
            offset: 1
          }
        ],
        { duration: total, fill: "forwards" }
      );

      clearPhaseTimer();
      state.phaseTimer = window.setTimeout(function () {
        if (state.phase === PHASE.ZOOMING_IN) setPhase(PHASE.ZOOMING_OUT);
      }, ZOOM_IN_MS);

      state.zoomAnim.finished.then(finishZoom).catch(function () {
        /* cancelled */
      });
      return;
    }

    img.classList.add("is-zooming");
    clearPhaseTimer();
    state.phaseTimer = window.setTimeout(finishZoom, total);
  }

  function enterWaiting(scene) {
    setPhase(PHASE.WAITING_FOR_NEXT);
    state.busy = false;
    state.orbitSpeed = 1;
    clearHold();
    if (prefersReducedMotion() || CANDIDATES.length < 2 || !state.visible) return;
    state.nextIndex = (state.index + 1) % CANDIDATES.length;
    markNextNode(scene, state.nextIndex);
    state.holdTimer = window.setTimeout(function () {
      goTo(scene, state.nextIndex, { auto: true });
    }, HOLD_MS);
  }

  function approachAndSelect(scene, nextIndex) {
    var previous = CANDIDATES[state.index];
    var next = CANDIDATES[nextIndex];
    var metrics = orbitMetrics(scene);
    var node = state.nodes.find(function (n) {
      return Number(n.dataset.index) === nextIndex;
    });

    setPhase(PHASE.APPROACHING);
    state.busy = true;
    state.orbitSpeed = 0.28;
    markNextNode(scene, nextIndex);
    cancelZoom();

    var photo = qs(scene, ".tb-match-profile__photo");
    var mainImg = qs(scene, '[data-tb-match-field="image"]');
    scene.classList.add("is-selecting");

    function commitSelection() {
      setPhase(PHASE.SELECTING);
      state.index = nextIndex;
      state.nextIndex = (nextIndex + 1) % CANDIDATES.length;

      if (mainImg) {
        mainImg.style.opacity = "0";
      }

      window.setTimeout(function () {
        applyCandidateFields(scene, next, {
          animateScore: true,
          fromScore: previous ? previous.score : next.score
        });
        rebuildOrbitNodes(scene);
        markNextNode(scene, state.nextIndex);
        showSelectionPulse(scene, orbitMetrics(scene));

        if (mainImg) {
          mainImg.style.opacity = "1";
          scene.classList.add("is-revealing");
        }

        window.setTimeout(function () {
          scene.classList.remove("is-selecting", "is-revealing", "is-transitioning");
          setPhase(PHASE.ACTIVE);
          runZoom(scene, next);
        }, FADE_MS);
      }, 80);
    }

    if (!node || prefersReducedMotion() || typeof node.animate !== "function") {
      scene.classList.add("is-transitioning");
      if (mainImg) mainImg.style.opacity = "0";
      window.setTimeout(commitSelection, FADE_MS);
      return;
    }

    node.classList.add("is-approaching", "is-next");
    var startLeft = parseFloat(node.style.left) || 0;
    var startTop = parseFloat(node.style.top) || 0;
    var startSize = parseFloat(node.style.width) || metrics.nodeSize;
    var targetSize = Math.min(96, Math.max(76, metrics.nodeSize * 1.75));
    var targetLeft = (metrics.targetX || metrics.cx) - targetSize / 2;
    var targetTop = (metrics.targetY || metrics.cy) - targetSize / 2;

    var flyer = document.createElement("div");
    flyer.className = "tb-match-orbit__flyer";
    flyer.style.left = startLeft + "px";
    flyer.style.top = startTop + "px";
    flyer.style.width = startSize + "px";
    flyer.style.height = startSize + "px";
    var flyerImg = document.createElement("img");
    flyerImg.src = next.image;
    flyerImg.alt = "";
    flyerImg.width = targetSize;
    flyerImg.height = targetSize;
    flyer.appendChild(flyerImg);
    scene.appendChild(flyer);
    state.flyer = flyer;

    updateLink(scene, metrics, { x: startLeft + startSize / 2, y: startTop + startSize / 2 }, true);

    if (mainImg) {
      mainImg.style.transition = "opacity " + FADE_MS + "ms ease";
      mainImg.style.opacity = "0.18";
    }

    if (typeof flyer.animate !== "function") {
      cancelApproach();
      scene.classList.add("is-transitioning");
      commitSelection();
      return;
    }

    state.approachAnim = flyer.animate(
      [
        {
          left: startLeft + "px",
          top: startTop + "px",
          width: startSize + "px",
          height: startSize + "px",
          offset: 0,
          easing: "cubic-bezier(0.22, 0.61, 0.36, 1)"
        },
        {
          left: targetLeft + "px",
          top: targetTop + "px",
          width: targetSize + "px",
          height: targetSize + "px",
          offset: 1
        }
      ],
      { duration: APPROACH_MS, fill: "forwards" }
    );

    var linkSync = window.setInterval(function () {
      if (!state.flyer) return;
      var r = state.flyer.getBoundingClientRect();
      var s = scene.getBoundingClientRect();
      updateLink(
        scene,
        metrics,
        { x: r.left - s.left + r.width / 2, y: r.top - s.top + r.height / 2 },
        true
      );
    }, 40);

    state.approachAnim.finished
      .then(function () {
        window.clearInterval(linkSync);
        node.classList.add("is-hidden");
        cancelApproach();
        commitSelection();
      })
      .catch(function () {
        window.clearInterval(linkSync);
      });
  }

  function buildDots(scene) {
    var wrap = qs(scene, "[data-tb-match-dots]");
    if (!wrap) return;
    wrap.textContent = "";
    CANDIDATES.forEach(function (candidate, index) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tb-match-dot";
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-label", "Show demo candidate " + candidate.name);
      btn.setAttribute("aria-selected", index === state.index ? "true" : "false");
      btn.dataset.index = String(index);
      btn.addEventListener("click", function () {
        goTo(scene, index, { manual: true });
      });
      wrap.appendChild(btn);
    });
  }

  function updateDots(scene) {
    var wrap = qs(scene, "[data-tb-match-dots]");
    if (!wrap) return;
    wrap.querySelectorAll(".tb-match-dot").forEach(function (btn, index) {
      var active = index === state.index;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", active ? "true" : "false");
    });
  }

  function goTo(scene, nextIndex, options) {
    options = options || {};
    nextIndex = ((nextIndex % CANDIDATES.length) + CANDIDATES.length) % CANDIDATES.length;

    if (state.busy && !options.force) return;
    if (nextIndex === state.index && !options.force) {
      if (options.manual) enterWaiting(scene);
      return;
    }

    clearHold();
    clearPhaseTimer();
    cancelApproach();
    cancelZoom();

    if (prefersReducedMotion() || options.instant) {
      var prev = CANDIDATES[state.index];
      state.index = nextIndex;
      applyCandidateFields(scene, CANDIDATES[nextIndex], {
        animateScore: !prefersReducedMotion(),
        fromScore: prev ? prev.score : CANDIDATES[nextIndex].score
      });
      rebuildOrbitNodes(scene);
      setPhase(PHASE.ACTIVE);
      state.busy = false;
      enterWaiting(scene);
      return;
    }

    approachAndSelect(scene, nextIndex);
  }

  function start(scene) {
    if (state.started) return;
    state.started = true;
    setPhase(PHASE.ACTIVE);
    applyCandidateFields(scene, CANDIDATES[state.index], {
      animateScore: !prefersReducedMotion(),
      fromScore: 0
    });
    rebuildOrbitNodes(scene);
    startOrbitLoop();
    if (prefersReducedMotion()) {
      enterWaiting(scene);
      return;
    }
    runZoom(scene, CANDIDATES[state.index]);
  }

  function init() {
    var scene = document.querySelector(SCENE_SEL);
    if (!scene || !CANDIDATES.length) return;
    state.scene = scene;

    preloadImages();
    buildDots(scene);
    applyCandidateFields(scene, CANDIDATES[0], { animateScore: false });
    rebuildOrbitNodes(scene);
    setPhase(PHASE.ACTIVE);

    if (prefersReducedMotion()) {
      setRing(qs(scene, "[data-tb-match-ring]"), CANDIDATES[0].score, false);
      return;
    }

    function onVisible(isVisible) {
      state.visible = isVisible;
      if (isVisible) {
        start(scene);
        if (state.started && !state.busy && state.phase === PHASE.WAITING_FOR_NEXT) {
          enterWaiting(scene);
        }
        startOrbitLoop();
      } else {
        clearHold();
        cancelScoreRaf();
        stopOrbitLoop();
      }
    }

    if (!("IntersectionObserver" in window)) {
      onVisible(true);
    } else {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            onVisible(entry.isIntersecting);
          });
        },
        { threshold: [0.2], rootMargin: "0px 0px -6% 0px" }
      );
      observer.observe(scene);

      var rect = scene.getBoundingClientRect();
      if (rect.top < window.innerHeight * 0.92 && rect.bottom > 0) {
        onVisible(true);
      }
    }

    document.addEventListener(
      "visibilitychange",
      function () {
        if (document.hidden) {
          clearHold();
          cancelScoreRaf();
          stopOrbitLoop();
        } else if (state.started && state.visible) {
          startOrbitLoop();
          if (!state.busy && state.phase === PHASE.WAITING_FOR_NEXT) {
            enterWaiting(scene);
          }
        }
      },
      false
    );

    window.addEventListener(
      "resize",
      function () {
        if (!state.scene) return;
        rebuildOrbitNodes(state.scene);
      },
      { passive: true }
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
