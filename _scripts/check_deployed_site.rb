#!/usr/bin/env ruby
# Verify that GitHub Pages serves the same Articles listing and Pagefind assets as the build.
require "cgi"
require "digest"
require "json"
require "net/http"
require "uri"

base_url = ENV.fetch("PAGES_URL")
expected_hrefs = JSON.parse(ENV.fetch("EXPECTED_ARTICLE_HREFS"))
expected_html_sha = ENV.fetch("EXPECTED_ARTICLE_HTML_SHA256")
expected_css_sha = ENV.fetch("EXPECTED_PAGEFIND_CSS_SHA256")
abort("ERROR: expected article URLs are missing from the build diagnostics output.") unless expected_hrefs.is_a?(Array) && !expected_hrefs.empty?

base_uri = URI(base_url)
abort("ERROR: Pages URL must be an HTTPS URL with a host.") unless base_uri.is_a?(URI::HTTPS) && base_uri.host
base_uri.path = "#{base_uri.path.sub(%r!/?\z!, '/')}"
archive_uri = URI.join(base_uri.to_s, "articles/")
run_id = ENV.fetch("GITHUB_RUN_ID", "local")
max_attempts = 12
delay_seconds = 10

def fetch(uri, run_id:, attempt:)
  request_uri = uri.dup
  params = URI.decode_www_form(request_uri.query.to_s)
  params << ["__pages_verify", "#{run_id}-#{attempt}"]
  request_uri.query = URI.encode_www_form(params)
  redirects = 0

  loop do
    request = Net::HTTP::Get.new(request_uri)
    request["Cache-Control"] = "no-cache, no-store, max-age=0"
    request["Pragma"] = "no-cache"
    request["Accept-Encoding"] = "identity"
    response = Net::HTTP.start(request_uri.host, request_uri.port, use_ssl: request_uri.scheme == "https", open_timeout: 10, read_timeout: 25) do |http|
      http.request(request)
    end

    if response.is_a?(Net::HTTPRedirection) && response["location"] && redirects < 5
      request_uri = URI.join(request_uri.to_s, response["location"])
      redirects += 1
      next
    end
    return [request_uri, response]
  end
end

def response_headers(response)
  %w[date server content-type cache-control age etag last-modified expires via x-cache x-served-by x-github-request-id content-encoding].filter_map do |name|
    value = response[name]
    "#{name}=#{value}" if value
  end.join("; ")
end

