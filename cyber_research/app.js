const resources = [
  {
    title: "Cybersecurity Framework (CSF) 2.0",
    publisher: "NIST",
    category: "Frameworks",
    description: "A risk-based framework for understanding, assessing, prioritizing, and communicating cybersecurity work.",
    tags: "risk governance identify protect detect respond recover",
    url: "https://www.nist.gov/cyberframework",
    action: "Explore the framework"
  },
  {
    title: "CISA Known Exploited Vulnerabilities Catalog",
    publisher: "CISA",
    category: "Vulnerabilities",
    description: "A catalog of vulnerabilities known to be exploited in the wild, useful for prioritizing remediation.",
    tags: "kev patching prioritization cve vulnerability remediation",
    url: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
    action: "View the catalog"
  },
  {
    title: "OWASP Top 10",
    publisher: "OWASP",
    category: "Learning",
    description: "An awareness document describing prominent web application security risks and defensive mitigations.",
    tags: "web application security secure coding learning",
    url: "https://owasp.org/www-project-top-ten/",
    action: "Read the guide"
  },
  {
    title: "MITRE ATT&CK",
    publisher: "MITRE",
    category: "Threats",
    description: "A knowledge base of observed adversary tactics and techniques to inform defensive threat modeling.",
    tags: "threat intelligence tactics techniques detection analysis",
    url: "https://attack.mitre.org/",
    action: "Browse the knowledge base"
  },
  {
    title: "National Vulnerability Database",
    publisher: "NIST",
    category: "Vulnerabilities",
    description: "Search vulnerability records and supporting security data to help understand and manage exposure.",
    tags: "nvd cve vulnerability cpe patching risk",
    url: "https://nvd.nist.gov/",
    action: "Search vulnerability data"
  },
  {
    title: "CISA Secure by Design",
    publisher: "CISA",
    category: "Learning",
    description: "Guidance encouraging technology providers to build products that are secure by default.",
    tags: "secure design default product development learning",
    url: "https://www.cisa.gov/securebydesign",
    action: "Read the guidance"
  },
  {
    title: "NIST Incident Response Guidance",
    publisher: "NIST",
    category: "Frameworks",
    description: "NIST resources for preparing for, detecting, responding to, and recovering from cybersecurity incidents.",
    tags: "incident response recovery preparation detection",
    url: "https://csrc.nist.gov/projects/incident-response",
    action: "Explore response resources"
  },
  {
    title: "CISA Cybersecurity Advisories",
    publisher: "CISA",
    category: "Threats",
    description: "Official alerts and advisories with defensive information for organizations and security practitioners.",
    tags: "threat intelligence alerts advisories defense",
    url: "https://www.cisa.gov/news-events/cybersecurity-advisories",
    action: "Browse advisories"
  },
  {
    title: "OWASP Web Security Testing Guide",
    publisher: "OWASP",
    category: "Learning",
    description: "A structured guide for authorized web application security testing and communicating findings responsibly.",
    tags: "web application testing authorized assessment learning",
    url: "https://owasp.org/www-project-web-security-testing-guide/",
    action: "Open the testing guide"
  }
];

const resourceGrid = document.querySelector("#resource-grid");
const searchInput = document.querySelector("#search-input");
const resultCount = document.querySelector("#result-count");
const categoryFilters = document.querySelector("#category-filters");
let selectedCategory = "All";

