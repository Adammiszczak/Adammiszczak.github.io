#!/usr/bin/env ruby
# Validate a Codex-generated EN/PL article pair before any PR token is used.
require "date"
require "digest"
require "fileutils"
require "json"
require "open3"
require "pathname"
require "time"
require "tmpdir"
require "uri"
require "yaml"

ROOT = File.expand_path("..", __dir__)
WORK_DIR = File.join(ROOT, ".automation", "content-source")
CONTEXT_PATH = File.join(WORK_DIR, "context.json")
METADATA_PATH = File.join(WORK_DIR, "metadata.json")
PR_DIR = File.join(ROOT, ".automation", "article-import")
PR_CONTEXT_PATH = File.join(PR_DIR, "context.json")
PR_BODY_PATH = File.join(PR_DIR, "pr-body.md")
ALLOWED_IMAGE_EXTENSIONS = %w[.jpg .jpeg .png .webp .gif .avif].freeze
SUBSTACK_PUBLICATION_HOST = "amiszczak.substack.com".freeze
IMAGE_MIME_EXTENSIONS = {
  "image/jpeg" => ".jpg", "image/png" => ".png", "image/webp" => ".webp",
  "image/gif" => ".gif", "image/avif" => ".avif",
}.freeze

def fail_check(message)
  escaped = message.gsub("%", "%25").gsub("\r", "%0D").gsub("\n", "%0A")
  puts "::error title=Article import validation failed::#{escaped}"
  abort("ERROR: #{message}")
end

def read_json(path)
  JSON.parse(File.read(path, encoding: "UTF-8"))
rescue Errno::ENOENT, JSON::ParserError => error
  fail_check("Could not read #{Pathname.new(path).relative_path_from(Pathname.new(ROOT))}: #{error.message}")
end

def read_yaml(path)
  YAML.safe_load_file(path, permitted_classes: [Date, Time], aliases: false)
rescue Errno::ENOENT, Psych::Exception => error
  fail_check("Could not read valid YAML from #{path.delete_prefix(ROOT + File::SEPARATOR)}: #{error.message}")
end

def front_matter(path)
  source = File.read(path, encoding: "UTF-8")
  match = source.match(/\A---\s*\r?\n(.*?)\r?\n---(?:\r?\n|\z)/m)
  fail_check("#{path.delete_prefix(ROOT + File::SEPARATOR)} has no valid YAML front matter.") unless match

  data = YAML.safe_load(match[1], permitted_classes: [Date, Time], aliases: false)
  fail_check("#{path.delete_prefix(ROOT + File::SEPARATOR)} front matter must be a mapping.") unless data.is_a?(Hash)
  [data, source[match[0].length..].to_s]
rescue Psych::Exception => error
  fail_check("Invalid front matter in #{path.delete_prefix(ROOT + File::SEPARATOR)}: #{error.message}")
end

def git_output(*arguments)
  stdout, stderr, status = Open3.capture3(process_environment, "git", *arguments, chdir: ROOT)
  fail_check("git #{arguments.join(' ')} failed: #{stderr.strip}") unless status.success?
  stdout
end

def process_environment(overrides = {})
  ENV.to_h.reject { |key, _value| %w[CONTENT_PR_TOKEN GH_TOKEN GITHUB_TOKEN].include?(key) }.merge(overrides)
end

def git_success?(*arguments)
  _stdout, _stderr, status = Open3.capture3(process_environment, "git", *arguments, chdir: ROOT)
  status.success?
end

def current_changes
  status = git_output("status", "--porcelain=v1", "-z", "--untracked-files=all")
  entries = status.split("\0").reject(&:empty?)
  entries.map do |entry|
    fail_check("Unexpected Git status entry: #{entry.inspect}") if entry.length < 4
    code = entry[0, 2]
    path = entry[3..]
    fail_check("Codex staged a file before validation: #{path}") unless code[0] == " " || code[0] == "?"
    fail_check("Unexpected rename/copy status for #{path}.") if code.include?("R") || code.include?("C")
    [code, path]
  end
