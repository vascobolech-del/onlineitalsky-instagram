# Online Italsky – automatické příspěvky na Instagram

Každý den kolem 18:00 (Praha) se samo spustí `scripts/publish.py`. Pokud v souboru `prispevky.json` nastal termín dalšího příspěvku, zveřejní ho na @onlineitalsky a zapíše do `odeslano.json`.

## Jednorázové nastavení
1. **Settings → Secrets and variables → Actions → New repository secret**: název `IG_TOKEN`, hodnota = token systémového uživatele z Meta Business (platnost „Nikdy“).
2. **Actions → Instagram – Online Italsky → Run workflow → režim `test`**: ověří token, účet a dostupnost obrázků. Nic nezveřejní.
3. Hotovo. Od prvního termínu to běží samo.

## Běžné úpravy
- **Změnit text nebo termín:** upravte příslušný řádek v `prispevky.json` (termín ve tvaru `2027-03-09 18:00`).
- **Vyměnit obrázek:** nahrajte nový JPEG 1080×1350 se stejným názvem do složky `feed/`.
- **Pozastavit:** Actions → Instagram – Online Italsky → ⋯ → Disable workflow.
- **Zveřejnit další příspěvek hned:** Run workflow → režim `publikovat-ted`.

## Pojistky
- Nejvýš jeden příspěvek denně. Když se nějaký termín zmešká (např. kvůli neplatnému tokenu), doběhne další den.
- Před zveřejněním se kontroluje, že stejný příspěvek už na profilu není.
- Když se zveřejnění nepovede, běh skončí chybou a GitHub pošle e-mail.
- Repozitář musí zůstat **Public**: Instagram si obrázky stahuje z veřejné adresy.

## Rozpis
| # | Termín (18:00) | Příspěvek |
|---|---|---|
| 1 | út 17.11.2026 | LA CHIAVE |
| 2 | st 25.11.2026 | BOH |
| 3 | čt 03.12.2026 | PESCE / PESCHE |
| 4 | pá 11.12.2026 | MAGARI! |
| 5 | út 15.12.2026 | GLI GNOCCHI |
| 6 | st 23.12.2026 | MA DAI! |
| 7 | st 30.12.2026 | NONO / NONNO |
| 8 | pá 08.01.2027 | SONO ALLA FRUTTA |
| 9 | út 12.01.2027 | E / È |
| 10 | st 20.01.2027 | MI DAI UNA MANO? |
| 11 | čt 28.01.2027 | UN PO’ |
| 12 | pá 05.02.2027 | UN PESCE FUOR D’ACQUA |
| 13 | út 09.02.2027 | LA MANO |
| 14 | st 17.02.2027 | MEGLIO TARDI CHE MAI |
| 15 | čt 25.02.2027 | DUE CAFFÈ |
| 16 | pá 05.03.2027 | CIOÈ |
| 17 | út 09.03.2027 | VECCHIO AMICO / AMICO VECCHIO |
| 18 | st 17.03.2027 | FIGURATI! |
| 19 | čt 25.03.2027 | BRAVA! |
| 20 | pá 02.04.2027 | PUÒ RIPETERE, PER FAVORE? |
| 21 | út 06.04.2027 | BELLISSIMO |
| 22 | st 14.04.2027 | DA PORTARE VIA |
| 23 | čt 22.04.2027 | QUALCHE GIORNO |
| 24 | pá 30.04.2027 | COSA CI CONSIGLIA? |
| 25 | út 04.05.2027 | A ROMA / IN ITALIA |
| 26 | st 12.05.2027 | BASTA COSÌ, GRAZIE. |
| 27 | čt 20.05.2027 | LUNEDÌ / IL LUNEDÌ |
| 28 | pá 28.05.2027 | POSSO ANDARCI A PIEDI? |
| 29 | út 01.06.2027 | SONO LE SEI E MEZZO. |
| 30 | st 09.06.2027 | A CHE BINARIO? |
| 31 | čt 17.06.2027 | HO SONNO. |
| 32 | pá 25.06.2027 | POSSO PAGARE CON LA CARTA? |
| 33 | út 29.06.2027 | STO BENE. |
| 34 | st 07.07.2027 | PRONTO? |
| 35 | čt 15.07.2027 | MI PIACE / MI PIACCIONO |
| 36 | pá 23.07.2027 | TI VA DI VENIRE? |
| 37 | út 27.07.2027 | C’È / CI SONO |
| 38 | st 04.08.2027 | LATTE / CAFFELLATTE |
| 39 | čt 12.08.2027 | VOLEVO CHIEDERTI UNA COSA. |
| 40 | pá 20.08.2027 | MI SVEGLIO / MI ALZO |
| 41 | út 24.08.2027 | SARÀ A CASA. |
| 42 | st 01.09.2027 | GENITORI / PARENTI |
| 43 | čt 09.09.2027 | POTRESTI ASPETTARE? |
| 44 | pá 17.09.2027 | CAMERA / VIDEOCAMERA |
| 45 | út 21.09.2027 | NON ANCORA / NON PIÙ |
| 46 | st 29.09.2027 | AL BANCO / AL TAVOLO |
| 47 | čt 07.10.2027 | STO PER PARTIRE. |
| 48 | pá 15.10.2027 | L’APERITIVO |
| 49 | út 19.10.2027 | CE L’HO. |
| 50 | st 27.10.2027 | PRIMO / SECONDO |
| 51 | čt 04.11.2027 | CE L’HO FATTA! |
| 52 | pá 12.11.2027 | LA SAGRA |
