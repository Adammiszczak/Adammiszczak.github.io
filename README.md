# Welcome to my Blog!

This is repository for my Github Pages blog which is launched using Jekyll and Markdown Files. The other important thing is that this is one of my initial repositorices.

## Docker

You can use it and develop locally using Docker. Docker uses [jekyl image](https://github.com/envygeeks/jekyll-docker/blob/master/README.md) Unfortunately there are issues with live reload in Windows.

**Building image:**

    docker build -t my-jekyll-site .
**Run container at http://localhost:4000/ :**

    docker run -d -p 4000:4000 --name my-jekyll-container my-jekyll-site

## Docker compose

I mentioned about live reload issues for Windows users and I find some inspiration to do workaround. I decided to make container with Jekyll and Nginx server. So after every change in code Jekyll is rebuilt and nginx serves content of _site folder which build from Jekyll :) Thanks to this solution I have real time live reload, not based on Jekyll mechanism. 

**To run in detached mode just do:**

    docker-compose -p your-cointainer-name up -d
    
## Gemfiles

In order to add Ruby (underhood jekyll image) dependencies, you have to edit [Gemfile](https://github.com/Adammiszczak/Adammiszczak.github.io/blob/master/Gemfile) and add gems.