end

def parse_time(value, label)
  fail_check("#{label} is missing or invalid.") if value.nil? || value.to_s.strip.empty?
  case value
  when Time
    value.utc
  when DateTime
    value.to_time.utc
  when Date
    Time.utc(value.year, value.month, value.day)
  else
    Time.parse(value.to_s).utc
  end
rescue ArgumentError, TypeError
  fail_check("#{label} is not a valid date/time: #{value.inspect}")
end

def image_path_for(data, label)
  image = data["image"]
  path = image.is_a?(Hash) ? image["path"] : image
  fail_check("#{label} must provide image or image.path.") unless path.is_a?(String) && !path.empty?
  fail_check("#{label} image must be under /assets/img/articles/.") unless path.start_with?("/assets/img/articles/")
  path
end

def normalize_substack_url(value)
  uri = URI.parse(value)
  normalized_path = uri.path.sub(%r{/+\z}, "")
  valid_path = normalized_path.start_with?("/p/") && normalized_path.count("/") == 2 && !normalized_path.delete_prefix("/p/").empty?
  valid = uri.is_a?(URI::HTTPS) && uri.host&.downcase == SUBSTACK_PUBLICATION_HOST && uri.port == 443 &&
          !uri.userinfo && valid_path
  fail_check("Substack reference must use https://#{SUBSTACK_PUBLICATION_HOST}/p/<slug>.") unless valid
  uri.host = SUBSTACK_PUBLICATION_HOST
  uri.path = normalized_path
  uri.query = nil
  uri.fragment = nil
  uri.to_s
rescue URI::InvalidURIError, ArgumentError
  fail_check("Substack reference is malformed; expected https://#{SUBSTACK_PUBLICATION_HOST}/p/<slug>.")
end

def temporary_branch_name(request_id)
  run_id = ENV.fetch("GITHUB_RUN_ID", "")
  run_attempt = ENV.fetch("GITHUB_RUN_ATTEMPT", "")
  fail_check("Workflow run ID or attempt is missing or invalid.") unless run_id.match?(/\A[1-9][0-9]{0,19}\z/) && run_attempt.match?(/\A[1-9][0-9]{0,5}\z/)
  normalized = request_id.gsub(/[^A-Za-z0-9_-]+/, "-").gsub(/\A[-_]+|[-_]+\z/, "").downcase
  normalized = "request" if normalized.empty?
  digest = Digest::SHA256.hexdigest(request_id)[0, 8]
  "content/google-docs-#{normalized[0, 40]}-#{digest}-run-#{run_id}-attempt-#{run_attempt}"
end

