#!/usr/bin/env ruby
# Validate localized routes and rendered SEO/technical signals after a Jekyll build.
require "cgi"
require "json"
require "rexml/document"
require "set"
require "yaml"

ROOT = File.expand_path("..", __dir__)
SITE_DIR = File.join(ROOT, "_site")
config = YAML.safe_load_file(File.join(ROOT, "_config.yml"))
groups = YAML.safe_load_file(File.join(ROOT, "_data/localized_pages.yml"))
routes = YAML.safe_load_file(File.join(ROOT, "_data/locale_routes.yml"))
base_url = "#{config.fetch('url')}#{config.fetch('baseurl', '')}".sub(%r!/$!, "")

def check(condition, message)
  raise message unless condition
end

def output_candidates(path)
  clean = path.sub(%r!^/+!, "")
  return [File.join(SITE_DIR, "index.html")] if clean.empty?
  return [File.join(SITE_DIR, clean, "index.html")] if path.end_with?("/")

  [File.join(SITE_DIR, "#{clean}.html"), File.join(SITE_DIR, clean), File.join(SITE_DIR, clean, "index.html")]
end

def output_path(path)
  output_candidates(path).find { |candidate| File.file?(candidate) } || output_candidates(path).first
end

def tags(html, name)
  html.scan(/<#{name}\b[^>]*>/i)
end

def attr(tag, name)
  match = tag.match(/\b#{Regexp.escape(name)}\s*=\s*["']([^"']*)["']/i)
  CGI.unescapeHTML(match[1]) if match
end

def link_tags(html)
  tags(html, "link")
end

def alternate_pairs(html)
  link_tags(html).filter_map do |tag|
    next unless attr(tag, "rel") == "alternate" && attr(tag, "hreflang")

    [attr(tag, "hreflang"), attr(tag, "href")]
  end.to_set
end

check(File.directory?(SITE_DIR), "Missing _site; run Jekyll build first.")
validated_pages = 0

groups.each do |key, variants|
  localized = variants.reject { |language, _| language == "x_default" }
  check(localized.keys.sort == %w[en pl], "#{key}: expected one English and one Polish page")
  check(variants["x_default"] == variants["en"], "#{key}: x-default must use the English equivalent")
  expected_alternates = localized.map do |language, path|
    [language, "#{base_url}#{path}"]
  end.to_set
  expected_alternates << ["x-default", "#{base_url}#{variants.fetch('x_default')}"]

  localized.each do |language, path|
    file = output_path(path)
    check(File.file?(file), "#{key}: missing generated page for #{path} (looked for #{file})")
    html = File.read(file)
    lang_match = html.match(/<html\b[^>]*\blang=["']([^"']+)["']/i)
    check(lang_match && lang_match[1] == language, "#{path}: expected html lang=#{language}")
    check(tags(html, "pagefind-modal-trigger").length == 1, "#{path}: expected one localized Pagefind search trigger")
    check(html.scan(/<pagefind-modal(?=[\s>])[^>]*>/i).length == 1, "#{path}: expected one Pagefind search modal")
    check(html.match?(%r!<main\b[^>]*\bdata-pagefind-body(?:\s|>)!i), "#{path}: Pagefind must index main content only")

    canonicals = link_tags(html).select { |tag| attr(tag, "rel") == "canonical" }.map { |tag| attr(tag, "href") }
    check(canonicals == ["#{base_url}#{path}"], "#{path}: expected one self-canonical, got #{canonicals.inspect}")
    check(alternate_pairs(html) == expected_alternates, "#{path}: hreflang set is missing, inconsistent, or non-reciprocal")
    check(tags(html, "meta").count { |tag| attr(tag, "name") == "description" } == 1, "#{path}: expected one meta description")
    expected_og_locale = language == "pl" ? "pl_PL" : "en_US"
    check(tags(html, "meta").any? { |tag| attr(tag, "property") == "og:locale" && attr(tag, "content") == expected_og_locale }, "#{path}: Open Graph locale is incorrect")

    tags(html, "img").each do |tag|
      source = attr(tag, "src")
      next unless source&.start_with?("/")
      check(File.file?(File.join(SITE_DIR, source.sub(%r!^/+!, ""))), "#{path}: missing local image #{source}")
    end
    tags(html, "a").each do |tag|
      href = attr(tag, "href")
      next unless href&.start_with?("/")
      target_path = href.split(/[?#]/, 2).first
      check(File.file?(output_path(target_path)), "#{path}: broken local link #{href}")
    end

    language_switches = html.scan(/<nav\b([^>]*)class=["']language-switch["'][^>]*>(.*?)<\/nav>/im)
    check(language_switches.length == 2, "#{path}: expected header and footer language controls")
    switch_targets = language_switches.first[1].scan(/<a\b[^>]*>/i).map { |tag| attr(tag, "href") }.to_set
    check(switch_targets == Set[variants.fetch("en"), variants.fetch("pl")], "#{path}: language control must link to the equivalent pages")

    theme_controls = tags(html, "button").select { |tag| attr(tag, "class") == "theme-toggle" }
    check(theme_controls.length == 2, "#{path}: expected header and footer theme controls")
    expected_theme_label = language == "pl" ? "Włącz tryb ciemny" : "Switch to dark mode"
    check(theme_controls.all? { |tag| attr(tag, "aria-label") == expected_theme_label }, "#{path}: theme control label is not localized")
    footer_social_links = tags(html, "a").select { |tag| attr(tag, "class").to_s.split.include?("footer-social-link") }
    expected_social_urls = %w[
      https://www.linkedin.com/in/adam-miszczak/
      https://substack.com/@adammiszczak
      https://github.com/Adammiszczak/Adammiszczak.github.io
    ].to_set
    check(footer_social_links.map { |tag| attr(tag, "href") }.to_set == expected_social_urls, "#{path}: footer social icon links are missing or incorrect")
    check(footer_social_links.all? { |tag| attr(tag, "aria-label").to_s.length.positive? }, "#{path}: footer social icons need accessible labels")

    json_blocks = html.scan(%r!<script type="application/ld\+json">\s*(.*?)\s*</script>!m).map { |entry| JSON.parse(entry.first) }
    articles = json_blocks.select { |entry| entry["@type"] == "BlogPosting" }
    if articles.any?
      check(articles.length == 1, "#{path}: expected one BlogPosting entity")
      article = articles.first
      check(article["inLanguage"] == language, "#{path}: BlogPosting language is incorrect")
      check(article["articleSection"] == (language == "pl" ? "Artykuły" : "Articles"), "#{path}: article section is not localized")
      author_url = article.dig("author", "url")
      check(author_url == "#{base_url}#{routes.fetch(language).fetch('about')}", "#{path}: localized author URL is incorrect")
      check(article.dig("image", "description").to_s.length.positive?, "#{path}: structured image description is missing")
      check(html.scan('class="article-discussion"').length == 1, "#{path}: expected exactly one article discussion call to action")
      check(!html.match?(/Continue the conversation|Kontynuujmy rozmowę/), "#{path}: found the old generic or duplicated call to action")
    end
    validated_pages += 1
  end
end

root = File.read(File.join(SITE_DIR, "index.html"))
check(alternate_pairs(root).include?(["x-default", "#{base_url}/"]), "English home page must be the root x-default")
check(root.include?("Senior SEO / GEO &amp; AI Search Specialist") || root.include?("Senior SEO / GEO & AI Search Specialist"), "Root must remain the English home page")
check(!root.include?("Choose a language"), "Root must not be a language selector page")
check(!Dir.exist?(File.join(SITE_DIR, "en")), "English content must not be moved into an /en/ catalog")

%w[/pl/about-me/ /pl/articles/ /pl/sitemap/ /pl/articles/google-search-central-live-deep-dive-seo-ai-search-questions].each do |old_polish_path|
  check(!output_candidates(old_polish_path).any? { |candidate| File.file?(candidate) }, "Found an untranslated Polish URL that should have a localized slug: #{old_polish_path}")
end

robots = File.read(File.join(SITE_DIR, "robots.txt"))
agents = robots.scan(/^User-agent:\s*(.+?)\s*$/).flatten
check(agents == ["*"], "robots.txt must allow all crawlers with one wildcard user-agent rule")
check(robots.match?(/^User-agent:\s*\*\s*\r?\nAllow:\s*\/\s*$/), "robots.txt must allow crawling of the full public site")
check(robots.match?(%r!^Disallow:\s*/pagefind/\s*$!), "robots.txt must keep Pagefind index assets out of crawler fetches")
check(robots.include?("Sitemap: #{base_url}/sitemap.xml"), "robots.txt must point to the generated XML sitemap")
pagefind_dir = File.join(SITE_DIR, "pagefind")
%w[pagefind.js pagefind-component-ui.js pagefind-component-ui.css].each do |asset|
  check(File.file?(File.join(pagefind_dir, asset)), "Missing generated Pagefind asset: #{asset}")
end
check(!File.file?(File.join(SITE_DIR, "search.html")) && !File.directory?(File.join(SITE_DIR, "search")), "Search must stay in the modal without creating an indexable search page")

{"en" => "/feed.xml", "pl" => "/pl/feed.xml"}.each do |language, path|
  feed_file = output_path(path)
  check(File.file?(feed_file), "Missing #{language} feed at #{path}")
  feed = REXML::Document.new(File.read(feed_file))
  check(feed.root.attributes["xml:lang"] == language, "#{language} feed has the wrong language")
  entry_links = REXML::XPath.match(feed, "//*[local-name()='entry']/*[local-name()='link']").map { |node| node.attributes["href"] }
  if language == "pl"
    check(entry_links.any? { |url| url.include?("/pl/artykuly/") }, "Polish feed does not contain the translated article")
    check(entry_links.all? { |url| url.include?("/pl/") }, "Polish feed includes a non-Polish post")
  else
    check(entry_links.none? { |url| url.include?("/pl/") }, "English feed includes a Polish post")
  end
end

sitemap = REXML::Document.new(File.read(File.join(SITE_DIR, "sitemap.xml")))
sitemap_urls = REXML::XPath.match(sitemap, "//*[local-name()='loc']").map(&:text)
groups.each_value do |variants|
  variants.each do |language, path|
    next if language == "x_default"
    check(sitemap_urls.include?("#{base_url}#{path}"), "XML sitemap is missing #{path}")
  end
end
check(sitemap_urls.none? { |url| url.include?("/en/") }, "XML sitemap contains an /en/ route")
check(sitemap_urls.none? { |url| url.include?("/pagefind/") }, "XML sitemap must not contain Pagefind index assets")

puts "Site checks passed: #{validated_pages} language pages, reciprocal hreflang pairs, Pagefind modal assets without a search route, wildcard crawler access, locale-specific feeds, and sitemap membership."
