#!/usr/bin/env ruby
# Emit a deployment-focused audit of the generated archive and its runtime assets.
require "cgi"
require "digest"
require "json"

ROOT = File.expand_path("..", __dir__)
SITE_DIR = File.join(ROOT, "_site")
ARCHIVE_PATH = File.join(SITE_DIR, "articles", "index.html")

def abort_check(condition, message)
  return if condition

  escaped = message.gsub('%', '%25').gsub("\r", '%0D').gsub("\n", '%0A')
  puts "::error title=Production build audit failed::#{escaped}"
  abort("ERROR: #{message}")
end

def sha256(path)
  Digest::SHA256.file(path).hexdigest
end

def report_file(path)
  abort_check(File.file?(path), "Expected generated file is missing: #{path.delete_prefix(SITE_DIR + File::SEPARATOR)}")
  puts format("FILE %-58s bytes=%-9d sha256=%s", path.delete_prefix(SITE_DIR + File::SEPARATOR), File.size(path), sha256(path))
end

puts "::group::Production build diagnostics"
puts "commit=#{ENV.fetch('GITHUB_SHA', 'local')}"
puts "ref=#{ENV.fetch('GITHUB_REF', 'local')}"
puts "event=#{ENV.fetch('GITHUB_EVENT_NAME', 'local')}"
puts "jekyll_env=#{ENV.fetch('JEKYLL_ENV', 'unset')}"
puts "ruby=#{RUBY_VERSION} platform=#{RUBY_PLATFORM}"
puts "site_dir=_site"

[["Jekyll", ENV["JEKYLL_BUILD_LOG"]], ["Pagefind", ENV["PAGEFIND_BUILD_LOG"]]].each do |tool, path|
  next unless path && File.file?(path)

  lines = File.readlines(path, chomp: true)
  warnings = lines.select { |line| line.match?(/\bwarn(?:ing)?\b/i) }
  errors = lines.select { |line| line.match?(/\b(?:error|fatal)\b/i) }
  puts "#{tool} log: lines=#{lines.length} warning_matches=#{warnings.length} error_matches=#{errors.length}"
  warnings.each do |line|
    sanitized = line.gsub(ROOT, ".")
    puts "::warning title=#{tool} build warning::#{sanitized.gsub('%', '%25').gsub("\r", '%0D').gsub("\n", '%0A')}"
  end
  errors.each { |line| puts "#{tool} error-like output: #{line.gsub(ROOT, '.')}" }
end

abort_check(File.directory?(SITE_DIR), "Generated site directory is missing; did Jekyll build succeed?")

abort_check(File.file?(ARCHIVE_PATH), "Generated English archive is missing at /articles/.")
html = File.read(ARCHIVE_PATH)
blocks = html.scan(/<article\b[^>]*>.*?<\/article>/im).select do |block|
  block.match?(/\bclass\s*=\s*["'][^"']*\barticle-card\b[^"']*["']/i)
end
abort_check(!html.include?("The first in-depth articles are in preparation."), "The generated English archive contains its obsolete empty-state copy.")
abort_check(!blocks.empty?, "The generated English archive contains no article cards.")

card_hrefs = blocks.map do |block|
  match = block.match(/<h2\b[^>]*>\s*<a\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>(.*?)<\/a>/im)
  abort_check(match, "An article card has no linked heading: #{block[0, 180].gsub(/\s+/, ' ')}")
  href = CGI.unescapeHTML(match[1])
  title = CGI.unescapeHTML(match[2].gsub(/<[^>]+>/, "").strip)
  abort_check(href.start_with?("/articles/"), "Unexpected article-card URL #{href.inspect}")
  article_path = File.join(SITE_DIR, href.split(/[?#]/, 2).first.sub(%r!\A/!, ""))
  article_outputs = ["#{article_path}.html", File.join(article_path, "index.html"), article_path]
  abort_check(article_outputs.any? { |candidate| File.file?(candidate) }, "Article card links to a missing generated page: #{href.inspect}")
  puts "ARTICLE #{title} -> #{href}"
  href
end
abort_check(card_hrefs.uniq == card_hrefs, "The archive contains duplicate article-card URLs.")

blocks.each_with_index do |block, index|
  image_tag = block.match(/<img\b[^>]*>/i)
  abort_check(image_tag, "Article card #{index + 1} has no lead image.")
  src = image_tag[0][/\bsrc\s*=\s*["']([^"']+)["']/i, 1]
  alt = image_tag[0][/\balt\s*=\s*["']([^"']*)["']/i, 1]
  abort_check(src && alt && !alt.strip.empty?, "Article card #{index + 1} has a missing image source or alt text.")
  local_image = File.join(SITE_DIR, CGI.unescapeHTML(src).sub(%r!\A/!, ""))
  abort_check(File.file?(local_image), "Article card #{index + 1} references missing image #{src.inspect}.")
end

puts "ARCHIVE /articles/: bytes=#{File.size(ARCHIVE_PATH)} cards=#{card_hrefs.length} sha256=#{sha256(ARCHIVE_PATH)}"
%w[
  articles/index.html
  robots.txt
  sitemap.xml
  feed.xml
  pagefind/pagefind.js
  pagefind/pagefind-component-ui.js
  pagefind/pagefind-component-ui.css
].each { |relative| report_file(File.join(SITE_DIR, relative)) }

archive_sha = sha256(ARCHIVE_PATH)
pagefind_css_sha = sha256(File.join(SITE_DIR, "pagefind", "pagefind-component-ui.css"))

if (output = ENV["GITHUB_OUTPUT"])
  File.open(output, "a") do |file|
    file.puts "article_card_count=#{card_hrefs.length}"
    file.puts "article_card_hrefs=#{JSON.generate(card_hrefs)}"
    file.puts "article_html_sha256=#{archive_sha}"
    file.puts "pagefind_css_sha256=#{pagefind_css_sha}"
  end
end

if (summary = ENV["GITHUB_STEP_SUMMARY"])
  File.open(summary, "a") do |file|
    file.puts "## Generated Articles archive diagnostics"
    file.puts
    file.puts "- Commit: `#{ENV.fetch('GITHUB_SHA', 'local')}`"
    file.puts "- Rendered cards: **#{card_hrefs.length}**"
    file.puts "- Archive SHA-256: `#{archive_sha}`"
    file.puts "- Pagefind CSS SHA-256: `#{pagefind_css_sha}`"
    file.puts "- Pagefind component CSS and JavaScript: present in `_site/pagefind/`"
    file.puts
    card_hrefs.each { |href| file.puts "  - `#{href}`" }
  end
end

puts "Build audit passed: article cards, lead images, metadata files, and Pagefind assets are present."
puts "::endgroup::"
