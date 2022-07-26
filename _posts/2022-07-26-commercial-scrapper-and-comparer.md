---
layout: repo-desc
title:  "Commercial scrapper and records comparer"
author: "Adam Miszczak"
categories: [repo-description]
technologies: [javascript, typescript, node.js, nest.js, handlebars.js, mongodb, chrome api]
---

### Background

I had occasion to do one commercial project. Long story short I can't show you the code without permission, because the rights was passed to the client. But I can at least tell something about it :) The client is software house which serves some ecommerces. **For the article purposes let's call this Software House XYZ** :). 

### General Goals

All of those ecommerces were placed at Shopify CMS. XYZ was migrating all of them to some Headless CMS. During such migrations XYZ has to be 100% sure that all crucial data were migrated and this data have to be identical. The main goal was to deliver the tool which is going to automate some process, namely **scrapping these crucial elements**. So far it was made manually. Of course it has to be stored somewhere.

Other than scrapping there is need for **comparing these records e.g. from the same path, but between dev / test and prod enviroment**.

All kind of results should be **presented as HTML table**, because you can easily copy them and paste to Google Sheets or file formats like .xlsx.

There is no need for beautiful frontend, but the working one was enough and accepted by client.

### Specific Goals
* Scraping crucial head section elements like Meta Tags, SEO related elements, Opengraphs tags, Twitter Cards and so on. Presentation of result as HTML table 
* Scrapping all Schema Microdata which is set of tags placed in HTML. Presentation of result as HTML table 
* Scrapping all Schema json/ld scripts which is other form of implementation of Schema. Presentation of result as HTML table 
* Make Chrome Extension for scrapping client side HTML and calling specific app functions with just one click.
* Make external database and store all of these records
* GUI for comparing records (Communication with Database, Record Selection, Validation and checks, Presentation of result as HTML table)
* Place whole application at the server e.g. Heroku, AWS and so on.


### Problems
Because of my SEO background I knew that there could be some problems with getting full and valid HTML from those eccomerces. There isn't any Shopify documentation which tells how to get the full HTML with all of resources. There could be many dependencies like whitelisted IP's, whitelisted bots, whitelisted user-agents, request requirements, anty scrapping and anty bot policies, type of device, lazy load, SSR and so on. Every of this dependency could vary HTML.

And there were some differences e.g. I couldn't get Schema json/ld scripts if requests are coming from my app, but... I can got it from the browser, becasue it occured that they were lazy loaded. It's not good for SEO btw. :)

So that is the reason why I had to do **Chrome Extension**. It's simply scrapping HTML from the client side with all resources at HTML. With one click you can scrape HTML, view the result as HTML table and sendint this data in the background to database. This extension has also implemented other goals just with one click, namely scrapping and comparing. Of course it redirects you to application.

### Possible Future Goals
* Integration with Google Sheets and Google Drive
* Generate and storing .har (HTTP Archive) files with Cypress Har Generator
* Implements SEO related warnings at Comparison GUI.

