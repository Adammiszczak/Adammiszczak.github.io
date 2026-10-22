# Paginate article archives independently from the site's latest-articles homepage.
module ArticleArchivePagination
  class Generator < Jekyll::Generator
    safe true
    priority :lowest

    ARCHIVES = {
      "en" => { "path" => "/articles/", "locale" => "en_US" },
      "pl" => { "path" => "/pl/artykuly/", "locale" => "pl_PL" }
    }.freeze

    def generate(site)
      page_size = site.config.fetch("article_archive_page_size", 4).to_i
      raise "article_archive_page_size must be greater than zero" unless page_size.positive?

      ARCHIVES.each do |lang, archive|
        articles = site.posts.docs
          .select do |post|
            post.data["section"] == "articles" && (post.data["lang"] || "en") == lang
          end
          .sort_by { |post| [post.date, post.url] }
          .reverse

        pages = [((articles.length + page_size - 1) / page_size), 1].max
        archive_page = site.pages.find { |page| page.url == archive["path"] }
        next unless archive_page

        (1..pages).each do |number|
          current = number == 1 ? archive_page : build_page(site, lang, archive, number)
          current.data["article_items"] = articles.slice((number - 1) * page_size, page_size) || []
          current.data["pagination"] = pagination_data(archive["path"], number, pages)
          next if number == 1

          site.pages << current
        end
      end
    end

    private

    def build_page(site, lang, archive, number)
      base_path = archive["path"].sub(%r{/$}, "")
      path = "#{base_path}/page#{number}/"
      page = Jekyll::PageWithoutAFile.new(site, site.source, path.sub(%r{^/|/$}, ""), "index.html")
      page.data.merge!(
        "layout" => "article-archive",
        "lang" => lang,
        "locale" => archive["locale"],
        "permalink" => path,
        "title" => archive_title(lang, number),
        "description" => archive_description(lang),
        "archive_heading" => archive_heading(lang, number),
        "archive_intro" => archive_intro(lang),
        "archive_footer" => archive_footer(lang)
      )
      page
    end

    def pagination_data(base_path, current, total)
      base = base_path.sub(%r{/$}, "")
      page_url = ->(number) { number == 1 ? base_path : "#{base}/page#{number}/" }
      {
        "current_page" => current,
        "total_pages" => total,
        "previous_url" => current > 1 ? page_url.call(current - 1) : nil,
        "next_url" => current < total ? page_url.call(current + 1) : nil,
        "pages" => (1..total).map do |number|
          { "number" => number, "url" => page_url.call(number), "current" => number == current }
        end
      }
    end

    def archive_title(lang, number)
      lang == "pl" ? "Artykuły i analizy: strona #{number}" : "Articles and research: page #{number}"
    end

    def archive_heading(lang, number)
      lang == "pl" ? "Artykuły i analizy: strona #{number}" : "Articles and research: page #{number}"
    end

    def archive_description(lang)
      lang == "pl" ? "Praktyczne analizy dotyczące SEO e-commerce, odkrywania produktów, GEO i AI Search." : "Practical analysis of international e-commerce SEO, product discovery, GEO and AI Search."
    end

    def archive_intro(lang)
      lang == "pl" ? "Praktyczne analizy dotyczące SEO w międzynarodowym e-commerce, odkrywania produktów, GEO, AI Search oraz automatyzacji procesów z agentami AI." : "Practical analysis of international e-commerce SEO, product discovery, GEO, AI Search and agentic automation."
    end

    def archive_footer(lang)
      if lang == "pl"
        "Krótsze aktualizacje publikuję na <a href=\"https://www.linkedin.com/in/adam-miszczak/\">LinkedIn</a> i <a href=\"https://substack.com/@adammiszczak\">Substacku</a>."
      else
        "For shorter updates, follow me on <a href=\"https://www.linkedin.com/in/adam-miszczak/\">LinkedIn</a> or <a href=\"https://substack.com/@adammiszczak\">Substack</a>."
      end
    end
  end
end
