# Labelling rules

Shared by all three parts of the holdout. Translated from the Polish rules the generator worked from; the data was labelled against the original text.

1. **`name`:** a natural person, every mention separately. The span excludes a title or honorific (`Dr.`, `Mr.`, `Pani`). Each person mention has a form in `formy`:
   - `full`: first name and surname, including a middle name, a hyphenated name or a particle (van der, de la, O'…);
   - `single`: only a first name or only a surname in a person context (greeting, signature, “ask Maria”, speaker line “Tom:”);
   - `titled`: a title plus one surname word (`Dr. Patel`, `Pani Nowak`); the span is the surname only;
   - `reversed`: “Surname, First name” in a list or form, as one span.

   A street patron inside an address belongs to the `address` span and is not a `name`. Companies, brands, places, titles of works, diseases and units named after people (Parkinson's disease, Gaussian) are **not** `name`.
2. **`address`:** a complete deliverable address: a street with a number (or P.O. Box / skrytka / Postfach) **and** a postcode and/or city, as one span, including multi-line blocks (`\n`). Not an address: a street alone, a city or postcode alone, “Room 418”, a warehouse, an IP address, GPS coordinates, a path, a version, an amount.
3. **`phone`:** a complete number (E.164 or local), with an extension in the same span. Not a phone: an extension alone, an order number with hyphens, a date, a time, a postcode, a port, a PID, a SKU, a tracking number.
4. **`email`:** the address of a person or of a named mailbox (including subdomains and plus tags). Not an e-mail: `noreply@…`, `mailer-daemon@…`, `user@host` in SSH/Git/DB strings, an `@handle`, code decorators and rules, placeholders such as `<first>@<company>`.
5. **`card`:** a full card number (Amex 15, Visa/Mastercard 16 digits) with a valid prefix and a **valid Luhn checksum**, any separators. Not a card: a number failing Luhn, a masked number (`**** 4821`), the last 4 digits alone, a payment gateway token `tok_…`.
6. **`iban`:** an ISO country code, 2 check digits, a BBAN valid for that country, `mod 97 == 1`; with or without spaces. Not an IBAN: a Polish NRB without `PL`, a sort code plus account, BLZ plus Konto, BIC/SWIFT, a wrong checksum.
7. **`pesel`:** 11 digits with a valid date (century encoded in the month) and a valid weighted checksum `1 3 7 9 1 3 7 9 1 3`. Not a PESEL: NIP, REGON, an 11-digit ID without the checksum.
8. **`ssn`:** `NNN-NN-NNNN`, `NNN NN NNNN`, or 9 digits in an SSN/TIN/W-2 context; area ≠ 000, 666, 900–999; group ≠ 00; serial ≠ 0000. Not an SSN: ITIN (9xx), EIN `XX-XXXXXXX`, an ABA routing number.
9. **`secret`:** the secret value alone (without the key name and without `Bearer `): API keys and tokens, passwords, JWTs, 2FA/OTP codes and PINs in an explicit access context. Not a secret: a SHA, a UUID, a correlation ID, an SSH key fingerprint, a variable name without a value, a placeholder.
10. **Completeness:** `gold` covers every occurrence of **all 9 categories** in a text. Texts for a target category avoid other categories apart from `name`; where they occur, they are labelled.
