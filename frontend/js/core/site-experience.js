(() => {
  const script = document.currentScript;
  if (!script || document.body.dataset.siteExperience === "ready") return;
  document.body.dataset.siteExperience = "ready";

  const isFilePreview = window.location.protocol === "file:";
  const rootUrl = isFilePreview
    ? new URL("../", script.src)
    : new URL("/", window.location.origin);

  const resolvePath = (path) => {
    if (!path) return rootUrl.href;
    if (/^https?:\/\//i.test(path) || path.startsWith("/")) return path;
    if (path === "index.html") return "/";
    if (path === "404.html") return "/404/";
    if (isFilePreview) return new URL(path, rootUrl).href;
    if (path.startsWith("pages/")) return `/${path}`;
    return `/${path.replace(/^\.\//, "")}`;
  };

  if (/{%[\s\S]*?%}|{{[\s\S]*?}}/.test(document.body.innerHTML)) {
    const pagePath = window.location.pathname.startsWith(rootUrl.pathname)
      ? window.location.pathname.slice(rootUrl.pathname.length)
      : "";
    const previewUrl = new URL(`site/${pagePath}`, rootUrl);
    window.location.replace(previewUrl.href);
    return;
  }

  if (document.body.hasAttribute("data-no-page-directory")) return;

  const groups = [
    {
      title: "Explore",
      links: [
        ["Home", "/"],
        ["For employers", "/employer/"],
        ["For job seekers", "/jobseaker/"],
        ["Job seeker information", "/employee/"],
        ["Browse jobs", "/jobs/"],
        ["Browse companies", "/companies/"],
        ["Search jobs", "/job-search/"],
        ["Job categories", "/categories/"],
        ["Job details", "/job-detail/"],
        ["Plans & pricing", "/pricing/"]
      ]
    },
    {
      title: "Job seekers",
      links: [
        ["Create an account", "/signup/job-seeker/"],
        ["Choose an account type", "/signup/"],
        ["My profile", "/profile/"],
        ["Edit profile", "/edit-profile/"],
        ["Resume management", "/resume-management/"],
        ["Saved jobs", "/saved-jobs/"],
        ["Applications", "/applied-jobs/"],
        ["Apply for a job", "/application-form/"],
        ["Application confirmation", "/application-success/"],
        ["Interviews", "/interviews/"]
      ]
    },
    {
      title: "Employers",
      links: [
        ["Company sign up", "/signup/employer/"],
        ["Employer profile", "/employer-profile/"],
        ["Company details", "/company-details/"],
        ["Employer approval", "/employer/pending/"],
        ["Post a job", "/posting-job/"],
        ["Manage jobs", "/manage-jobs/"],
        ["Manage applications", "/manage-applications/"],
        ["Candidate details", "/candidate-details/"],
        ["Admin dashboard", "/admin-dashboard/"]
      ]
    },
    {
      title: "Dashboards",
      links: [
        ["Job seeker dashboard", "/pages/dashboard/jdashboard.html"],
        ["Employer dashboard", "/pages/dashboard/cdashboard.html"],
        ["Employer dashboard (legacy)", "/pages/dashboard/dindex.html"],
        ["Customize dashboard", "/pages/dashboard/customize.html"],
        ["Organize dashboard cards", "/pages/dashboard/organize-cards.html"],
        ["Notifications", "/notifications/"]
      ]
    },
    {
      title: "Account",
      links: [
        ["Sign in", "/login/"],
        ["Reset password", "/forgot-password/"],
        ["Password reset", "/password-reset/"],
        ["Confirm password reset", "/password-reset-confirm/"],
        ["Password reset complete", "/password-reset/complete/"],
        ["Account setup", "/pages/socialaccount/signup.html"]
      ]
    },
    {
      title: "About & support",
      links: [
        ["About TalentBridge", "/about/"],
        ["Help center", "/help/"],
        ["FAQs", "/faq/"],
        ["Contact", "/contact/"]
      ]
    },
    {
      title: "Company",
      links: [
        ["Customer stories", "/customer-stories/"],
        ["Blog & insights", "/blog/"],
        ["Careers", "/careers/"]
      ]
    },
    {
      title: "Trust & support",
      links: [
        ["Trust center", "/trust-center/"],
        ["AI audit center", "/ai-audit-center/"],
        ["Platform status", "/platform-status/"],
        ["Cookie preferences", "/cookie-preferences/"]
      ]
    },
    {
      title: "Policies & errors",
      links: [
        ["Privacy policy", "/privacy/"],
        ["Terms", "/terms/"],
        ["Page not found", "/404/"],
        ["Site error page", "/404/"]
      ]
    }
  ];

  const directory = document.createElement("details");
  directory.className = "tb-page-directory";

  const toggle = document.createElement("summary");
  toggle.innerHTML = '<span class="tb-page-directory__icon" aria-hidden="true">☷</span><span>Page directory</span>';

  const panel = document.createElement("div");
  panel.className = "tb-page-directory__panel";
  const heading = document.createElement("div");
  heading.className = "tb-page-directory__heading";
  const title = document.createElement("h2");
  title.textContent = "Explore TalentBridge AI";
  const description = document.createElement("p");
  description.textContent = "Pages grouped by task, so every section is easy to find.";
  heading.append(title, description);

  const groupContainer = document.createElement("div");
  groupContainer.className = "tb-page-directory__groups";
  groups.forEach(group => {
    const section = document.createElement("nav");
    section.className = "tb-page-directory__group";
    section.setAttribute("aria-label", group.title);
    const groupTitle = document.createElement("h3");
    groupTitle.textContent = group.title;
    const list = document.createElement("ul");

    group.links.forEach(([label, path]) => {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = resolvePath(path);
      link.textContent = label;
      try {
        if (new URL(link.href, window.location.origin).pathname === window.location.pathname) {
          link.setAttribute("aria-current", "page");
        }
      } catch (_error) {
        /* ignore invalid comparison */
      }
      item.append(link);
      list.append(item);
    });

    section.append(groupTitle, list);
    groupContainer.append(section);
  });

  panel.append(heading, groupContainer);
  directory.append(toggle, panel);
  document.body.append(directory);
})();
