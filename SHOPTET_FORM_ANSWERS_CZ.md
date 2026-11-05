# Shoptet Doplňky — Готовые ответы для формы регистрации нового дополнения (Copy & Paste)

Официальная форма подачи заявки в Shoptet:  
👉 **[https://salesforce-eu.123formbuilder.com/form-62353/cz-nabidka-noveho-doplnku](https://salesforce-eu.123formbuilder.com/form-62353/cz-nabidka-noveho-doplnku)**

Живая демонстрационная ссылка вашего чешского приложения (100% изолирована от Shopify):  
👉 **[https://mikrozar-cell.github.io/sortflow-shoptet/](https://mikrozar-cell.github.io/sortflow-shoptet/)**

---

## Поля анкеты (по порядку сверху вниз):

### 1. Jméno a příjmení (Имя и фамилия)
* **First Name:** `Sergey`
* **Last Name:** `Gorbunov`

### 2. Telefonní číslo (Телефон)
* Введите ваш словенский номер телефона (например, `+386 ...`).

### 3. E-mailová adresa (E-mail)
* `mikrozar@gmail.com`

### 4. IČO (Регистрационный / налоговый номер)
* Если подаете как ИП / компания в Словении — укажите ваш словенский регистрационный / налоговый номер (Matična / Davčna številka), либо `EU Developer (Slovenia)` / прочерк, если оформляете на физлицо до подписания договора.

### 5. Firma, kterou zastupujete (Компания / Разработчик)
* `Sergey Gorbunov — SortFlow Pro`

---

### 6. Navrhovaný název doplňku (Предлагаемое название дополнения)
```text
SortFlow: Vizuální řazení produktů a správa vyprodaných
```

---

### 7. Pro které klienty a trhy je doplněk určený? (Для каких клиентов и рынков предназначен аддон?)
```text
Doplněk je určen pro všechny e-shopy na platformě Shoptet (tarify Free, Basic, Business, Profi, Enterprise i Shoptet Premium) na trzích ČR (doplnky.shoptet.cz), SR (doplnky.shoptet.sk) a HU. Cílovou skupinou jsou e-shopy s módou, obuví, elektronikou, kosmetikou a dárkovým zbožím, které potřebují plnou vizuální kontrolu nad pořadím produktů v kategoriích a automatické odsouvání vyprodaných položek.
```

---

### 8. Technický popis doplňku, jeho fungování a přínos pro zákazníka/e-shop (Техническое описание работы и польза для магазина)
```text
SortFlow Pro řeší jeden z nejčastějších problémů e-shopařů: vyprodané produkty zůstávají na předních místech kategorií (snižují konverzní poměr) a při opětovném naskladnění se nevrátí na svou původní pozici.

Hlavní funkce a přínos pro e-shopy:
1. Vizuální Drag & Drop editor priorit: Přehledná mřížka produktů s okamžitým náhledem pozice, hromadným výběrem (Multi-Select) a rychlým skokem na zadané pořadí.
2. Připnutí klíčových produktů (Pin-to-Top): Možnost uzamknout vybrané bestseller/hero produkty na prvních pozicích kategorie.
3. Automatické odsunutí vyprodaných produktů (Auto-Demote Out-of-Stock): Při vyprodání produktu (stav skladu = 0 ks na základě webhooku stock:movement) doplněk automaticky přesune produkt na konec kategorie.
4. Paměť naskladnění (Restock Memory): Doplněk si pamatuje přesnou původní pozici produktu před vyprodáním. Jakmile je produkt znovu naskladněn (> 0 ks), automaticky jej vrátí na původní místo v kategorii.
5. Chytré řazení novinek (Smart New Arrivals): Nově přidané produkty se automaticky zařadí hned za připnuté položky (nikdy nezapadnou pod vyprodané zboží).
6. 1-Click Undo (Okamžitá obnova ze zálohy): Před každou změnou doplněk uloží snapshot priorit kategorie s možností obnovení jedním kliknutím.
```

---

### 9. Je někde doplněk viditelný, nasazený na produkčním nebo testovacím e-shopu? (Где можно посмотреть живое демо дополнения?)
```text
Ano, plně funkční interaktivní česká demoverze doplňku je dostupná online zde:
https://mikrozar-cell.github.io/sortflow-shoptet/

V demoverzi si můžete ihned vyzkoušet Drag & Drop přesouvání karet, připnutí produktů (Připnout), simulaci vyprodání (Vyprodat 0 ks -> automatické odsunutí na konec), simulaci naskladnění (Naskladnit +25 ks -> návrat na původní pozici díky Paměti naskladnění) i 1-Click Undo.
```

---

### 10. Předpokládaná cena za vytvořený doplněk (Предполагаемая цена по сетке Shoptet)
```text
200 Kč / měsíc (2 304 Kč / rok se slevou 4 %), 14 dní na vyzkoušení zdarma.
```

---

### 11. Popis vašeho business modelu — je služba na vaší straně účtovaná? (Описание бизнес-модели)
```text
Jednoduchý a transparentní model předplatného přímo přes fakturaci Shoptet Doplňků (200 Kč / měsíc s 14denní bezplatnou zkušební dobou). Na naší straně nejsou účtovány žádné další ani skryté poplatky, žádné limity počtu produktů ani kategorií.
```

---

### 12. Чекбокс подтверждения ознакомления с API документацией
* Поставьте галочку **`[x] Zaškrtnutím políčka závazně potvrzuji...`**

---

### 13. Níže vypište seznam endpointů, které plánujete u doplňku využívat, včetně stručného popisu use-case (Список эндпоинтов Shoptet API и их назначение)
```text
1. GET /api/categories
Use-case: Načtení seznamu kategorií e-shopu pro výběr kategorie ve vizuálním editoru.

2. GET /api/categories/{categoryGuid} a PATCH /api/categories/{categoryGuid}
Use-case: Kontrola a případné přepnutí způsobu řazení kategorie na "category-priority" (řazení dle priority produktů).

3. GET /api/categories/{categoryGuid}/productsPriority
Use-case: Načtení aktuálního seznamu produktů v dané kategorii a jejich stávajících priorit (stránkování po 1000 položkách).

4. PATCH /api/categories/{categoryGuid}/productsPriority
Use-case: Hromadný zápis nově vypočtených priorit produktů (0..65535) v dávkách (batch až 300 položek na požadavek) po ruční úpravě nebo automatickém přeřazení.

5. GET /api/products a GET /api/products/{guid}
Use-case: Získání názvu, kódu (SKU), ceny, náhledového obrázku a aktuálního stavu skladu (stock) produktů v kategorii.

6. POST /api/webhooks (registrace webhooků: stock:movement, product:create, product:update, addon:uninstall)
Use-case: Automatické přeřazení vyprodaných produktů na konec kategorie a jejich návrat na původní pozici po naskladnění v reálném čase, plus vyčištění dat při odinstalaci doplňku.
```
