# Text Anonymizer
*Text Anonymizer* is a text anonymization app for journalists, newscasters, and content producers. It uses natural language processing to enable the users to anonymize different parts of a text (e.g., name of individuals, locations, dates, etc.). The app provides the option to replace the names (e.g., individuals, countries, organizations, etc.) with place holders or with fake names.

**Web app:** [https://text-anonymizer.herokuapp.com/](https://text-anonymizer.herokuapp.com/)

**API:** OpenAPI (Swagger) documentation available in [json](https://github.com/kayvanrad/text_anonymizer/blob/master/openapi.json) and [yaml](https://github.com/kayvanrad/text_anonymizer/blob/master/openapi.yaml) format

**Author:** [Aras Kayvanrad](https://www.linkedin.com/in/kayvanrad/).
**Company:** Insight Data Science, Toronto

It is common for journalists and content producers to anonymize stories or redact documents for confidentiality, privacy, and/or security reasons. Another application would be to reduce the bias based on sex, ethnicity, etc. that names can carry. For example, a hiring manager may wish to anonymize the portfolio of the applicants to reduce hiring bias. Depending on the content, various parts of the text may need to be anonymized/redacted. This may include name of individuals, locations, dates, monetary values, etc.

Through the web app, the user selects the entity type(s) that she wishes to anonymize. Text Anonymizer currently supports the following entity types: 
- Person
- Nationalities or religious or political groups
- Companies, agencies, institutions, etc.
- Countries, cities, states
- Date
- Languages
- Monetary values 

The app provides the option to to redact the text by replacing these entities with a place holder or to replace them with fictional names, as it is often desired to replace names of individuals, places, languages, etc. with fictional names rather than with a place holder to maintain the integrity of the story. Text Anonymizer uses a list of fictional characters, places, languages, etc. to anonymize stories with fictional names should the user wish to do so.

### Natural language processing (NLP) pipeline
**(a) Tokenization and Part-of-speech tagging**
![Text Anonymizer NLP pipeline - Tokenization/PoS](https://docs.google.com/drawings/d/e/2PACX-1vSGMfKRnL96zDNtUxB4uG6awfr1qi2LIPzv2zDUoO4vynDEj-KWdPGZlS5r0oajGR8_ugf5HfE6niLY/pub?w=1304&h=505)

Text Anonymizer uses the [English core web spaCy model](https://spacy.io/models) for tokenization and document parsing.

**(b) Unique name identification and fictional name matching**
![Text Anonymizer NLP pipeline - unique name identification / Fictional name matching](https://docs.google.com/drawings/d/e/2PACX-1vS0jgQNPEimIfJE8hIQBRvJ0ZEGM52bFyVqbQeAzSCD-P6-cfDKDq528anwX-MdjctdnYYr-3rDgleM/pub?w=1315&h=656)

A person can appear in several places in the text, and they may be referred to by full name, first name, or last name. In this example, Thomas Edison is referred to once by full name, once by first name (Thomas), and once by last name (Edison). Moreover, if there are people in the text with the same first or last name, Text Anonymizer attempts to identify which person was referred to based on the text preceding the reference. In the above example, Thomas Edison and Thomas Jefferson share the same first name. If called by first name, Text Anonymizer attempts to identify the person based on the preceding text.

When an entity is identified as a PERSON, Text Anonymizer identifies the unique person, and the fictional person assigned to them - or assign a fictional person if the person is seen for the first time. Text Anonymizer then identifies whether the person was called by full name or first / last name, and matches the reference to the fictional person accordingly. In the above example, Thomas Edison is given the fictional name Humma Kavula. References to Thomas are replaced with Humma and references to Edison are replaced by Kavula.

### Further development
Text Anonymizer currently does not match gender for fictional names. To use gender specific fictional names, further development will require to identify the gender of the characters referred to in the text. This can be done, for example, based on the associated pronouns.

It may also be desired to anonymize the gender, which will require not only the use of gender-neutral fictional names, but also replacing the associated pronouns with gender-neutral pronouns.


**Try Text Anonymizer** [text-anonymizer.herokuapp.com](https://text-anonymizer.herokuapp.com/)
