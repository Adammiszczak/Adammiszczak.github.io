---
layout: article
lang: pl
locale: pl_PL
translation_key: google_live_deep_dive
title: "Google Search Central Live Barcelona: 10 pytań o SEO i AI Search"
date: 2026-10-15
description: "Dziesięć pytań z Google Search Central Live Barcelona zestawionych z dokumentacją Google o AI Search, danych produktowych, crawlowaniu i pomiarze."
section: articles
categories:
  - articles
permalink: /pl/artykuly/google-search-central-live-barcelona-10-pytan-seo-ai-search
tags:
  - technical-seo
  - ecommerce-seo
  - geo
  - ai-search
  - google-merchant-center
localized_keywords:
  - SEO techniczne
  - SEO e-commerce
  - GEO
  - AI Search
  - Google Merchant Center
image:
  path: /assets/img/articles/google-search-central-live-deep-dive-barcelona-2026.jpg
  alt: "Ekran Slido podczas Google Search Central Live Deep Dive Europe 2026 w Barcelonie z pytaniami o AI Search, wyszukiwanie lokalne i aktualność danych produktowych w e-commerce."
image_alt: "Ekran Slido podczas Google Search Central Live Deep Dive Europe 2026 w Barcelonie z pytaniami o AI Search, wyszukiwanie lokalne i aktualność danych produktowych w e-commerce."
image_caption: "Pytania z sesji Slido podczas Google Search Central Live Deep Dive Europe 2026."
linkedin_url: "https://lnkd.in/p/disgpEvQ"
substack_url: "https://substack.com/@adammiszczak/note/c-354362248"
author:
  name: Adam Miszczak
  url: https://adammiszczak.github.io/pl/o-mnie/
---

Google Search Central Live Deep Dive Europe 2026 w Barcelonie był świetną okazją do rozmów z osobami pracującymi na co dzień nad wyszukiwarką Google. Cieszę się, że mogłem zadać bezpośrednie pytania członkom zespołu Search, w tym Johnowi Muellerowi i Gary’emu Illyesowi, oraz posłuchać dyskusji o tematach ważnych dla e-commerce.

Kilka moich pytań zadanych przez Slido pojawiło się wysoko na ekranie. Prowadzący przypomnieli, by dać szansę także innym uczestnikom, a w sali pojawił się żart: „Adam, bez kolejnych pytań!”. To był sympatyczny moment podczas spotkania pełnego ciekawych rozmów.

Poniżej wracam do dziesięciu pytań z wydarzenia i zestawiam je z opublikowaną dokumentacją Google oraz dyskusją na scenie. Wypowiedź lub wyjaśnienie podczas wydarzenia nie oznacza zobowiązania do wprowadzenia produktu. Jeśli Google nie opisało konkretnej odpowiedzi lub mechanizmu w dokumentacji, zaznaczam to zamiast wyciągać wnioski bez podstaw.

## 1. Pomiar widoczności w funkcjach AI

**Czy Search Console API lub eksport zbiorczy do BigQuery otrzyma osobne wymiary dla AI Overviews lub zapytań wieloetapowych?**

