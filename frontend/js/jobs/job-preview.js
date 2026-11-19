(() => {
  const sampleJobs = {
    "frontend-developer": {
      title: "Frontend Developer", company: "Google", location: "Remote", category: "Technology",
      skills: ["JavaScript", "React", "CSS"],
      responsibilities: ["Build accessible, responsive product interfaces.", "Collaborate with design and API teams to deliver features.", "Review code and improve front-end quality."]
    },
    "ui-ux-designer": {
      title: "UI/UX Designer", company: "Northstar Studio", location: "Hybrid · Bhopal", category: "Design & creative",
      skills: ["Figma", "UI/UX", "Design research"],
      responsibilities: ["Research user needs and map key journeys.", "Create prototypes and communicate design decisions.", "Work with engineers to refine shipped experiences."]
    },
    "software-engineer-intern": {
      title: "Software Engineer Intern", company: "Orbit Systems", location: "Remote", category: "Technology · Early career",
      skills: ["Python", "APIs", "Git"],
      responsibilities: ["Contribute to scoped product engineering tasks.", "Write and test code with guidance from the team.", "Document learning and share progress in reviews."]
    },
    "junior-web-developer": {
      title: "Junior Web Developer", company: "Nova Digital", location: "On-site · Bhopal", category: "Technology · Early career",
      skills: ["HTML", "CSS", "JavaScript"],
      responsibilities: ["Implement page layouts from design references.", "Test pages across common screen sizes.", "Work with teammates to fix bugs and maintain components."]
    },
    "product-designer": {
      title: "Product Designer", company: "Pixel & Co.", location: "On-site · Indore", category: "Product & design",
      skills: ["Product design", "Research", "Figma"],
      responsibilities: ["Turn user needs into clear product workflows.", "Create prototypes and maintain reusable design patterns.", "Partner with product and engineering during delivery."]
    },
    "business-analyst": {
      title: "Business Analyst", company: "ClearPath Consulting", location: "Hybrid · Mumbai", category: "Business & finance",
      skills: ["Analysis", "Reporting", "Communication"],
      responsibilities: ["Gather requirements from project stakeholders.", "Analyze information and prepare concise reports.", "Document processes and validate proposed improvements."]
    },
    "growth-marketing-specialist": {
      title: "Growth Marketing Specialist", company: "BrightPath Digital", location: "Remote", category: "Sales & marketing",
      skills: ["Marketing", "Analytics", "Content"],
      responsibilities: ["Plan campaigns around audience and business goals.", "Review performance data and summarize learning.", "Coordinate useful content across marketing channels."]
    },
    "people-operations-coordinator": {
      title: "People Operations Coordinator", company: "PeopleFirst", location: "Hybrid · Pune", category: "People & administration",
      skills: ["Coordination", "Communication", "HR operations"],
      responsibilities: ["Coordinate onboarding and employee support tasks.", "Maintain organized people-process documentation.", "Help teams communicate important process updates."]
    },
    "mechanical-design-engineer": {
      title: "Mechanical Design Engineer", company: "Meridian Engineering", location: "On-site · Indore", category: "Engineering",
      skills: ["CAD", "Design", "Manufacturing"],
      responsibilities: ["Prepare and review practical engineering drawings.", "Support design reviews against requirements.", "Coordinate revisions with manufacturing partners."]
    }
  };
  const requestedRole = new URLSearchParams(window.location.search).get("role");
  const role = requestedRole || "frontend-developer";
  const job = sampleJobs[role];

  const detailTitle = document.querySelector("[data-job-detail-title]");
  const detailMessage = document.querySelector("[data-job-detail-message]");
  if (!job) {
    if (detailTitle) detailTitle.textContent = "Role preview unavailable";
    if (detailMessage) detailMessage.textContent = "Choose a role from Browse Jobs to see its details. Live vacancy data is not connected yet.";
    return;
  }

  if (detailTitle && detailMessage) {
    detailTitle.textContent = job.title;
    detailMessage.textContent = `Illustrative ${job.category.toLowerCase()} preview for TalentBridge — not an active opening.`;
    const company = document.querySelector("[data-job-detail-company]");
    const location = document.querySelector("[data-job-detail-location]");
    const category = document.querySelector("[data-job-detail-category]");
    const responsibilities = document.querySelector("[data-job-detail-responsibilities]");
    const skills = document.querySelector("[data-job-detail-skills]");
    if (company) company.textContent = job.company;
    if (location) location.textContent = job.location;
    if (category) category.textContent = job.category;
    if (responsibilities) {
      responsibilities.replaceChildren(...job.responsibilities.map(text => {
        const item = document.createElement("li");
        item.textContent = text;
        return item;
      }));
    }
    if (skills) {
      skills.replaceChildren(...job.skills.map(text => {
        const skill = document.createElement("span");
        skill.className = "tb-pill";
        skill.textContent = text;
        return skill;
      }));
    }
  }

  const applicationContext = document.querySelector("[data-application-context]");
  if (applicationContext) {
    applicationContext.textContent = `Previewing an application for ${job.title} at ${job.company}. This form does not send or save an application.`;
    const detailLink = document.querySelector("[data-review-job-details]");
    if (detailLink) detailLink.href = `job-detail.html?role=${encodeURIComponent(role)}`;
  }

  const applyAction = document.querySelector("[data-sample-apply]");
  const applyLink = applyAction?.querySelector("a");
  if (applyAction && applyLink) {
    applyLink.href = `application-form.html?role=${encodeURIComponent(role)}`;
    applyAction.hidden = false;
  }
})();
