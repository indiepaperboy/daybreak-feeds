# daybreak-feeds

The source catalogue for **rss.** (project *Daybreak*) — a section-organised list of
RSS feeds the app offers when you tap **＋ Add a feed**.

- **`catalogue.json`** — the machine-readable catalogue the app fetches, grouped into
  newspaper sections: News, Business, Politics, Technology, Science, Sport, Arts & Culture,
  Books & Literary, Style & Living, and **Local** (feeds tagged by country, e.g. `"AU"`).
- Every feed is **health-checked weekly** by a GitHub Action
  ([`validate.yml`](.github/workflows/validate.yml)): genuinely dead feeds are pruned after
  3 consecutive failures; feeds that merely *block* automated fetches (HTTP 403/429) are kept
  and flagged `"blocked": true`, never auto-removed; feeds marked `"protected": true` are never
  auto-pruned (they're flagged loudly instead).
- Seeded from the CC0 [awesome-rss-feeds](https://github.com/plenaryapp/awesome-rss-feeds)
  list, then validated.

## Contributing
Open a PR adding a feed to the right section in `catalogue.json` — entries are
`{ "title", "url", "site" }` (add `"country"` for Local).

## Licence
[CC0 1.0](LICENSE) — public domain. Take it, fork it, ship it.
