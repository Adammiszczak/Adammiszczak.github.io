#!/usr/bin/env ruby
# Validate a Codex-generated EN/PL Substack article pair before any PR token is used.
require "date"
require "digest"
require "json"
require "open3"
require "pathname"
require "time"
require "tmpdir"
require "uri"
require "yaml"

ROOT = File.expand_path("..", __dir__)
WORK_DIR = File.join(ROOT, ".automation", "substack")
CONTEXT_PATH = File.join(WORK_DIR, "context.json")
METADATA_PATH = File.join(WORK_DIR, "metadata.json")
ALLOWED_IMAGE_EXTENSIONS = %w[.jpg .jpeg .png .webp .gif .avif].freeze

def fail_check(message)
  escaped = message.gsub("%", "%25").gsub("\r", "%0D").gsub("\n", "%0A")
  puts "::error title=Substack import validation failed::#{escaped}"
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

def validate_external_urls!(context)
  {
    "substack_url" => [context.fetch("substack_url"), "substack.com"],
    "linkedin_url" => [context.fetch("linkedin_url"), "linkedin.com"],
  }.each do |label, (value, domain)|
    begin
      uri = URI.parse(value)
      host = uri.host&.downcase
      valid_host = host && (host == domain || host.end_with?(".#{domain}"))
      fail_check("#{label} must be an HTTPS URL on #{domain} or a subdomain of #{domain}.") unless uri.is_a?(URI::HTTPS) && valid_host && !uri.userinfo
    rescue URI::InvalidURIError
      fail_check("#{label} is malformed.")
    end
  end
  request_id = context.fetch("request_id")
  fail_check("request_id contains unsupported characters or is too long.") unless request_id.match?(/\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\z/) && !request_id.include?("..") && !request_id.end_with?(".")
  normalized = request_id.gsub(/[^A-Za-z0-9_-]+/, "-").gsub(/\A[-_]+|[-_]+\z/, "").downcase
  normalized = "request" if normalized.empty?
  digest = Digest::SHA256.hexdigest(request_id)[0, 8]
  expected_branch = "content/substack-#{normalized[0, 48]}-#{digest}"
  fail_check("Temporary branch name is invalid or no longer matches request_id.") unless context["branch_name"] == expected_branch
end

def verify_fetched_integrity!(context, metadata)
  [File.join(ROOT, ".automation"), WORK_DIR, CONTEXT_PATH, METADATA_PATH, File.join(WORK_DIR, "source.html")].each do |path|
    fail_check("Fetched working files must not be symlinks: #{path.delete_prefix(ROOT + File::SEPARATOR)}") if File.symlink?(path)
  end
  {
    "source_html_sha256" => File.join(WORK_DIR, "source.html"),
    "metadata_sha256" => METADATA_PATH,
    "context_sha256" => CONTEXT_PATH,
  }.each do |name, path|
    expected = ENV[name.upcase]
    fail_check("Missing pre-Codex integrity value for #{name}.") if expected.nil? || expected.empty?
    fail_check("Fetched source file changed after retrieval: #{name}.") unless File.file?(path) && Digest::SHA256.file(path).hexdigest == expected
  end
  expected_image = ENV.fetch("LEAD_IMAGE_SHA256", "none")
  image_path = metadata["lead_image_path"]
  fail_check("Fetched metadata has no candidate lead image.") unless image_path.is_a?(String) && !image_path.empty?
  image_absolute = File.expand_path(image_path, ROOT)
  fail_check("Candidate lead image path escapes the temporary source directory.") unless image_absolute.start_with?(WORK_DIR + File::SEPARATOR)
  fail_check("Fetched lead image must not be a symlink.") if File.symlink?(image_absolute)
  fail_check("Fetched candidate lead image changed after retrieval.") unless expected_image != "none" && File.file?(image_absolute) && Digest::SHA256.file(image_absolute).hexdigest == expected_image
  fail_check("Fetched metadata does not preserve the supplied Substack URL.") unless metadata["source_url"] == context.fetch("substack_url")
  fail_check("Fetched HTML path is unexpected.") unless metadata["source_html_path"] == ".automation/substack/source.html"
  fail_check("Fetched metadata path is unexpected.") unless metadata["metadata_path"] == ".automation/substack/metadata.json"
end

def verify_git_remote!
  repository = ENV.fetch("GITHUB_REPOSITORY", "")
  server = ENV.fetch("GITHUB_SERVER_URL", "https://github.com").sub(%r{/+$}, "")
  fail_check("Missing GitHub repository context.") if repository.empty? || repository.include?("\n")
  expected = "#{server}/#{repository}.git".downcase
  fetch_url = git_output("remote", "get-url", "origin").strip.downcase
  push_url = git_output("remote", "get-url", "--push", "origin").strip.downcase
  fail_check("The origin fetch URL changed during Codex execution.") unless fetch_url == expected
  fail_check("The origin push URL changed during Codex execution.") unless push_url == expected
end