def validate_external_urls!(context)
  begin
    value = context.fetch("substack_url")
    uri = URI.parse(value)
    host = uri.host&.downcase
    valid_path = uri.path.start_with?("/p/") && uri.path.sub(%r{/+\z}, "").count("/") == 2 && !uri.path.sub(%r{/+\z}, "").delete_prefix("/p/").empty?
    valid_port = uri.port == 443
    fail_check("substack_url must be an HTTPS /p/<slug> URL on exactly #{SUBSTACK_PUBLICATION_HOST} with no credentials.") unless uri.is_a?(URI::HTTPS) && host == SUBSTACK_PUBLICATION_HOST && valid_path && valid_port && !uri.userinfo && uri.fragment.nil?
  rescue URI::InvalidURIError, KeyError
    fail_check("substack_url is malformed; expected https://#{SUBSTACK_PUBLICATION_HOST}/p/<slug>.")
  end
  begin
    linkedin_value = context.fetch("linkedin_url")
    linkedin_uri = URI.parse(linkedin_value)
    linkedin_host = linkedin_uri.host&.downcase
    valid_linkedin_host = linkedin_host && (linkedin_host == "lnkd.in" || linkedin_host == "linkedin.com" || linkedin_host.end_with?(".linkedin.com"))
    fail_check("linkedin_url must use HTTPS on linkedin.com, a linkedin.com subdomain, or lnkd.in; its exact submitted value must be preserved.") unless linkedin_uri.is_a?(URI::HTTPS) && valid_linkedin_host && !linkedin_uri.userinfo
  rescue URI::InvalidURIError
    fail_check("linkedin_url is malformed.")
  end
  request_id = context.fetch("request_id")
  fail_check("request_id contains unsupported characters or is too long.") unless request_id.match?(/\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\z/) && !request_id.include?("..") && !request_id.end_with?(".")
  content_id = context.fetch("content_id")
  fail_check("content_id contains unsupported characters or is too long.") unless content_id.match?(/\A[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?\z/)
end

def verify_fetched_integrity!(context, metadata)
  [File.join(ROOT, ".automation"), WORK_DIR, CONTEXT_PATH, METADATA_PATH,
   File.join(WORK_DIR, "source.md")].each do |path|
    fail_check("Source package files must not be symlinks: #{path.delete_prefix(ROOT + File::SEPARATOR)}") if File.symlink?(path)
  end
  fail_check("Source context must use Google Docs acquisition.") unless context["source_mode"] == "google_docs" && metadata["source_mode"] == "google_docs"
  expected_paths = %w[context.json metadata.json source.md]
  image_path = metadata["lead_image_path"]
  fail_check("Fetched metadata has no lead image path.") unless image_path.is_a?(String) && image_path.match?(%r{\A\.automation/content-source/lead-image\.(?:jpg|png|webp|gif|avif)\z})
  expected_paths << File.basename(image_path)
  actual_paths = Dir.children(WORK_DIR).sort
  fail_check("Source artifact package contains unexpected files.") unless actual_paths == expected_paths.sort

  source_path = File.join(WORK_DIR, "source.md")
  image_absolute = File.join(ROOT, image_path)
  hashes = {
    "SOURCE_MD_SHA256" => source_path,
    "CONTEXT_SHA256" => CONTEXT_PATH,
    "METADATA_SHA256" => METADATA_PATH,
    "LEAD_IMAGE_SHA256" => image_absolute,
  }
  hashes.each do |name, path|
    expected = ENV[name]
    fail_check("Missing pre-Codex integrity value for #{name.downcase}.") if expected.nil? || expected.empty?
    fail_check("Source artifact must be a regular non-symlink file: #{name.downcase}.") if File.symlink?(path)
    fail_check("Source artifact changed after acquisition: #{name.downcase}.") unless File.file?(path) && Digest::SHA256.file(path).hexdigest == expected
  end
  source = File.binread(source_path).force_encoding(Encoding::UTF_8)
  fail_check("Imported Google Markdown must be valid UTF-8.") unless source.valid_encoding?
  fail_check("Imported Google Markdown must be non-empty.") if source.strip.empty?
  document = metadata["document"]
  image = metadata["image"]
  expected_image_extension = image.is_a?(Hash) ? IMAGE_MIME_EXTENSIONS[image["mimeType"]] : nil
  source_folder_id = ENV.fetch("CONTENT_SOURCE_FOLDER_ID", "")
  doc_valid = document.is_a?(Hash) && document["id"] == context["doc_file_id"] &&
              document["version"].to_s == context["doc_version"] &&
              document["mimeType"] == "application/vnd.google-apps.document" &&
              document["parents"].is_a?(Array) && document["parents"].include?(source_folder_id) &&
              document["canDownload"] == true
  fail_check("Google Doc metadata does not match the trusted workflow snapshot.") unless doc_valid
  image_valid = image.is_a?(Hash) && image["id"] == context["image_file_id"] &&
                image["version"].to_s == context["image_version"] &&
                image["parents"].is_a?(Array) && image["parents"].include?(source_folder_id) &&
                image["canDownload"] == true && expected_image_extension &&
                File.extname(image_path) == expected_image_extension
  fail_check("Lead-image metadata does not match the trusted workflow snapshot.") unless image_valid
  fail_check("Metadata must identify the deterministic source paths.") unless metadata["source_path"] == ".automation/content-source/source.md" && metadata["metadata_path"] == ".automation/content-source/metadata.json"
end

def verify_git_remote!
  repository = ENV.fetch("GITHUB_REPOSITORY", "")
  server = ENV.fetch("GITHUB_SERVER_URL", "https://github.com").sub(%r{/+$}, "")
  fail_check("Missing GitHub repository context.") if repository.empty? || repository.include?("\n")
  expected = "#{server}/#{repository}".downcase
  accepted_urls = [expected, "#{expected}.git"]
  fetch_url = git_output("remote", "get-url", "origin").strip.downcase
  push_url = git_output("remote", "get-url", "--push", "origin").strip.downcase
  fail_check("The origin fetch URL does not point to this GitHub repository.") unless accepted_urls.include?(fetch_url)
  fail_check("The origin push URL does not point to this GitHub repository.") unless accepted_urls.include?(push_url)
end

def validate!
  context = read_json(CONTEXT_PATH)
  metadata = read_json(METADATA_PATH)
  {
    "content_id" => "CONTENT_ID",
    "doc_file_id" => "DOC_FILE_ID",
    "doc_version" => "DOC_VERSION",
    "image_file_id" => "IMAGE_FILE_ID",
    "image_version" => "IMAGE_VERSION",
    "linkedin_url" => "LINKEDIN_URL",
    "published_at" => "PUBLISHED_AT",
    "request_id" => "REQUEST_ID",
  }.each do |key, environment_name|
    fail_check("Temporary workflow context no longer matches the workflow input #{key}.") unless context[key] == ENV.fetch(environment_name, nil)
  end
  fail_check("Temporary context does not contain the normalized canonical Substack URL.") unless context["substack_url"] == normalize_substack_url(ENV.fetch("SUBSTACK_URL", ""))
  submitted_modified_at = ENV.fetch("LAST_MODIFIED_AT", "")
  if submitted_modified_at.empty?
    fail_check("last_modified_at must be omitted when the workflow input is empty.") if context.key?("last_modified_at")
  else
    fail_check("Temporary context no longer matches the workflow input last_modified_at.") unless context["last_modified_at"] == submitted_modified_at
  end
  validate_external_urls!(context)
  verify_fetched_integrity!(context, metadata)
  verify_git_remote!
  changes = current_changes
  fail_check("The .automation directory must not be staged or committed.") if changes.any? { |_code, path| path.start_with?(".automation/") }

  new_posts = changes.filter_map do |code, path|
    next unless path.start_with?("_posts/") && path.end_with?(".md")
    fail_check("Article files must be new and untracked; existing article changed: #{path}") unless code == "??"
    file_path = File.join(ROOT, path)
    fail_check("Article files must be regular files, not symlinks: #{path}") if File.symlink?(file_path)
    data, body = front_matter(file_path)
    next unless data["substack_url"] == context.fetch("substack_url")
    { path: path, data: data, body: body }
  end
  fail_check("Expected exactly two new article files with the normalized substack_url; found #{new_posts.length}.") unless new_posts.length == 2

  by_language = new_posts.group_by { |post| post[:data]["lang"] }
  fail_check("The new articles must contain one lang: en and one lang: pl version.") unless by_language.keys.sort == %w[en pl] && by_language.values.all? { |items| items.length == 1 }
  en = by_language.fetch("en").first
  pl = by_language.fetch("pl").first
  en_data = en[:data]
  pl_data = pl[:data]

  mapping_path = "_data/localized_pages.yml"
  mapping_status = changes.find { |_code, path| path == mapping_path }
  fail_check("Codex must update _data/localized_pages.yml.") unless mapping_status && mapping_status[0] == " M"
  other_changes = changes.map(&:last) - [en[:path], pl[:path], mapping_path]
  image_changes = other_changes.select { |path| path.start_with?("assets/img/articles/") }
  fail_check("Expected exactly one new article image under assets/img/articles/; found #{image_changes.length}.") unless image_changes.length == 1
  fail_check("The article image must be a new untracked raster file.") unless changes.find { |_code, path| path == image_changes.first }&.first == "??"
  image_extension = File.extname(image_changes.first).downcase
  fail_check("Article image extension must be one of #{ALLOWED_IMAGE_EXTENSIONS.join(', ')}.") unless ALLOWED_IMAGE_EXTENSIONS.include?(image_extension)
  source_image_extension = File.extname(metadata.fetch("lead_image_path")).downcase
  fail_check("Article image extension must preserve the downloaded source image format.") unless image_extension == source_image_extension
  fail_check("Article image filename must be lowercase and descriptive.") unless image_changes.first.match?(%r{\Aassets/img/articles/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:jpg|jpeg|png|webp|gif|avif)\z})
  fail_check("Unexpected generated or unrelated files changed: #{(other_changes - image_changes).join(', ')}") unless (other_changes - image_changes).empty?
  fail_check("Automation source files must not be committed.") if changes.any? { |_code, path| path.start_with?(".automation/") }
  trailing_whitespace = [en[:path], pl[:path]].flat_map do |path|
    File.foreach(File.join(ROOT, path)).with_index(1).filter_map do |line, line_number|
      "#{path}:#{line_number}" if line.match?(/[ \t]+(?:\r?\n)?\z/)
    end
  end
  fail_check("Generated Markdown must not contain trailing whitespace; use blank lines instead of hard-break spaces: #{trailing_whitespace.join(', ')}") unless trailing_whitespace.empty?

  baseline_mapping = YAML.safe_load(git_output("show", "HEAD:#{mapping_path}"), permitted_classes: [Date, Time], aliases: false)
  current_mapping = read_yaml(File.join(ROOT, mapping_path))
  translation_key = en_data["translation_key"]
  key_pattern = /\A[a-z][a-z0-9]*(?:_[a-z0-9]+)*\z/
  fail_check("translation_key must be a topic-derived snake_case key.") unless translation_key.is_a?(String) && key_pattern.match?(translation_key)
  fail_check("translation_key must be shared by EN and PL.") unless pl_data["translation_key"] == translation_key
  fail_check("translation_key must not be derived from request_id.") if translation_key.casecmp(context.fetch("request_id")).zero?
  fail_check("translation_key already exists in the base localized_pages.yml.") if baseline_mapping.key?(translation_key)
  group = current_mapping[translation_key]
  fail_check("localized_pages.yml must map EN, PL, and x_default for #{translation_key}.") unless group.is_a?(Hash)

  en_slug = File.basename(en[:path]).sub(/\A\d{4}-\d{2}-\d{2}-/, "").sub(/\.md\z/, "")
  fail_check("The English post filename must use YYYY-MM-DD-descriptive-slug.md.") unless en[:path].match?(%r{\A_posts/\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md\z})
  fail_check("The Polish post filename must use YYYY-MM-DD-polish-slug-pl.md.") unless pl[:path].match?(%r{\A_posts/\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*-pl\.md\z})
  en_path = en_data["permalink"] || "/articles/#{en_slug}"
  pl_path = pl_data["permalink"]
  fail_check("The English article must remain at /articles/<slug> without an /en/ prefix.") unless en_path.match?(%r{\A/articles/[a-z0-9]+(?:-[a-z0-9]+)*\z})
  fail_check("The Polish article must use an explicit /pl/artykuly/<slug> permalink.") unless pl_path.is_a?(String) && pl_path.match?(%r{\A/pl/artykuly/[a-z0-9]+(?:-[a-z0-9]+)*\z})
  expected_group = { "en" => en_path, "pl" => pl_path, "x_default" => en_path }
  fail_check("localized_pages.yml paths do not match the new articles: expected #{expected_group.inspect}, got #{group.inspect}.") unless group == expected_group

  expected_date = parse_time(context.fetch("published_at"), "published_at workflow input")
  en_date = parse_time(en_data["date"], "English article date")
  pl_date = parse_time(pl_data["date"], "Polish article date")
  fail_check("Both article dates must preserve the trusted published_at timestamp.") unless en_date == expected_date && pl_date == expected_date
  expected_filename_date = context.fetch("published_at").to_s[0, 10]
  [en, pl].each do |post|
    fail_check("Post filename date must match the trusted published_at date.") unless File.basename(post[:path])[0, 10] == expected_filename_date
  end
  %w[en pl].zip([en, pl]).each do |language, post|
    data = post[:data]
    label = language == "en" ? "English" : "Polish"
    fail_check("#{label} article must use layout: article and section: articles.") unless data["layout"] == "article" && data["section"] == "articles"
    fail_check("#{label} article must include categories: [articles].") unless data["categories"] == ["articles"]
    fail_check("#{label} title and description are required.") unless [data["title"], data["description"]].all? { |value| value.is_a?(String) && !value.strip.empty? }
    fail_check("#{label} article title must not contain an em dash.") if data["title"].include?("—")
    fail_check("#{label} article must not have an empty body.") if post[:body].strip.empty?
    fail_check("#{label} article headings must not contain an em dash.") if post[:body].match?(/^\s{0,3}\#{1,6}.*—/)
    fail_check("#{label} article must preserve the exact supplied linkedin_url.") unless data["linkedin_url"] == context.fetch("linkedin_url")
    fail_check("#{label} article must use the normalized Substack article URL.") unless data["substack_url"] == context.fetch("substack_url")
    fail_check("#{label} article must include a non-empty image_alt.") unless data["image_alt"].is_a?(String) && !data["image_alt"].strip.empty?
    fail_check("#{label} article must include Adam Miszczak as the author.") unless data.dig("author", "name") == "Adam Miszczak"
    expected_author_path = language == "pl" ? "/pl/o-mnie/" : "/about-me/"
    fail_check("#{label} article author URL must follow the localized site route.") unless data.dig("author", "url") == "https://adammiszczak.github.io#{expected_author_path}"
  end
  fail_check("Polish metadata must use locale: pl_PL.") unless pl_data["locale"] == "pl_PL"
  fail_check("English locale, when explicit, must be en_US.") if en_data["locale"] && en_data["locale"] != "en_US"
  fail_check("English and Polish image_alt text must be localized separately.") if en_data["image_alt"] == pl_data["image_alt"]
  captions = [en_data["image_caption"], pl_data["image_caption"]]
  fail_check("Image captions must be provided and localized for both articles, or omitted from both.") unless captions.all?(&:nil?) || captions.all? { |caption| caption.is_a?(String) && !caption.strip.empty? }
  fail_check("EN and PL image captions must be localized separately.") if captions.all? && captions.first == captions.last
  en_tags = en_data["tags"]
  pl_tags = pl_data["tags"]
  unless en_tags.is_a?(Array) && pl_tags.is_a?(Array)
    fail_check("Both articles must define tags as arrays; EN=#{en_tags.inspect}, PL=#{pl_tags.inspect}.")
  end
  unless en_tags.all? { |tag| tag.is_a?(String) } && pl_tags.all? { |tag| tag.is_a?(String) }
    fail_check("Article tags must all be strings; EN=#{en_tags.inspect}, PL=#{pl_tags.inspect}.")
  end
  unless en_tags.sort == pl_tags.sort
    fail_check("English and Polish articles must share the same tags; EN=#{en_tags.inspect}, PL=#{pl_tags.inspect}.")
  end
  taxonomy = read_yaml(File.join(ROOT, "_data", "taxonomy.yml"))
  approved_tags = Array(taxonomy["tags"])
  tags = en_tags
  fail_check("Both articles must use at least one approved taxonomy tag.") if tags.empty?
  fail_check("Choose a short list of no more than four approved taxonomy tags.") if tags.length > 4
  invalid_tags = tags - approved_tags
  fail_check("Unapproved taxonomy tags: #{invalid_tags.join(', ')}") unless invalid_tags.empty?

  en_image = image_path_for(en_data, "English article")
  pl_image = image_path_for(pl_data, "Polish article")
  fail_check("EN and PL articles must use the same relevant image.") unless en_image == pl_image
  fail_check("Front matter image must point to the new article image file.") unless en_image.delete_prefix("/") == image_changes.first
  image_file = File.join(ROOT, image_changes.first)
  fail_check("Referenced article image must be a regular file, not a symlink.") if File.symlink?(image_file)
  fail_check("Referenced article image does not exist or is empty.") unless File.file?(image_file) && File.size(image_file).positive?
  fetched_image = File.expand_path(metadata.fetch("lead_image_path"), ROOT)
  fail_check("The article image must preserve the validated Google Drive lead image bytes.") unless Digest::SHA256.file(image_file).hexdigest == Digest::SHA256.file(fetched_image).hexdigest

  fail_check("If last_modified_at is set, it must be set consistently for both translations.") unless !!en_data["last_modified_at"] == !!pl_data["last_modified_at"]
  if en_data["last_modified_at"] || pl_data["last_modified_at"]
    modified = context["last_modified_at"]
    fail_check("last_modified_at is only allowed when supplied as a valid workflow input.") if modified.nil? || modified.to_s.empty?
    expected_modified = parse_time(modified, "last_modified_at")
    fail_check("last_modified_at must represent a later source modification.") unless expected_modified > expected_date
    [en_data["last_modified_at"], pl_data["last_modified_at"]].compact.each do |value|
      fail_check("last_modified_at must match the supplied real modification timestamp.") unless parse_time(value, "last_modified_at") == expected_modified
    end
  end

  changed_content = [en[:path], pl[:path], mapping_path, image_changes.first]
  changed_content.each do |path|
    content = File.binread(File.join(ROOT, path))
    fail_check("Potential credential/token pattern found in #{path}.") if content.match?(/(?:sk-[A-Za-z0-9_-]{20,}|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})/)
    fail_check("Local machine paths must not be published in #{path}.") if content.match?(%r{(?:/home/[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+|file://)}i)
  end

  title = en_data.fetch("title").gsub(/[\r\n\t]+/, " ").gsub(/\s{2,}/, " ").strip
  fail_check("English title contains control characters unsuitable for a PR title.") if title.match?(/[[:cntrl:]]/)
  pr_context = context.merge(
    "branch_name" => temporary_branch_name(context.fetch("request_id")),
    "en_article_path" => en[:path],
    "pl_article_path" => pl[:path],
    "image_path" => image_changes.first,
    "translation_key" => translation_key,
    "english_title" => title,
  )
  [PR_DIR, PR_CONTEXT_PATH, PR_BODY_PATH].each do |path|
    fail_check("PR manifest paths must not be symlinks.") if File.symlink?(path)
  end
  FileUtils.mkdir_p(PR_DIR)
  File.write(PR_CONTEXT_PATH, JSON.pretty_generate(pr_context) + "\n", mode: "w", encoding: "UTF-8")
  body = <<~BODY
    Automated article import

    Substack reference URL: #{context.fetch('substack_url')}
    content_id: #{context.fetch('content_id')}
    LinkedIn URL: #{context.fetch('linkedin_url')}
    request_id: #{context.fetch('request_id')}
    English article: #{en[:path]}
    Polish article: #{pl[:path]}
    translation_key: #{translation_key}

    Review checklist:
    - [ ] Content reviewed
    - [ ] EN reviewed
    - [ ] PL reviewed
    - [ ] Image/caption reviewed
    - [ ] Preview reviewed
  BODY
  File.write(PR_BODY_PATH, body, mode: "w", encoding: "UTF-8")
  puts "Validated EN/PL article pair, approved tags, exact social destinations, localization mapping, lead-image bytes, and trusted timestamps."
  puts "English: #{en[:path]} -> #{en_path}"
  puts "Polish: #{pl[:path]} -> #{pl_path}"
  puts "translation_key: #{translation_key}"
end

def run!(*arguments, environment: {})
  safe_environment = process_environment(environment)
  stdout, stderr, status = Open3.capture3(safe_environment, *arguments, chdir: ROOT)
  unless status.success?
    detail = [stderr, stdout].reject(&:empty?).join("\n").strip
    fail_check("#{arguments.first} failed: #{detail}")
  end
  print stdout unless stdout.empty?
end

def git_blob(path)
  stdout, stderr, status = Open3.capture3(process_environment, "git", "show", ":#{path}", chdir: ROOT, binmode: true)
  fail_check("Could not read staged file #{path}: #{stderr}") unless status.success?
  stdout
end

def publish!
  context = read_json(PR_CONTEXT_PATH)
  token = ENV["CONTENT_PR_TOKEN"]
  fail_check("CONTENT_PR_TOKEN is required only for the post-validation publishing step.") if token.nil? || token.empty?
  paths = [context.fetch("en_article_path"), context.fetch("pl_article_path"), context.fetch("image_path"), "_data/localized_pages.yml"]
  fail_check("Git staging area must be empty before the publishing step.") unless git_success?("diff", "--cached", "--quiet")
  run!("git", "config", "user.name", "github-actions[bot]")
  run!("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
  run!("git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "add", "--", *paths)
  # Extra empty lines at EOF do not affect Markdown; keep other whitespace checks strict.
  run!("git", "-c", "core.whitespace=-blank-at-eof", "diff", "--cached", "--check")
  staged = git_output("diff", "--cached", "--name-only").lines.map(&:chomp).sort
  fail_check("Only validated article, image, and localization files may be staged: #{staged.inspect}") unless staged == paths.sort
  paths.each do |path|
    fail_check("Staged bytes differ from the files that passed validation: #{path}") unless git_blob(path) == File.binread(File.join(ROOT, path))
  end
  run!("git", "checkout", "-b", context.fetch("branch_name"))
  git_environment = {
    "GIT_CONFIG_NOSYSTEM" => "1",
    "GIT_CONFIG_GLOBAL" => "/dev/null",
  }
  run!("git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "commit", "-m", "Automated article import: #{context.fetch('english_title')}", environment: git_environment)

  askpass = File.join(Dir.tmpdir, "content-pr-askpass-#{Process.pid}")
  File.write(askpass, <<~'SH', mode: "w", perm: 0o700)
    #!/bin/sh
    case "$1" in
      *Username*) printf '%s\n' 'x-access-token' ;;
      *Password*) printf '%s\n' "$CONTENT_PR_TOKEN" ;;
      *) exit 1 ;;
    esac
  SH
  begin
    git_environment = {
      "GIT_ASKPASS" => askpass,
      "GIT_TERMINAL_PROMPT" => "0",
      "CONTENT_PR_TOKEN" => token,
      "GIT_CONFIG_NOSYSTEM" => "1",
      "GIT_CONFIG_GLOBAL" => "/dev/null",
    }
    run!("git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "-c", "http.proxy=", "push", "--set-upstream", "origin", context.fetch("branch_name"), environment: git_environment)
  ensure
    File.delete(askpass) if File.exist?(askpass)
  end

  gh_environment = {
    "GH_TOKEN" => token,
    "GH_PROMPT_DISABLED" => "1",
    "GIT_CONFIG_NOSYSTEM" => "1",
    "GIT_CONFIG_GLOBAL" => "/dev/null",
    "GIT_CONFIG_COUNT" => "3",
    "GIT_CONFIG_KEY_0" => "core.hooksPath",
    "GIT_CONFIG_VALUE_0" => "/dev/null",
    "GIT_CONFIG_KEY_1" => "credential.helper",
    "GIT_CONFIG_VALUE_1" => "",
    "GIT_CONFIG_KEY_2" => "diff.external",
    "GIT_CONFIG_VALUE_2" => "",
  }
  run!(
    "gh", "pr", "create",
    "--base", "master",
    "--head", context.fetch("branch_name"),
    "--title", "Content: #{context.fetch('english_title')}",
    "--body-file", PR_BODY_PATH,
    environment: gh_environment,
  )
end

mode = ARGV.fetch(0, "validate")
case mode
when "validate"
  validate!
when "publish"
  publish!
else
  fail_check("Usage: ruby _scripts/validate_article_import.rb {validate|publish}")
end
