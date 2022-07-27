---
layout: repo-desc
title:  "Github Actions SEO monitoring and automation"
author: "Adam Miszczak"
categories: [repo-description]
technologies: [javascript, typescript, node.js, cron, github actions, mysql, slack]
---

### Background
At my current occupation as SEO Specialist my team have a need for constant monitoring for some checks and automate every important process which cost us valuable time. So that is the reason for developing our so called "Seo Monitor". **I can't show you the code or talk about detailed specification, but I can tell you a bit about it :)**

### Challenges
Our team is theoretically non programming one, that's why we didn't have direct access for many internal tools, APIs, raw data, environments. That is why sometimes I had to find and develop some workarounds.

### General Goals
* Prepare and launching SEO related daily checks
* Automate internal processes 

### Specific Goals
* Integration with internal and external APIs / Databases to get data insight (SEO related data from differents tools / apps)
* Constant scrapping of some pages from our domains and launching SEO related checks (valid html, valid directives, potentially harmful internal changes, internal logic checks)
* Integration with internal services endpoints for getting specific data or making specific operations
* Storing data and make operations on them
* Integration with Slack for all of above (Sending data, sending results, sending information about success / fails, all of it with details )
* Implement cron triggered Github Actions Workflows for all of above - Daily, weekly, monthly, every x hours (Build -> Making Steps -> Check every step for fails -> Check GIT diff / conditional commit )



