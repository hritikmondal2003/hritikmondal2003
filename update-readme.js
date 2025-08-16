const fetch = require("node-fetch");
const fs = require("fs");

const username = "hritikmondal2003"; // your GitHub username
const readmePath = "./README.md";

async function updateReadme() {
  const res = await fetch(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated`);
  const repos = await res.json();

  const publicRepos = repos.filter(repo => !repo.private);

  const repoCount = publicRepos.length;
  const repoList = publicRepos
    .map(repo => `- [${repo.name}](${repo.html_url}) – ${repo.description || "No description"}`)
    .join("\n");

  let readmeContent = fs.readFileSync(readmePath, "utf8");

  readmeContent = readmeContent.replace(
    /(<!-- REPO_COUNT:START -->)(.*?)(<!-- REPO_COUNT:END -->)/,
    `$1${repoCount}$3`
  );

  readmeContent = readmeContent.replace(
    /(<!-- REPO_LIST:START -->)(.*?)(<!-- REPO_LIST:END -->)/s,
    `$1\n${repoList}\n$3`
  );

  fs.writeFileSync(readmePath, readmeContent);
}

updateReadme();
