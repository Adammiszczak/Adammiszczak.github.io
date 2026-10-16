---
layout: article
lang: pl
locale: pl_PL
translation_key: chatgpt_referral_attribution
title: "Spadek ruchu z ChatGPT? Najpierw sprawdź atrybucję"
date: "2026-10-15 16:00:00 +0000"
last_modified_at: "2026-10-16 16:00:00 +0000"
description: "Spadek ruchu z ChatGPT może wynikać z braku atrybucji, a nie utraty wizyt. Co październikowy problem z UTM i wdrażana poprawka oznaczają dla raportowania w dużej organizacji."
section: articles
categories:
  - articles
permalink: /pl/artykuly/atrybucja-ruchu-chatgpt-powrot-utm
tags:
  - ecommerce-seo
  - geo
  - ai-search
localized_keywords:
  - ruch z ChatGPT
  - atrybucja ruchu
  - UTM
  - SEO e-commerce
  - GEO
image:
  path: /assets/img/articles/cedric-huesler-fix.jpg
  alt: "Wykres Cedrica Hueslera pokazujący spadek wizyt przypisanych do ChatGPT, gdy wizyty bez tagu UTM trafiały do kanału Direct."
image_alt: "Wykres Cedrica Hueslera pokazujący spadek wizyt przypisanych do ChatGPT, gdy wizyty bez tagu UTM trafiały do kanału Direct."
image_caption: "Źródło: Cedric Huesler, dane telemetryczne Adobe Brand Visibility. Wykres wskazuje próbę około 500 stron i określa porównanie jako kierunkowe."
linkedin_url: "https://www.linkedin.com/feed/update/urn:li:activity:7516785204255125505/"
substack_url: "https://substack.com/@adammiszczak/note/c-362349160"
author:
  name: Adam Miszczak
  url: https://adammiszczak.github.io/pl/o-mnie/
---

