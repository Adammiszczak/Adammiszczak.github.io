# Extend jekyll-seo-tag's existing BlogPosting entity in place for expert articles.
# Keeping these additions in the SEO tag output avoids emitting a second Article entity.
require "json"

module Jekyll
  class SeoTag::JSONLDDrop
    alias_method :to_json_without_article_details, :to_json
    private :to_json_without_article_details

    def to_json(state = nil)
      data = JSON.parse(to_json_without_article_details(state))
      return data.to_json(state) unless data["@type"] == "BlogPosting"

      page = page_drop.send(:page)
      return data.to_json(state) unless page["section"] == "articles"

      site = page_drop.send(:site)
      canonical_url = page_drop.canonical_url
      data["@id"] = "#{canonical_url}#article" if canonical_url
      data["articleSection"] = page["lang"] == "pl" ? "Artykuły" : "Articles"
      data["inLanguage"] = page["lang"] || site["lang"] || "en"
      data["isAccessibleForFree"] = true
      website_url = site["url"]
      if website_url
        website_url = website_url.sub(%r{/+$}, "")
        data["isPartOf"] = { "@type" => "WebSite", "@id" => "#{website_url}/#website", "name" => site["title"], "url" => website_url }
      end

      tags = Array(page["localized_keywords"] || page["tags"]).compact.map(&:to_s).reject(&:empty?)
      data["keywords"] = tags unless tags.empty?

      author = data["author"]
      if author.is_a?(Hash)
        author_url = author["url"]
        author["@id"] = "#{author_url}#person" if author_url
        social = site["social"]
        social_links = social["links"] if social
        author["sameAs"] = social_links if social_links.is_a?(Array) && !social_links.empty?
        if author["@id"]
          data["publisher"] = { "@id" => author["@id"] }
          data["copyrightHolder"] = { "@id" => author["@id"] }
        end
      end

      image_url = data["image"]
      image_url = image_url["url"] || image_url["path"] if image_url.is_a?(Hash)
      if image_url
        image = { "@type" => "ImageObject", "url" => image_url }
        image["description"] = page["image_alt"] if page["image_alt"]
        image["caption"] = page["image_caption"] if page["image_caption"]
        data["image"] = image
      end

      published = page["date"]
      data["copyrightYear"] = published.year if published.respond_to?(:year)
      data.to_json(state)
    end
  end
end
