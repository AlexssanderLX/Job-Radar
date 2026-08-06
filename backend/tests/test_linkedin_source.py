from app.sources.linkedin import parse_job_description, parse_search_cards


def test_parses_linkedin_search_card():
    markup = '''
    <div class="base-search-card" data-entity-urn="urn:li:jobPosting:123">
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/123?trk=x"></a>
      <h3 class="base-search-card__title">Backend Developer Júnior</h3>
      <h4 class="base-search-card__subtitle">Acme</h4>
      <span class="job-search-card__location">São Paulo, SP</span>
      <time datetime="2026-08-05"></time>
    </div>'''
    cards = parse_search_cards(markup)
    assert cards == [{
        "id": "123", "title": "Backend Developer Júnior", "company": "Acme",
        "location": "São Paulo, SP", "url": "https://www.linkedin.com/jobs/view/123",
        "date": "2026-08-05",
    }]


def test_parses_linkedin_job_description():
    markup = '<div class="show-more-less-html__markup"><p>Python e Docker</p></div>'
    assert parse_job_description(markup) == "Python e Docker"