Google udostępniło już w Search Console [dedykowany raport skuteczności funkcji generatywnej AI](https://support.google.com/webmasters/answer/16984139?hl=en). Według Google 31 sierpnia 2026 r. raport był dostępny dla witryn na całym świecie. Pokazuje wyświetlenia w AI Overviews i AI Mode z podziałem na stronę, kraj, datę i urządzenie. Dane z wykresu i tabeli można eksportować. Dokumentacja tego raportu nie opisuje kliknięć ani wymiaru zapytania.

Dokumentacja [Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) nadal opisuje ogólne wymiary Search Console, w tym zapytanie, ale nie wymienia osobnego wymiaru dla AI Overviews, AI Mode ani konwersacji wieloetapowych. Dokumentacja [eksportu zbiorczego Search Console do BigQuery](https://support.google.com/webmasters/answer/12917675?hl=en) oraz [tabel i pól](https://support.google.com/webmasters/answer/12917991?hl=en) opisuje bieżący eksport danych Search Console; nie dokumentuje osobnego zbioru danych dla funkcji AI ani zapytań wieloetapowych. To stan opublikowanej dokumentacji, a nie twierdzenie, że Google nigdy nie doda takich danych.

Podczas wydarzenia Google mówiło o trudnościach z przypisywaniem konwersacyjnych próśb do tradycyjnych słów kluczowych oraz o równoważeniu użyteczności raportów z ochroną prywatności. W zespołach enterprise warto wykorzystać raport do analizy wyświetleń i stron w zakresie, który dokumentuje, a następnie połączyć te dane z zaangażowaniem i wynikami biznesowymi mierzonymi w analityce własnej.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-search-central-live-deep-dive-ai-search-console-question.jpg' | relative_url }}" alt="Ekran Slido podczas Google Search Central Live Deep Dive. Adam Miszczak pyta o wymiary dotyczące AI Overviews i zapytań wieloetapowych w Search Console API oraz eksporcie do BigQuery." loading="lazy">
  <figcaption>Pytanie o pomiar doświadczeń AI Search w Search Console i eksporcie zbiorczym.</figcaption>
</figure>

## 2. Rola SEO e-commerce w zmieniającej się ścieżce zakupowej

**Jaką rolę będzie odgrywać SEO e-commerce, gdy Google coraz więcej etapów odkrywania i oceny produktów obsługuje we własnym ekosystemie?**

Wytyczne Google dotyczące [funkcji generatywnej AI w wyszukiwarce](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) zalecają dalsze stosowanie podstawowych zasad SEO: czytelną strukturę techniczną i unikalne, pomocne treści. Strona nadal musi być zaindeksowana i kwalifikować się do wyświetlenia fragmentu, aby mogła pojawić się w generatywnych funkcjach wyszukiwania Google. Dokumentacja nie mówi, że SEO e-commerce traci znaczenie ani nie przewiduje, że całe odkrywanie produktów przeniesie się do Google.

Dla międzynarodowego e-commerce zadania pozostają konkretne: zapewnić dostępność ważnych stron produktów i kategorii, dbać o poprawność informacji o produktach dla poszczególnych rynków oraz mierzyć wpływ widoczności w wyszukiwarce na wartościowe wizyty i konwersje. [Dokumentacja funkcji AI](https://developers.google.com/search/docs/appearance/ai-features) mówi również, że AI Overviews i AI Mode nie wymagają specjalnych rozwiązań technicznych ani osobnego oznaczenia Schema.org.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-search-central-live-deep-dive-ecommerce-seo-question.jpg' | relative_url }}" alt="Ekran Slido podczas Google Search Central Live Deep Dive z pytaniem o długoterminową rolę SEO e-commerce, gdy Google obsługuje coraz większą część ścieżki zakupowej." loading="lazy">
  <figcaption>Pytanie o rolę SEO e-commerce w zmieniającej się ścieżce odkrywania produktów.</figcaption>
</figure>

## 3. Oddzielne mechanizmy kontroli crawlerów AI

**Czy właściciele witryn będą mogli zarządzać dostępem AI oddzielnie dla poszczególnych crawlerów, takich jak GPTBot?**

Dokumentacja crawlerów Google wyjaśnia, że ustawienia crawlowania dla Googlebota wpływają na wyszukiwarkę Google i jej funkcje. Google nie opisało osobnego user agenta Google Search dla AI Overviews lub AI Mode w [dokumentacji wspólnych crawlerów](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers).

Istnieje osobne, dostępne na poziomie usługi [ustawienie dotyczące generatywnej AI w Search Console](https://support.google.com/webmasters/answer/16908024?hl=en). Do 31 sierpnia 2026 r. Google udostępniło je na całym świecie. Właściciele witryn mogą w nim zezwolić na użycie linków i treści w generatywnych funkcjach wyszukiwarki lub je wyłączyć. Google podaje, że ustawienie nie wpływa na inne części wyszukiwarki jako sygnał rankingowy lub warunek uwzględnienia i nie steruje trenowaniem modeli.

To inne zastosowanie niż <code>Google-Extended</code>. Według [listy crawlerów Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended) Google-Extended jest tokenem kontroli w pliku <code>robots.txt</code>, a nie osobnym user agentem HTTP. Dotyczy wykorzystania pobranych treści do trenowania i uziemiania odpowiedzi Gemini, ale nie wpływa na uwzględnienie ani pozycję w Google Search. Nie należy utożsamiać trzech odrębnych kwestii: obecności w funkcjach AI Google Search, wykorzystania treści w Gemini i crawlowania przez Googlebota.

## 4. Dane uporządkowane i pewność co do encji

**Czy rozbudowane właściwości Schema.org pomagają systemom AI zrozumieć relacje między encjami, jeśli nie prowadzą do wyniku z elementami rozszerzonymi?**

Aktualne [wytyczne Google dotyczące AI Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) są jednoznaczne: dane uporządkowane nie są wymagane dla generatywnych funkcji AI i nie ma osobnego oznaczenia Schema.org przeznaczonego dla AI Overviews lub AI Mode. Dane uporządkowane pomagają Google interpretować treść strony i mogą kwalifikować ją do obsługiwanych wyników z elementami rozszerzonymi, zgodnie z [wprowadzeniem do danych uporządkowanych](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data).

Podczas dyskusji o danych strukturalnych prelegenci opisywali je jako jedno ze źródeł przetwarzanych przez systemy Google oraz wspominali o ekstrakcji i kontroli jakości informacji wykorzystywanych przez funkcje AI. To przydatny kontekst, ale nie opublikowany wskaźnik pewności encji ani obietnica, że dodanie kolejnych właściwości poprawi pobieranie danych lub cytowania. Publiczna dokumentacja Google nie opisuje takiego wzoru. Warto stosować konkretne, poprawne oznaczenia dla obsługiwanych funkcji wyszukiwania i jasnego opisu faktów, zamiast dodawać właściwości spekulacyjnie jako taktykę GEO.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-search-central-live-deep-dive-schema-ai-retrieval-question.jpg' | relative_url }}" alt="Ekran Slido podczas Google Search Central Live Deep Dive z pytaniem Adama Miszczaka o właściwości Schema.org i pewność encji w systemach AI." loading="lazy">
  <figcaption>Pytanie o dane uporządkowane poza kwalifikacją do wyników z elementami rozszerzonymi.</figcaption>
</figure>

## 5. Aktualne stany magazynowe i ceny

**Jak platformy e-commerce mogą przekazywać aktualizacje cen i dostępności tak, aby AI Mode i AI Overviews uwzględniały bieżące dane o produktach?**

Google udostępnia mechanizmy przesyłania i aktualizowania danych produktowych przez [Merchant Center i Merchant API](https://developers.google.com/merchant/api/guides/products/overview). Merchant Center może również odczytywać dane ze stron produktów i automatycznie aktualizować wybrane wartości, gdy nie zgadzają się one z przesłanymi danymi. Dotyczy to między innymi ceny i dostępności. Google podkreśla, że [automatyczne aktualizacje produktów](https://support.google.com/merchants/answer/12157888?hl=en) nie zastępują regularnego przesyłania danych.

Te narzędzia pomagają dbać o jakość danych produktowych, ale opublikowana dokumentacja Google nie obiecuje, że każda zmiana ceny lub stanu magazynowego zostanie natychmiast uwzględniona w AI Overviews lub AI Mode ani nie określa czasu odświeżenia dla tych funkcji. W dużym katalogu najlepiej utrzymywać zgodność katalogu źródłowego, przesyłanego feedu i informacji widocznych na stronie produktu, monitorować rozbieżności oraz aktualizować dane za pomocą obsługiwanych mechanizmów. To zalecenie dotyczące jakości danych, a nie gwarancja czasu ich odświeżenia przez Google.

## 6. Dyrektywy sterujące fragmentami i prezentacją AI

**Czy <code>max-snippet:-1</code> i <code>max-image-preview:large</code> dają przewagę wizualną w AI Overviews w porównaniu z domyślnymi ustawieniami fragmentu?**

Dokumentacja Google dotycząca [meta tagów robots](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) mówi, że <code>max-snippet:-1</code> pozwala Google samodzielnie dobrać długość fragmentu tekstu, którą uzna za najbardziej przydatną. Dokumentacja wyjaśnia też, że <code>max-snippet</code> ma zastosowanie do AI Overviews i AI Mode oraz ogranicza ilość treści, której te funkcje mogą użyć bezpośrednio.

<code>max-image-preview:large</code> zezwala na duży podgląd obrazu, nawet na szerokość widocznego obszaru, w typach wyników wymienionych w dokumentacji. Nie wymienia ona AI Overviews ani AI Mode w kontekście tej dyrektywy. Google nie twierdzi, że dyrektywa poprawia pozycję, gwarantuje obraz w AI Overview lub daje stronie przewagę wizualną. To ustawienia dotyczące zakresu podglądu, a nie przełączniki zapewniające lepszą ekspozycję.

## 7. Dane Merchant Center a odkrywanie produktów w AI Search

**Czy poza bezpłatnymi informacjami o produktach atrybuty Google Merchant Center wpływają na pobieranie lub źródła odpowiedzi w AI Mode i AI Overviews?**

W [wytycznych dotyczących generatywnej AI](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) Google podaje, że feedy Merchant Center mogą pomóc produktom pojawiać się w odpowiedziach AI i innych wynikach wyszukiwania. Google opisało też konwersacyjne atrybuty produktów w Merchant Center, w tym [pytania i odpowiedzi](https://support.google.com/merchants/answer/17085211?hl=en), [odnośniki do dokumentów](https://support.google.com/merchants/answer/17084656?hl=en), powiązane produkty i ranking popularności. [Specyfikacja danych produktowych](https://support.google.com/merchants/answer/7052112?hl=en) wskazuje, że część tych atrybutów służy między innymi doświadczeniom konwersacyjnym, takim jak AI Mode.

Dokumentacja potwierdza rolę danych Merchant Center w odkrywaniu produktów, ale nie ujawnia, jak poszczególne atrybuty feedu są ważone przy pobieraniu informacji, ustalaniu kolejności ani cytowaniu źródeł. [Wytyczne Google dla danych strukturalnych Product](https://developers.google.com/search/docs/appearance/structured-data/product) zalecają korzystanie zarówno z feedów Merchant Center, jak i danych strukturalnych na stronie produktu. Pomaga to zwiększyć kwalifikację do funkcji zakupowych i wspiera Google w rozumieniu oraz weryfikowaniu informacji o produktach.

W praktyce feed, oznaczenia Product i treść widoczna na stronie powinny przedstawiać te same fakty o produkcie. To model pracy nad danymi w dużym e-commerce, a nie formuła Google łącząca feed z cytowaniami.

## 8. Zgodność danych strukturalnych z treścią strony

**Czy właściwości Schema.org muszą być widoczne na stronie, aby systemy AI im ufały, i jak sprawdzać, co odczytują crawlery?**

Google w [politykach dotyczących danych strukturalnych](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) zabrania oznaczania treści niewidocznych dla czytelników i wymaga, aby dane strukturalne rzetelnie przedstawiały treść strony. To zasada jakości, a nie osobny test oceniający wiarygodność ukrytych właściwości w systemach AI.

Podczas wydarzenia Google opisywało dane strukturalne jako część szerszego procesu ekstrakcji i kontroli jakości, a nie jako treść kopiowaną bezpośrednio z JSON-LD do promptu AI. W praktyce warto porównywać oznaczenia z informacjami widocznymi na stronie, używać [Rich Results Test](https://search.google.com/test/rich-results) dla obsługiwanych typów wyników oraz [inspekcji adresu URL](https://support.google.com/webmasters/answer/9012289?hl=en), aby sprawdzić dostęp i indeksowanie przez Google. Pomyślny test nie gwarantuje cytowania przez AI ani określonego wyglądu wyniku wyszukiwania.

## 9. Tekst alternatywny i oznaczanie obrazów AI

**Czy dodanie określenia „wygenerowany przez AI” do tekstu alternatywnego pomaga, czy odciąga uwagę od tego, co faktycznie przedstawia obraz? Czy pochodzenie obrazu lepiej opisać gdzie indziej?**

Wytyczne Google dotyczące [SEO obrazów](https://developers.google.com/search/docs/appearance/google-images) zalecają zwięzły tekst alternatywny opisujący temat obrazu w kontekście strony. Google nie wskazuje określenia „wygenerowany przez AI” jako ogólnego błędu w tekście alternatywnym. Tekst alternatywny opisuje obraz, a nie pełni funkcji uniwersalnego pola pochodzenia. Warto uwzględnić tę informację tylko wtedy, gdy pomaga zrozumieć obraz.

Dla danych produktowych w Merchant Center Google określa osobne mechanizmy dotyczące pochodzenia: obrazy produktów wygenerowane przez AI wymagają odpowiednich metadanych IPTC <code>DigitalSourceType</code>, a tytuły i opisy produktów wygenerowane przez AI używają atrybutów <code>structured_title</code> i <code>structured_description</code>. Szczegóły opisują [wymagania Google dotyczące treści wygenerowanych przez AI](https://support.google.com/merchants/answer/14743464?hl=en). Nie należy mylić tych wymogów dla Merchant Center z tworzeniem dostępnego tekstu alternatywnego do obrazu na stronie.

## 10. Lokalne informacje w podsumowaniach AI

**Na jakich sygnałach powinny skupić się lokalne zespoły SEO, gdy podsumowania AI korzystają z informacji z Profilu Firmy w Google i opinii klientów?**

Google informuje, że [Profile Firmy w Google mogą pomagać lokalnym firmom pojawiać się w odpowiedziach AI](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). Opublikowane [wytyczne dotyczące lokalnego rankingu](https://support.google.com/business/answer/7091?hl=en) opisują wyniki lokalne przez trafność, odległość i rozpoznawalność. Zalecają uzupełnianie informacji o firmie, aby poprawić trafność, a także wskazują, że linki, liczba opinii i pozytywne oceny mogą wpływać na rozpoznawalność.

To udokumentowane zasady lokalnego wyszukiwania, a nie formuła podsumowań AI. Google nie opublikowało oddzielnej listy sygnałów AI dla wyników lokalnych ani modelu wag określającego, jak opinie wpływają na konkretne podsumowanie. Utrzymuj aktualny Profil Firmy w Google i spójne informacje o firmie na stronie, a zmiany widoczności lokalnej traktuj jako dane do analizy, nie dowód działania konkretnego sygnału AI.

## Co łączy te pytania?

W SEO technicznym, międzynarodowym SEO e-commerce, GEO i AI Search powracają cztery tematy: **pomiar, kontrola, jakość danych produktowych i weryfikacja**. Dokumentacja Google daje właścicielom witryn więcej bezpośrednich sposobów mierzenia wyświetleń w funkcjach AI i zarządzania uwzględnieniem treści, a jednocześnie nadal wskazuje na znaczenie stron dostępnych dla crawlerów i przydatnych użytkownikom oraz poprawnych informacji o firmach i produktach.

W dużych platformach e-commerce warto zadbać o spójne dane produktowe w feedach, danych strukturalnych i treści widocznej na stronach; jasny podział odpowiedzialności za aktualizacje cen i dostępności; oraz pomiar powiązany z wartościowymi wizytami i konwersjami. To praktyczna podstawa odkrywania produktów w różnych obszarach Google Search, a nie obietnica, że konkretne pole feedu, właściwość Schema.org lub dyrektywa podglądu zapewni wyższe pozycje czy cytowania.

Z Barcelony wróciłem z kolejnymi pytaniami i dużym uznaniem dla społeczności Search Central. Bezpośrednie rozmowy pomagają przekładać szerokie dyskusje o AI Search na konkretne hipotezy, które mogą testować zespoły SEO, produktowe i inżynieryjne.