function renderResources() {
  const query = searchInput.value.trim().toLowerCase();
  const matches = resources.filter((resource) => {
    const searchable = `${resource.title} ${resource.publisher} ${resource.category} ${resource.description} ${resource.tags}`.toLowerCase();
    return (selectedCategory === "All" || resource.category === selectedCategory) && searchable.includes(query);
  });

  resourceGrid.replaceChildren();
  for (const resource of matches) {
    const card = document.createElement("article");
    card.className = "resource-card";
    const meta = document.createElement("div");
    meta.className = "card-meta";
    const category = document.createElement("span");
    category.className = "category-label";
    category.textContent = resource.category;
    const publisher = document.createElement("span");
    publisher.className = "publisher";
    publisher.textContent = resource.publisher;
    meta.append(category, publisher);

    const title = document.createElement("h3");
    title.textContent = resource.title;
    const description = document.createElement("p");
    description.textContent = resource.description;
    const link = document.createElement("a");
    link.className = "card-link";
    link.href = resource.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = `${resource.action} ↗`;
    card.append(meta, title, description, link);
    resourceGrid.append(card);
  }

  resultCount.textContent = `${matches.length} ${matches.length === 1 ? "resource" : "resources"}`;
  document.querySelector("#empty-search").classList.toggle("hidden", matches.length !== 0);
}

searchInput.addEventListener("input", renderResources);
categoryFilters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-category]");
  if (!button) return;
  selectedCategory = button.dataset.category;
  categoryFilters.querySelector(".selected").classList.remove("selected");
  button.classList.add("selected");
  renderResources();
});

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector(".nav-item.active").classList.remove("active");
    button.classList.add("active");
    document.querySelector(".view.active").classList.remove("active");
    document.querySelector(`#${button.dataset.view}-view`).classList.add("active");
    document.querySelector("#current-section").textContent = button.textContent.trim().replace(/\s+\d+$/, "");
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
});

function readItems(key) {
  try {
    const value = JSON.parse(localStorage.getItem(key) || "[]");
    return Array.isArray(value) ? value.filter((item) => item && typeof item.text === "string") : [];
  } catch {
    return [];
  }
}

function saveItems(key, items) {
  try {
    localStorage.setItem(key, JSON.stringify(items));
    return true;
  } catch {
    window.alert("Could not save locally. Check this browser's storage settings.");
    return false;
  }
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(timestamp));
}

function renderList(key, listId, emptyId, countId) {
  const items = readItems(key);
  const list = document.querySelector(listId);
  list.replaceChildren();
  items.forEach((item, index) => {
    const entry = document.createElement("article");
    entry.className = "entry-card";
    const header = document.createElement("div");
    header.className = "entry-top";
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = formatDate(item.createdAt);
    const remove = document.createElement("button");
    remove.className = "delete-button";
    remove.type = "button";
    remove.textContent = "Delete";
    remove.setAttribute("aria-label", `Delete entry from ${date.textContent}`);
    remove.addEventListener("click", () => {
      const current = readItems(key);
      current.splice(index, 1);
      if (saveItems(key, current)) renderList(key, listId, emptyId, countId);
    });
    const text = document.createElement("p");
    text.className = "entry-text";
    text.textContent = item.text;
    header.append(date, remove);
    entry.append(header, text);
    list.append(entry);
  });
  document.querySelector(emptyId).classList.toggle("hidden", items.length !== 0);
  document.querySelector(countId).textContent = items.length;
}

function connectComposer(formId, inputId, key, listId, emptyId, countId) {
  document.querySelector(formId).addEventListener("submit", (event) => {
    event.preventDefault();
    const input = document.querySelector(inputId);
    const text = input.value.trim();
    if (!text) {
      input.focus();
      return;
    }
    const items = readItems(key);
    items.unshift({ text, createdAt: new Date().toISOString() });
    if (saveItems(key, items)) {
      input.value = "";
      renderList(key, listId, emptyId, countId);
    }
  });
}

connectComposer("#note-form", "#note-input", "signalDeskNotes", "#notes-list", "#empty-notes", "#note-count");
connectComposer("#post-form", "#post-input", "signalDeskPosts", "#posts-list", "#empty-posts", "#post-count");
renderResources();
renderList("signalDeskNotes", "#notes-list", "#empty-notes", "#note-count");
renderList("signalDeskPosts", "#posts-list", "#empty-posts", "#post-count");
