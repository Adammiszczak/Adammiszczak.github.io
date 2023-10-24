# GH Pages dependencies https://pages.github.com/versions/

FROM jekyll/jekyll:latest

WORKDIR /srv/jekyll

# Copy your Jekyll project into the container
COPY . .

RUN chmod -R 777 .

# Expose the default Jekyll port
EXPOSE 4000

# Serve the Jekyll site
CMD ["jekyll", "serve", "--trace", "--host", "0.0.0.0", "--no-watch"]