---
layout: repo-desc
title:  "Har Exporter Chrome extension"
author: "Adam Miszczak"
categories: [repo-description]
technologies: [javascript, chrome api]
---

### Background
Due to one of my previous tasks namely [scrapper and comparer](/repo-description/commercial-scrapper-and-comparer) I got another one to bring solution which enables exporting all requests in HTTP Archive format (.har) when you are querying some webpage.

### Motivation
Using extension you can export requests from client perspective and you are able to simulate various events. There are various methods, but for example using Cypress with plugin to generate .har files was problematic, because of some reasons. In general, there are lack of customization and configuration. There are also some wrappers with Chromium for libraries like node-fetch, but then you can't export specific requests like some Google Tag Manager events launched by some kind of (user) interactions. That is why this extension was created.

### Goals
* Exporting all requests in HTTP Archive format (.har)
* Make it easy for use without too many interaction
* Make an options panel
* Filtering requests by specific url. It could be domain or whole path
* Make option for saving request response body or not
* Make options to choose Mime Types of requests which have to be saved
* Sending requests to database in order to comparing them between each other
* Sending notifications to operational systems after storing request at database