def article_hrefs(html)
  html.scan(/<article\b[^>]*>.*?<\/article>/im).select do |block|
    block.match?(/\bclass\s*=\s*["'][^"']*\barticle-card\b[^"']*["']/i)
  end.filter_map do |block|
    match = block.match(/<h2\b[^>]*>\s*<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']/im)
    CGI.unescapeHTML(match[1]) if match
  end
end

def asset_urls(html, page_uri)
  tags = html.scan(/<(?:link|script)\b[^>]*>/i)
  tags.filter_map do |tag|
    next unless tag.include?("pagefind-component-ui")

    path = tag[/\b(?:href|src)\s*=\s*["']([^"']+)["']/i, 1]
    URI.join(page_uri.to_s, CGI.unescapeHTML(path)) if path
  end
end

def append_step_summary(lines)
  summary_path = ENV["GITHUB_STEP_SUMMARY"]
  return unless summary_path

  File.open(summary_path, "a") do |file|
    file.puts lines.join("\n")
    file.puts
  end
end

puts "::group::Post-deployment Pages smoke check"
puts "workflow_run=#{run_id} commit=#{ENV.fetch('GITHUB_SHA', 'unknown')}"
puts "pages_url=#{base_uri}"
puts "expected_article_cards=#{expected_hrefs.length}"
puts "expected_article_hrefs=#{expected_hrefs.join(', ')}"
puts "expected_archive_sha256=#{expected_html_sha}"
puts "expected_pagefind_css_sha256=#{expected_css_sha}"
summary_lines = [
  "## Live Pages smoke check",
  "",
  "- Workflow run: `#{run_id}`",
  "- Commit: `#{ENV.fetch('GITHUB_SHA', 'unknown')}`",
  "- Page URL: `#{base_uri}`",
  "- Expected archive SHA-256: `#{expected_html_sha}`",
  "- Expected Pagefind CSS SHA-256: `#{expected_css_sha}`",
  "- Expected article links: #{expected_hrefs.map { |href| "`#{href}`" }.join(', ')}"
]

last_failure = nil
max_attempts.times do |index|
  attempt = index + 1
  attempt_failure = nil
  begin
    final_uri, response = fetch(archive_uri, run_id: run_id, attempt: attempt)
    html = response.body.to_s
    actual_hrefs = article_hrefs(html)
    html_hash = Digest::SHA256.hexdigest(html)
    content_type = response["content-type"].to_s
    stale_empty_state = html.match?(/The first in-depth articles are in preparation\./i)
    archive_hash_matches = html_hash == expected_html_sha

    puts "attempt=#{attempt}/#{max_attempts} archive_status=#{response.code} final_url=#{final_uri} bytes=#{html.bytesize} sha256=#{html_hash} sha_matches_artifact=#{archive_hash_matches} cards=#{actual_hrefs.length} stale_empty_state=#{stale_empty_state} headers=[#{response_headers(response)}]"
    puts "actual_article_hrefs=#{actual_hrefs.join(', ')}"
    summary_lines << "- Attempt #{attempt}: archive HTTP #{response.code}; cards #{actual_hrefs.length}/#{expected_hrefs.length}; archive hash match `#{archive_hash_matches}`; stale empty state `#{stale_empty_state}`; headers: `#{response_headers(response)}`."

    failures = []
    failures << "Articles returned HTTP #{response.code}." unless response.code.to_i == 200
    failures << "Articles response content type was #{content_type.inspect}, expected text/html." unless content_type.include?("text/html")
    failures << "Live Articles HTML SHA-256 differs from the uploaded artifact." unless archive_hash_matches
    failures << "Live Articles response contains the old empty-state message." if stale_empty_state
    if actual_hrefs != expected_hrefs
      failures << "Article links differ from the uploaded build: missing=#{(expected_hrefs - actual_hrefs).inspect}; unexpected=#{(actual_hrefs - expected_hrefs).inspect}."
    end

    urls = asset_urls(html, final_uri)
    css_uri = urls.find { |uri| uri.path.end_with?("pagefind-component-ui.css") }
    js_uri = urls.find { |uri| uri.path.end_with?("pagefind-component-ui.js") }
    unless css_uri && js_uri
      failures << "Live HTML does not reference both Pagefind component assets (css=#{css_uri.inspect}, js=#{js_uri.inspect})."
    else
      if response.code.to_i == 200
        [[:css, css_uri], [:javascript, js_uri]].each do |kind, uri|
          asset_final_uri, asset_response = fetch(uri, run_id: run_id, attempt: attempt)
          asset_hash = Digest::SHA256.hexdigest(asset_response.body.to_s)
          css_hash_matches = kind != :css || asset_hash == expected_css_sha
          puts "asset=#{kind} status=#{asset_response.code} final_url=#{asset_final_uri} bytes=#{asset_response.body.to_s.bytesize} sha256=#{asset_hash} sha_matches_artifact=#{css_hash_matches} headers=[#{response_headers(asset_response)}]"
          summary_lines << "  - #{kind}: HTTP #{asset_response.code}; bytes #{asset_response.body.to_s.bytesize}; hash match `#{css_hash_matches}`; headers: `#{response_headers(asset_response)}`."
          failures << "Pagefind #{kind} returned HTTP #{asset_response.code} at #{asset_final_uri}." unless asset_response.code.to_i == 200
          failures << "Deployed Pagefind CSS content differs from the uploaded build artifact." if kind == :css && !css_hash_matches
        end
      end
    end
    attempt_failure = failures.join(" ") unless failures.empty?
  rescue StandardError => error
    attempt_failure = "Attempt #{attempt} request failed: #{error.class}: #{error.message}"
    puts attempt_failure
    summary_lines << "- Attempt #{attempt}: request error `#{error.class}: #{error.message}`."
  end

  last_failure = attempt_failure
  break if last_failure.nil?

  if attempt < max_attempts
    puts "Waiting #{delay_seconds}s for Pages/CDN propagation before retrying."
    sleep delay_seconds
  end
end

puts "::endgroup::"
if last_failure
  summary_lines << ""
  summary_lines << "**Verification failed:** #{last_failure}"
  append_step_summary(summary_lines)
  puts "::error title=Deployed Pages verification failed::#{last_failure.gsub('%', '%25').gsub("\r", '%0D').gsub("\n", '%0A')}"
  abort(last_failure)
end
summary_lines << ""
summary_lines << "**Verification passed:** deployed archive matches the uploaded build and Pagefind component assets return HTTP 200."
append_step_summary(summary_lines)
puts "Deployed site verification passed: live archive matches the build and Pagefind component assets return HTTP 200."
