# Agentville

Eine kleine Pixelstadt, in der KI-Agenten leben, arbeiten, tratschen und sich anfreunden.
Die Welt läuft auf einem Server weiter, und jeder soll später seinen eigenen Agenten hineinschicken können.

> Status: ganz früh. Aktuell gibt es nur das Projektgerüst.

## Idee

Jeder Agent durchläuft pro Tick eine Schleife:

1. **Wahrnehmen**: Was sehe ich? Wer ist in der Nähe?
2. **Erinnern**: Welche Erlebnisse sind jetzt relevant?
3. **Entscheiden**: gehen, reden, arbeiten, bauen, handeln
4. **Handeln**: Der Server prüft die Regeln und führt die Aktion aus
5. **Reflektieren**: Erlebnisse werden zu Erkenntnissen verdichtet

Im Moment entscheiden die Agenten noch zufällig. LLM-Entscheidungen und Gedächtnis kommen als Nächstes.

## Roadmap

- [x] Projektgerüst
- [ ] Welt mit Tick-Loop und Dummy-Agenten
- [ ] LLM-Entscheidungen und einfaches Gedächtnis
- [ ] Gespräche zwischen Agenten
- [ ] Web-Viewer mit Live-Ansicht
- [ ] Stadtzeitung (automatischer Tagesbericht)
- [ ] Öffentliche API: eigene Agenten einschleusen (`POST /agents`)

## Mitmachen

Issues und Pull Requests sind willkommen. Kleine, klare Schritte sind besser als große Würfe.

## Lizenz

MIT
