(function () {
  "use strict";

  var isPreviewPage = document.body && (
    document.body.getAttribute("data-live-preview") === "true" ||
    !!document.getElementById("server-status") ||
    !!document.getElementById("current-errors") ||
    !!document.querySelector(".preview-shell")
  );

  if (!isPreviewPage) {
    return;
  }

  var endpoint = "/__dev__/state/";
  var previous = null;
  var clientErrors = [];
  var networkUnavailable = false;
  var consecutiveFailures = 0;
  var pollTimeout = 8000;
  var banner = document.createElement("div");
  banner.setAttribute("role", "status");
  banner.style.cssText = "position:fixed;z-index:2147483647;right:12px;bottom:12px;max-width:min(440px,calc(100vw - 24px));padding:10px 14px;border-radius:8px;background:#163653;color:#fff;font:13px/1.5 Segoe UI,sans-serif;box-shadow:0 3px 14px #0003;display:none";
  document.addEventListener("DOMContentLoaded", function () {
    if (!document.getElementById("server-status")) document.body.appendChild(banner);
  });

  function showBanner(message, isError) {
    var background = isError ? "#9e2637" : "#163653";
    if (banner.textContent === message && banner.style.background === background && banner.style.display === "block") return;
    banner.textContent = message;
    banner.style.background = background;
    banner.style.display = "block";
  }

  function updateField(id, value, state) {
    var field = document.getElementById(id);
    if (!field) return;
    if (field.textContent !== value) field.textContent = value;
    if (state && field.getAttribute("data-state") !== state) field.setAttribute("data-state", state);
  }

  function refreshStylesheets() {
    Array.prototype.forEach.call(document.querySelectorAll('link[rel="stylesheet"]'), function (link) {
      var url;
      try {
        url = new URL(link.href, window.location.href);
      } catch (error) {
        return;
      }
      if (url.origin !== window.location.origin) return;
      url.searchParams.set("_live", Date.now().toString());
      var replacement = link.cloneNode();
      replacement.href = url.href;
      replacement.onload = function () { link.remove(); };
      replacement.onerror = function () {
        replacement.remove();
        var message = "A stylesheet failed to load. Check the Django terminal for errors.";
        clientErrors = [{ level: "error", message: message }];
        updateField("frontend-status", "Stylesheet failed to load", "error");
        showBanner(message, true);
      };
      link.after(replacement);
    });
  }

  function showErrors(errors) {
    var list = document.getElementById("current-errors");
    var panel = document.querySelector(".error-card");
    if (!list) return;
    var signature = errors.map(function (error) {
      return (error.level || "") + "\n" + error.message;
    }).join("\n");
    if (list.getAttribute("data-error-signature") === signature) return;
    list.setAttribute("data-error-signature", signature);
    list.textContent = "";
    if (!errors.length) {
      var clear = document.createElement("li");
      clear.textContent = "No current Django system-check or frontend source errors.";
      list.appendChild(clear);
      if (panel) panel.classList.remove("has-errors");
      return;
    }
    if (panel) panel.classList.add("has-errors");
    errors.forEach(function (error) {
      var item = document.createElement("li");
      item.textContent = (error.level ? error.level.toUpperCase() + ": " : "") + error.message;
      list.appendChild(item);
    });
  }

  function validateScripts(paths) {
    return Promise.all(paths.map(function (path) {
      var sourceUrl = "/" + path.split("/").map(encodeURIComponent).join("/");
      return fetch(sourceUrl, { cache: "no-store" })
        .then(function (response) {
          if (!response.ok) throw new Error("HTTP " + response.status + " for " + sourceUrl);
          return response.text();
        })
        .then(function (source) {
          new Function(source);
          return null;
        })
        .catch(function (error) {
          return "JavaScript check failed for " + sourceUrl + ": " + error.message;
        });
    })).then(function (results) {
      return results.filter(Boolean);
    });
  }

  function renderState(state) {
    var serverOk = state.server.status === "ok";
    var frontendOk = state.frontend.status === "ok";
    updateField("server-status", serverOk ? "Running" : "Needs attention", serverOk ? "ok" : "error");
    updateField("website-url", state.server.url, "ok");
    var website = document.getElementById("website-url");
    if (website) website.href = state.server.url;
    updateField("development-mode", state.server.mode);
    updateField("last-reload", new Date(state.server.started_at).toLocaleString());
    updateField("backend-status", serverOk ? "Running · PID " + state.server.pid : "Errors detected", serverOk ? "ok" : "error");
    updateField(
      "frontend-status",
      frontendOk
        ? state.frontend.counts.styles + " CSS · " + state.frontend.counts.scripts + " JS files"
        : "Needs attention",
      frontendOk ? "ok" : "error"
    );
    showErrors((state.errors || []).concat(clientErrors));
  }

  function poll() {
    var controller = typeof AbortController === "function" ? new AbortController() : null;
    var timeout = window.setTimeout(function () {
      if (controller) controller.abort();
    }, pollTimeout);
    var options = { cache: "no-store", headers: { "Accept": "application/json" } };
    if (controller) options.signal = controller.signal;
    fetch(endpoint, options)
      .then(function (response) {
        if (!response.ok) throw new Error("Status endpoint returned HTTP " + response.status);
        return response.json();
      })
      .then(function (state) {
        consecutiveFailures = 0;
        if (networkUnavailable) {
          networkUnavailable = false;
          banner.style.display = "none";
        }
        if (previous) {
          if (state.server.pid !== previous.server.pid) {
            showBanner("Django restarted successfully. Refreshing this page…", false);
            window.location.reload();
            return;
          }
          if (state.fingerprints.backend !== previous.fingerprints.backend) {
            showBanner("Backend code changed. Refreshing this page…", false);
            window.location.reload();
            return;
          }
          if (state.fingerprints.templates !== previous.fingerprints.templates) {
            showBanner("Template changed. Refreshing the page…", false);
            window.location.reload();
            return;
          }
          if (state.fingerprints.styles !== previous.fingerprints.styles) {
            refreshStylesheets();
            showBanner("Stylesheet updated.", false);
          }
          if (state.fingerprints.assets !== previous.fingerprints.assets) {
            showBanner("Image or media asset changed. Refreshing the page…", false);
            window.location.reload();
            return;
          }
          if (state.fingerprints.scripts !== previous.fingerprints.scripts) {
            previous = state;
            return validateScripts(state.frontend.scripts).then(function (errors) {
              if (errors.length) {
                clientErrors = errors.map(function (message) {
                  return { level: "error", message: message };
                });
                updateField("frontend-status", "JavaScript syntax errors detected", "error");
                showErrors((state.errors || []).concat(clientErrors));
                showBanner("JavaScript syntax/load error. The current page was kept; fix the script and save again.", true);
                return;
              }
              showBanner("JavaScript updated. Refreshing the page…", false);
              window.location.reload();
            });
          }
        }
        previous = state;
        renderState(state);
      })
      .catch(function (error) {
        consecutiveFailures += 1;
        if (!networkUnavailable) {
          networkUnavailable = true;
          showBanner("Django health check unavailable: " + error.message + ". Retrying automatically; other server failures remain visible in the Django terminal.", true);
          updateField("server-status", "Unavailable", "error");
          updateField("backend-status", "Unavailable", "error");
        }
      })
      .finally(function () {
        window.clearTimeout(timeout);
        var retryDelay = networkUnavailable
          ? Math.min(5000 * Math.pow(2, Math.min(consecutiveFailures - 1, 2)), 15000)
          : 5000;
        window.setTimeout(poll, retryDelay);
      });
  }

  poll();
}());
