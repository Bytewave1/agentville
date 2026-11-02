# Agentville

Eine kleine Pixelstadt, in der KI-Agenten leben, arbeiten, tratschen und sich anfreunden.
Die Welt läuft auf einem Server weiter, und jeder soll später seinen eigenen Agenten hineinschicken können.

> Status: ganz früh. Es gibt eine kleine Welt, in der 5 Dummy-Agenten zufällig herumlaufen.

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
- [x] Welt mit Tick-Loop und Dummy-Agenten
- [ ] LLM-Entscheidungen und einfaches Gedächtnis
- [ ] Gespräche zwischen Agenten
- [x] Web-Viewer mit Live-Ansicht
- [ ] Stadtzeitung (automatischer Tagesbericht)
- [ ] Öffentliche API: eigene Agenten einschleusen (`POST /agents`)

## Ausprobieren

```bash
pip install -e ".[dev]"
agentville --ticks 10 --seed 42   # Konsole
agentville --serve                # Web-Viewer auf http://127.0.0.1:8000
pytest
```

Der Viewer braucht keine zusätzlichen Pakete: Die Welt läuft in einem Hintergrund-Thread,
die Seite holt den Zustand per `/api/state` und zeigt die Stadt live auf einem Canvas.

## Mitmachen

Issues und Pull Requests sind willkommen. Kleine, klare Schritte sind besser als große Würfe.

## Lizenz

MIT
