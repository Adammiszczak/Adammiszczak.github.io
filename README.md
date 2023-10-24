# Welcome to my Blog!

This is repository for my Github Pages blog which is launched using Jekyll and Markdown Files. The other important thing is that this is one of my initial repositorices.

## Docker

You can use it and develop locally using Docker. Docker uses [jekyl image](https://github.com/envygeeks/jekyll-docker/blob/master/README.md)

**Building image:**

    docker build -t my-jekyll-site .
**Run container at http://localhost:4000/ :**

    docker run -d -p 4000:4000 --name my-jekyll-container my-jekyll-site
    
## Gemfiles

In order to add Ruby (underhood jekyll image) dependencies, you have to edit [Gemfile](https://github.com/Adammiszczak/Adammiszczak.github.io/blob/master/Gemfile) and add gems.