{% capture update_note %}
**Aktualizacja · 16 października 2026:** 15 października OpenAI rozpoczęło wdrażanie poprawki przywracającej tag `utm_source` w linkach z ChatGPT. Cedric Huesler podał, że do 9:00 czasu pacyficznego 16 października liczba otagowanych kliknięć wróciła do około 95–100% poziomu z tej samej godziny tydzień wcześniej - w danych telemetrycznych obejmujących tysiące domen. Większość kliknięć z ChatGPT nadal nie miała referrera, dlatego sprawdź własne dane. Poprawka przywraca atrybucję przyszłych wizyt, ale nie odtworzy informacji, których wcześniej nie zarejestrowano. [Przeczytaj aktualizację na LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7516785204255125505/) lub [notatkę na Substack](https://substack.com/@adammiszczak/note/c-362349160).
{% endcapture %}
{% include article-callout.html type="update" label="Aktualizacja · 16 października 2026" title="Trwa wdrażanie poprawki tagów UTM" content=update_note %}

Nagły spadek raportowanych wejść z ChatGPT sam w sobie nie dowodzi pogorszenia wyników SEO ani GEO. W październiku 2026 r. linki wychodzące z ChatGPT tymczasowo przestały zawierać tag `utm_source=chatgpt.com`. Gdy brakowało zarówno tagu, jak i referrera, narzędzia analityczne mogły klasyfikować takie wizyty jako Direct, mimo że użytkownicy nadal przechodzili z ChatGPT.

## Co pokazywały wstępne dane

W swojej pierwotnej analizie [Cedric Huesler](https://www.linkedin.com/in/cedrichuesler/) odnotował około 31 tys. mniej wizyt dziennie przypisanych do ChatGPT i jednocześnie 26 tys. dodatkowych wizyt Direct w tej samej próbie około 500 stron. Podał też, że dwie trzecie stron, na których spadły wizyty przypisane do ChatGPT, odnotowało wzrost ruchu Direct. Obserwacje te wspierają hipotezę o utracie atrybucji, ale nie dowodzą, że każda brakująca w raporcie wizyta z ChatGPT trafiła do Direct ani że problem dotyczył każdego doświadczenia ChatGPT.

W późniejszej aktualizacji Cedric wskazał na prawdopodobny błąd produktu: około 8 października GPT-6 przestał dodawać tag UTM, a przed rozpoczęciem wdrażania poprawki 15 października OpenAI potwierdziło znany problem. W aktualizacji z 16 października Cedric podał, że otagowane kliknięcia wróciły do około 95–100% poziomu z tej samej godziny tydzień wcześniej w danych z tysięcy domen. Zaznaczył też, że większość kliknięć z ChatGPT nadal nie miała referrera. To pomiary z jego telemetrii wykonane w konkretnym czasie, a nie gwarancja pełnego przywrócenia atrybucji we wszystkich serwisach.

Osobne dane przedstawił Ivan Slobodin z Searchable. W aktualizacji z 15 października wykres oparty na połączeniu Searchable dla 242 witryn pokazywał wzrost liczby otagowanych wizyt w ciągu dnia, ale o 14:00 czasu pacyficznego wynik nadal był o 27% niższy od typowego poziomu. Inny procent i inna pora odzwierciedlają osobną próbę i pomiar. Nie należy łączyć tych liczb w jeden globalny szacunek.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/ivan-slobodin-fix.jpg' | relative_url }}" alt="Wykres Searchable udostępniony przez Ivana Slobodina pokazujący rozpoczęte 15 października odbudowywanie ruchu ChatGPT z tagami UTM; o 14:00 czasu pacyficznego wynik pozostawał 27% poniżej typowego poziomu." loading="lazy">
  <figcaption>Źródło: Ivan Slobodin, połączenie Searchable LLM traffic connector; 242 witryny, październik 2026. Odczyt z 14:00 czasu pacyficznego to pomiar w konkretnym momencie.</figcaption>
</figure>

## Dlaczego to rozróżnienie ma znaczenie

Tagi UTM i referrer to odrębne sygnały atrybucji. Referrer może wskazać źródło wejścia, nawet gdy brakuje tagu kampanii. Jeśli nie ma ani jednego, ani drugiego sygnału i nie istnieje inna użyteczna informacja, wizyta może trafić do kanału Direct. Z kolei dodanie lub przywrócenie tagów UTM przez dostawcę może zwiększyć raportowany ruch AI bez wzrostu liczby samych wizyt.

Osobną kwestią jest klasyfikacja. Nawet jeśli źródło i medium zostały zarejestrowane, wizyta może trafić do niewłaściwego kanału analitycznego, jeśli wewnętrzne reguły nie rozpoznają nowej kombinacji. Wykrywanie źródła i przypisanie go do kanału wymagają osobnych kontroli.

Podobny przypadek już się zdarzył: w maju 2025 r. Ahrefs opisał wejścia z Google AI Mode bez referrera, a następnie poinformował o naprawieniu problemu. Zmiana w atrybucji po stronie dostawcy może wyglądać jak trend widoczności, dopóki zespół nie sprawdzi sygnałów stojących za raportem.

## Proces monitorowania dla dużych organizacji

W dużych serwisach e-commerce porównuj zmiany źródła i medium poszczególnych dostawców z ruchem Direct i łączną liczbą wizyt na tych samych stronach docelowych. Analizuj osobno rynki, urządzenia i typy stron, by różnice nie zniknęły w sumie dla całego serwisu. Obserwuj nowe i brakujące wartości UTM, zmiany referrera, przekierowania, działanie zgód oraz nieoczekiwane przypisania do kanałów.

Gdy pojawi się przerwa w raportowaniu, wykonaj testowe przejścia i sprawdź całą ścieżkę do strony docelowej. Oznacz w raportach daty objęte problemem i potwierdź powrót atrybucji we własnych danych, zanim zmienisz budżety lub przypiszesz zmianę wynikom SEO/GEO. W tym przypadku Huesler zalecił oznaczenie okresu 8–15 października, porównanie tych samych stron i nieprzebudowywanie modelu atrybucji z powodu tymczasowego błędu tagowania. Przywrócone tagi mogą poprawić przyszłą atrybucję, ale nie odtworzą źródła, którego nie zapisano. Ewentualne uzupełnienia i szacunki należy wyraźnie oznaczyć.

Ta zasada dotyczy nie tylko ChatGPT: monitoruj sygnały atrybucji dla wszystkich istotnych dostawców AI i wyszukiwarek, a nie tylko wykresy, które z nich powstają. Tymczasowy błąd może zniknąć. Proces monitorowania powinien pozostać.

## Źródła i autorstwo grafik

To analiza i synteza Adama Miszczaka na podstawie poniższych źródeł. Obserwowane wskaźniki i chronologia incydentu są przypisane ich autorom oraz konkretnym próbom. Grafiki opatrzono źródłami w podpisach: pierwsza przedstawia telemetrię Adobe Brand Visibility Cedrica Hueslera, a druga wykres Searchable Ivana Slobodina.

- [Pierwotna analiza Cedrica Hueslera](https://www.linkedin.com/posts/cedrichuesler_chatgpt-didnt-stop-sending-visitors-it-share-7515970264514400256-RRow/)
- [Aktualizacja Cedrica Hueslera o poprawce](https://lnkd.in/p/dt-6Rh65)
- [Pierwotny wpis Adama Miszczaka na LinkedIn](https://lnkd.in/p/dYnN6vfP)
- [Aktualizacja Adama Miszczaka na LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7516785204255125505/)
- [Aktualizacja Ivana Slobodina z Searchable](https://lnkd.in/p/dyZP2Emd)
- [Ahrefs o problemie z referrerem w Google AI Mode](https://lnkd.in/dB7be8fT)
