# Online Italsky – automatické příspěvky na Instagram

Každý den mezi 8. a 20. hodinou (Praha) se dvakrát za hodinu samo spustí `scripts/publish.py`. Pokud v souboru `prispevky.json` nastal termín dalšího příspěvku (nebo u sněhového příspěvku platí podmínka počasí), zveřejní ho na Instagramu @onlineitalsky, hned potom stejný příspěvek na facebookové stránce Online Italsky a obojí zapíše do `odeslano.json`.

## Jednorázové nastavení
1. **Settings → Secrets and variables → Actions → New repository secret**: název `IG_TOKEN`, hodnota = token systémového uživatele z Meta Business (platnost „Nikdy“).
2. **Actions → Instagram – Online Italsky → Run workflow → režim `test`**: ověří token, účet a dostupnost obrázků. Nic nezveřejní.
3. Hotovo. Od prvního termínu to běží samo.

## Běžné úpravy
- **Změnit text nebo termín:** upravte příslušný řádek v `prispevky.json` (termín ve tvaru `2027-03-09 18:00`, čas může být kdykoli mezi 8:00 a 20:00).
- **Tematické příspěvky** mají čísla od 101 (v rozpisu S1, S2…). Příspěvek s polem `podminka` místo data vyjde podle počasí (data Open-Meteo).
- **Vyměnit obrázek:** nahrajte nový JPEG 1080×1350 se stejným názvem do složky `feed/`.
- **Pozastavit:** Actions → Instagram – Online Italsky → ⋯ → Disable workflow.
- **Zveřejnit další příspěvek hned:** Run workflow → režim `publikovat-ted`.

## Pojistky
- Nejvýš jeden příspěvek denně. Když se nějaký termín zmešká (např. kvůli neplatnému tokenu), doběhne další den.
- Před zveřejněním se kontroluje, že stejný příspěvek už na profilu není.
- Když se zveřejnění nepovede, běh skončí chybou a GitHub pošle e-mail.
- Když se nepovede Facebook (Instagram už vyšel), skript to zkusí ještě dvakrát při dalších bězích.
- Facebook lze vypnout: Settings → Secrets and variables → Actions → Variables → `FACEBOOK` = `0`.
- Repozitář musí zůstat **Public**: Instagram si obrázky stahuje z veřejné adresy.