def validate!
  context = read_json(CONTEXT_PATH)
  metadata = read_json(METADATA_PATH)
  {
    "substack_url" => "SUBSTACK_URL",
    "linkedin_url" => "LINKEDIN_URL",
    "request_id" => "REQUEST_ID",
  }.each do |key, environment_name|
    fail_check("Temporary workflow context no longer matches the workflow input #{key}.") unless context[key] == ENV.fetch(environment_name, nil)
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
  fail_check("Expected exactly two new article files with the supplied substack_url; found #{new_posts.length}.") unless new_posts.length == 2

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
  fail_check("The source HTML must not be committed.") if changes.any? { |_code, path| path.end_with?(".html") }

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

  metadata_published = metadata["date_published"]
  fail_check("Substack metadata has no reliable publication date; the workflow will not invent one.") if metadata_published.nil? || metadata_published.to_s.empty?
  expected_date = parse_time(metadata_published, "Substack publication date")
  en_date = parse_time(en_data["date"], "English article date")
  pl_date = parse_time(pl_data["date"], "Polish article date")
  fail_check("Both article dates must preserve the Substack publication timestamp.") unless en_date.to_i == expected_date.to_i && pl_date.to_i == expected_date.to_i
  expected_filename_date = expected_date.strftime("%Y-%m-%d")
  [en, pl].each do |post|
    fail_check("Post filename date must match the Substack publication date.") unless File.basename(post[:path])[0, 10] == expected_filename_date
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
    fail_check("#{label} article must preserve the exact supplied substack_url.") unless data["substack_url"] == context.fetch("substack_url")
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
  fail_check("English and Polish articles must share the same approved tags.") unless en_data["tags"].is_a?(Array) && pl_data["tags"].is_a?(Array) && en_data["tags"].sort == pl_data["tags"].sort
  taxonomy = read_yaml(File.join(ROOT, "_data", "taxonomy.yml"))
  approved_tags = Array(taxonomy["tags"])
  tags = Array(en_data["tags"])
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
  fail_check("The article image must preserve the validated Substack lead image bytes.") unless Digest::SHA256.file(image_file).hexdigest == Digest::SHA256.file(fetched_image).hexdigest

  fail_check("If last_modified_at is set, it must be set consistently for both translations.") unless !!en_data["last_modified_at"] == !!pl_data["last_modified_at"]
  if en_data["last_modified_at"] || pl_data["last_modified_at"]
    modified = metadata["date_modified"]
    fail_check("last_modified_at is only allowed when Substack has a real modification timestamp.") if modified.nil? || modified.to_s.empty?
    expected_modified = parse_time(modified, "Substack modification date")
    fail_check("last_modified_at must represent a later source modification.") unless expected_modified > expected_date
    [en_data["last_modified_at"], pl_data["last_modified_at"]].compact.each do |value|
      fail_check("last_modified_at must match Substack's real modification timestamp.") unless parse_time(value, "last_modified_at").to_i == expected_modified.to_i
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
  context.merge!(
    "en_article_path" => en[:path],
    "pl_article_path" => pl[:path],
    "image_path" => image_changes.first,
    "translation_key" => translation_key,
    "english_title" => title,
  )
  File.write(CONTEXT_PATH, JSON.pretty_generate(context) + "\n", mode: "w", encoding: "UTF-8")
  body = <<~BODY
    Automated Substack import

    Substack source URL: #{context.fetch('substack_url')}
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
  File.write(File.join(WORK_DIR, "pr-body.md"), body, mode: "w", encoding: "UTF-8")
  puts "Validated EN/PL article pair, approved tags, exact social destinations, localization mapping, image, and source dates."
  puts "English: #{en[:path]} -> #{en_path}"
  puts "Polish: #{pl[:path]} -> #{pl_path}"
  puts "translation_key: #{translation_key}"
end

def run!(*arguments, environment: {})
  safe_environment = process_environment(environment)
  stdout, stderr, status = Open3.capture3(safe_environment, *arguments, chdir: ROOT)
  print stdout unless stdout.empty?
  fail_check("#{arguments.first} failed: #{stderr.strip}") unless status.success?
end

def git_blob(path)
  stdout, stderr, status = Open3.capture3(process_environment, "git", "show", ":#{path}", chdir: ROOT, binmode: true)
  fail_check("Could not read staged file #{path}: #{stderr}") unless status.success?
  stdout
end

def publish!
  context = read_json(CONTEXT_PATH)
  token = ENV["CONTENT_PR_TOKEN"]
  fail_check("CONTENT_PR_TOKEN is required only for the post-validation publishing step.") if token.nil? || token.empty?
  paths = [context.fetch("en_article_path"), context.fetch("pl_article_path"), context.fetch("image_path"), "_data/localized_pages.yml"]
  fail_check("Git staging area must be empty before the publishing step.") unless git_success?("diff", "--cached", "--quiet")
  run!("git", "config", "user.name", "github-actions[bot]")
  run!("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
  run!("git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "add", "--", *paths)
  run!("git", "diff", "--cached", "--check")
  staged = git_output("diff", "--cached", "--name-only").lines.map(&:chomp).sort
  fail_check("Only validated article, image, and localization files may be staged: #{staged.inspect}") unless staged == paths.sort
  paths.each do |path|
    fail_check("Staged bytes differ from the files that passed validation: #{path}") unless git_blob(path) == File.binread(File.join(ROOT, path))
  end
  git_environment = {
    "GIT_CONFIG_NOSYSTEM" => "1",
    "GIT_CONFIG_GLOBAL" => "/dev/null",
  }
  run!("git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "commit", "-m", "Automated Substack import: #{context.fetch('english_title')}", environment: git_environment)

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
    "--body-file", File.join(WORK_DIR, "pr-body.md"),
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
  fail_check("Usage: ruby _scripts/validate_substack_import.rb {validate|publish}")
end
