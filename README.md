# Obimex Werkplek

Digitale werkplek voor de Obimex-werkplaats (Almelo). Statische web-app — werkt op telefoon, tablet en pc, ook offline op de werkvloer.

## Modules

| Pagina | Wat het doet |
| --- | --- |
| `index.html` | Werkplek-hub: overzicht van alle modules |
| `tellen.html` | Voorraad tellen: lijsten (Brut H-profiel, Almelo Wit, 9005 FS, glas-bonnen), zoeken en barcode/QR-scannen, aantallen invoeren of **wegen** (bea-producten), automatische **afwijkingscontrole** t.o.v. de systeemvoorraad, notities + markeren voor management, foto/dwarsdoorsnede per artikel, oude catalogus (archief), vrije invoer, CSV-export en printen |
| `plattegrond.html` | Interactieve plattegrond: upload de gebouwplattegrond, plaats zones (A–L), koppel artikelen aan zones en tel gericht per gebied |
| `elumatec-werkinstructie.html` | Werkinstructie Elumatec SBZ 122/71 (CNC) |

## Gebruik

Open `index.html` — of deploy de map als statische site (Vercel-configuratie zit erbij in `vercel.json`). Alle telgegevens worden lokaal op het apparaat bewaard (localStorage + IndexedDB); via ⋯ Meer kun je back-ups downloaden/terugzetten en lijsten importeren uit Excel/CSV.