## Rozpis
| # | Termín | Příspěvek |
|---|---|---|
| 1 | út 17.11.2026 18:00 | LA CHIAVE |
| 2 | st 25.11.2026 18:00 | BOH |
| S1 | ne 29.11.2026 18:00 | L’AVVENTO – 1. adventní neděle |
| 3 | čt 03.12.2026 18:00 | PESCE / PESCHE |
| S2 | so 05.12.2026 18:00 | SAN NICOLA – Mikuláš |
| S3 | ne 06.12.2026 18:00 | LA CORONA D’AVVENTO – 2. adventní neděle |
| 4 | pá 11.12.2026 18:00 | MAGARI! |
| S4 | ne 13.12.2026 18:00 | SANTA LUCIA – sv. Lucie + 3. advent |
| 5 | út 15.12.2026 18:00 | GLI GNOCCHI |
| 6 | út 22.12.2026 18:00 | MA DAI! |
| S5 | čt 24.12.2026 10:00 | LA VIGILIA DI NATALE – Štědrý den |
| 7 | út 29.12.2026 18:00 | NONO / NONNO |
| S6 | čt 31.12.2026 14:00 | BUON ANNO! – Silvestr |
| S7 | st 06.01.2027 18:00 | LA BEFANA – Tři králové (Epifania) |
| 8 | pá 08.01.2027 18:00 | SONO ALLA FRUTTA |
| 9 | út 12.01.2027 18:00 | E / È |
| 10 | st 20.01.2027 18:00 | MI DAI UNA MANO? |
| 11 | čt 28.01.2027 18:00 | UN PO’ |
| 12 | pá 05.02.2027 18:00 | UN PESCE FUOR D’ACQUA |
| S8 | út 09.02.2027 18:00 | IL CARNEVALE – masopustní úterý |
| 13 | čt 11.02.2027 18:00 | LA MANO |
| S9 | ne 14.02.2027 18:00 | TI AMO / TI VOGLIO BENE – Valentýn |
| 14 | st 17.02.2027 18:00 | MEGLIO TARDI CHE MAI |
| 15 | čt 25.02.2027 18:00 | DUE CAFFÈ |
| 16 | pá 05.03.2027 18:00 | CIOÈ |
| S10 | po 08.03.2027 18:00 | LA FESTA DELLA DONNA – MDŽ |
| 17 | st 10.03.2027 18:00 | VECCHIO AMICO / AMICO VECCHIO |
| 18 | st 17.03.2027 18:00 | FIGURATI! |
| 19 | čt 25.03.2027 18:00 | BRAVA! |
| S11 | ne 28.03.2027 18:00 | BUONA PASQUA! – Velikonoční neděle |
| 20 | pá 02.04.2027 18:00 | PUÒ RIPETERE, PER FAVORE? |
| 21 | út 06.04.2027 18:00 | BELLISSIMO |
| 22 | st 14.04.2027 18:00 | DA PORTARE VIA |
| 23 | čt 22.04.2027 18:00 | QUALCHE GIORNO |
| 24 | pá 30.04.2027 18:00 | COSA CI CONSIGLIA? |
| 25 | út 04.05.2027 18:00 | A ROMA / IN ITALIA |
| 26 | st 12.05.2027 18:00 | BASTA COSÌ, GRAZIE. |
| 27 | čt 20.05.2027 18:00 | LUNEDÌ / IL LUNEDÌ |
| 28 | pá 28.05.2027 18:00 | POSSO ANDARCI A PIEDI? |
| 29 | po 31.05.2027 18:00 | SONO LE SEI E MEZZO. |
| S12 | st 02.06.2027 18:00 | LA FESTA DELLA REPUBBLICA – Den republiky |
| 30 | st 09.06.2027 18:00 | A CHE BINARIO? |
| 31 | čt 17.06.2027 18:00 | HO SONNO. |
| 32 | pá 25.06.2027 18:00 | POSSO PAGARE CON LA CARTA? |
| 33 | út 29.06.2027 18:00 | STO BENE. |
| 34 | st 07.07.2027 18:00 | PRONTO? |
| 35 | čt 15.07.2027 18:00 | MI PIACE / MI PIACCIONO |
| 36 | pá 23.07.2027 18:00 | TI VA DI VENIRE? |
| 37 | út 27.07.2027 18:00 | C’È / CI SONO |
| 38 | st 04.08.2027 18:00 | LATTE / CAFFELLATTE |
| 39 | čt 12.08.2027 18:00 | VOLEVO CHIEDERTI UNA COSA. |
| S13 | ne 15.08.2027 18:00 | FERRAGOSTO – Ferragosto |
| 40 | pá 20.08.2027 18:00 | MI SVEGLIO / MI ALZO |
| 41 | út 24.08.2027 18:00 | SARÀ A CASA. |
| 42 | st 01.09.2027 18:00 | GENITORI / PARENTI |
| 43 | čt 09.09.2027 18:00 | POTRESTI ASPETTARE? |
| 44 | pá 17.09.2027 18:00 | CAMERA / VIDEOCAMERA |
| 45 | út 21.09.2027 18:00 | NON ANCORA / NON PIÙ |
| 46 | st 29.09.2027 18:00 | AL BANCO / AL TAVOLO |
| 47 | čt 07.10.2027 18:00 | STO PER PARTIRE. |
| 48 | pá 15.10.2027 18:00 | L’APERITIVO |
| 49 | út 19.10.2027 18:00 | CE L’HO. |
| 50 | st 27.10.2027 18:00 | PRIMO / SECONDO |
| 51 | čt 04.11.2027 18:00 | CE L’HO FATTA! |
| 52 | pá 12.11.2027 18:00 | LA SAGRA |
| S14 | podle počasí, 18:00 | LA PRIMA NEVE – první den od 2026-11-20, kdy v místě Krkonoše (Špindlerův Mlýn) napadne ≥ 15 cm sněhu za 24 h; po 2027-02-28 se vynechá |
