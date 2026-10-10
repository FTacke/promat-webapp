"""Localized long-form content definitions for PROMAT public pages."""

from __future__ import annotations


PROJECT_VIDEO_YOUTUBE_ID = "ucvpPAONGoY"
PROJECT_VIDEO_YOUTUBE_SOURCE_URL = "https://youtu.be/ucvpPAONGoY?si=HhtYele7RsY3hmS0"
PROJECT_VIDEO_YOUTUBE_EMBED_URL = "https://www.youtube.com/embed/ucvpPAONGoY"
MARELE_PROJECT_URL = "https://hispanistica.com/projects/marele/"


def _link_marele(text: str) -> str:
    return text.replace("MAR.ELE", f'<a href="{MARELE_PROJECT_URL}">MAR.ELE</a>')


LEGACY_PROJECT_PAGE_REDIRECTS: dict[str, str] = {
    "research-design": "structure",
}


PROJECT_PAGES_CONTENT: dict[str, dict[str, object]] = {
    "about": {
        "title": {
            "de": "Worum es geht",
            "en": "What this project is about",
        },
        "page_kind": "reading",
        "sections": [
            {
                "heading": {
                    "de": "Aussprache als Forschungs- und Unterrichtsgegenstand",
                    "en": "Pronunciation as a subject of research and teaching",
                },
                "paragraphs_html": {
                    "de": [
                        "Aussprache gehört zu den zentralen Bereichen des Fremdsprachenlernens, wird in Forschung, Hochschullehre und schulischer Praxis aber häufig weniger systematisch behandelt als Wortschatz, Grammatik oder Textkompetenz. Gerade für Lernende ist Aussprache jedoch kein Randthema. Sie betrifft Verständlichkeit, Hörwahrnehmung, Selbstsicherheit beim Sprechen und die Frage, wie sprachliche Variation im Unterricht sinnvoll vermittelt werden kann.",
                        "<em>Pronunciation Matters</em> setzt hier an. Das Projekt erhebt, strukturiert und erschließt Sprachaufnahmen von Lernenden so, dass sie für Forschung und Lehre gezielt genutzt werden können. Im Mittelpunkt steht nicht die bloße Bewertung von Aussprache nach dem Maßstab vermeintlicher Nativität. Entscheidend sind vielmehr Intelligibilität, systematische Muster, wiederkehrende Schwierigkeiten, sprachliche Variation und die Frage, wie Aussprache im Fremdsprachenunterricht nachvollziehbar, vergleichbar und lernendengerecht thematisiert werden kann.",
                        "Die Plattform verbindet dafür drei Ebenen: empirische Forschung zu Lernendenaussprache, forschungsnahe Hochschullehre und die Entwicklung von Materialien für den schulischen Unterricht. Studierende arbeiten nicht nur mit fertigen Beispielen, sondern erhalten Einblick in die Entstehung, Aufbereitung und Analyse authentischer Sprachdaten. Lehrkräfte und Lernende können von Materialien profitieren, die aus der wissenschaftlichen Arbeit heraus entwickelt werden.",
                    ],
                    "en": [
                        "Pronunciation is a central part of foreign language learning, but it is often treated less systematically than vocabulary, grammar, or textual competence in research, higher education, and school practice. For learners, however, pronunciation is not a marginal issue. It affects intelligibility, listening perception, confidence in speaking, and the question of how linguistic variation can be addressed meaningfully in the classroom.",
                        "This is where <em>Pronunciation Matters</em> begins. The project records, structures, and makes accessible speech data from learners so that it can be used specifically for research and teaching. The aim is not simply to evaluate pronunciation against a supposed native-speaker standard. What matters instead are intelligibility, systematic patterns, recurring difficulties, linguistic variation, and the question of how pronunciation can be addressed in foreign language teaching in ways that are transparent, comparable, and appropriate for learners.",
                        "The platform connects three levels: empirical research on learner pronunciation, research-based university teaching, and the development of materials for school contexts. Students do not only work with finished examples; they gain insight into how authentic speech data is created, processed, and analysed. Teachers and learners can benefit from materials that are developed out of this research process.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Vom Pilotprojekt zur mehrsprachigen Plattform",
                    "en": "From a pilot project to a multilingual platform",
                },
                "paragraphs_html": {
                    "de": [
                        _link_marele("Ausgangspunkt von <em>Pronunciation Matters</em> war das spanische Pilotprojekt MAR.ELE. In diesem Projekt wurden an der Philipps-Universität Marburg zwischen 2024 und 2025 Sprachaufnahmen von Spanischlernenden erhoben, aufbereitet und in einer WebApp zugänglich gemacht. MAR.ELE zeigte, dass authentische Lernendenaussprache nicht nur dokumentiert, sondern auch für linguistische Analysen, fachdidaktische Diskussionen und Unterrichtsmaterialien fruchtbar gemacht werden kann."),
                        _link_marele("Gleichzeitig machte MAR.ELE deutlich, wo ein kleines Pilotprojekt an Grenzen stößt. Für MAR.ELE wurde zunächst an bestehende korpusphonologische Forschungsprojekte angeknüpft; insbesondere wurde die Wortliste aus dem Projekt (I)FEC übernommen, um an ein etabliertes Design zur Beschreibung spanischer Aussprachevariation anzuschließen. In der Arbeit mit Lernenden zeigte sich jedoch, dass solche Materialien nicht ohne Weiteres auf ein lernendensprachliches Aussprachekorpus übertragbar sind. Manche Items waren lexikalisch unnötig schwierig, manche für Lernendenaussprache relevante Phänomene wurden nicht ausreichend mehrfach abgedeckt, und nicht jedes etablierte Aufgabenformat passte zu einer Erhebung, die vergleichbare Daten erzeugen und zugleich für Lernende gut bearbeitbar bleiben soll."),
                        "<em>Pronunciation Matters</em> führt diese Erfahrungen weiter. Das Projekt nutzt bestehende Forschungsdesigns als wichtige Orientierung, passt Aufgabenformate und Materialien aber gezielt an die Arbeit mit Lernenden an. So entsteht eine Plattformstruktur, in der Datenerhebung, Aufbereitung, Analyse und didaktische Nutzung von Anfang an zusammengedacht werden.",
                        "Die Plattform beginnt mit den vier in Marburg vertretenen Bereichen Spanisch, Französisch, Englisch und Deutsch als Fremd- bzw. Zweitsprache. Das Projekt folgt dabei einem gemeinsamen Grunddesign: Die Aufnahmen werden unter vergleichbaren Bedingungen erhoben, die Aufgabenformate sind systematisch angelegt, die Metadaten werden nachvollziehbar erfasst, und die Forschungsdaten werden pseudonymisiert in eine gemeinsame Plattformstruktur überführt. Zugleich muss dieses Design sprachspezifisch angepasst werden. Nicht jede Sprache verlangt dieselben Materialien und nicht jedes Aufgabenformat ist für alle Lernkontexte gleichermaßen sinnvoll. Für Spanisch, Französisch und Deutsch können etwa kontrollierte Satzlisten mit gut verständlichen Einzeläußerungen naheliegen, während im Englischen ein etablierter zusammenhängender Text besser geeignet sein kann, weil Englisch als Fremdsprache unter anderen Voraussetzungen gelernt, gelesen und schulisch vermittelt wird. Die einzelnen Sprachkorpora bleiben deshalb vergleichbar, ohne ihre fachlichen Unterschiede künstlich zu glätten.",
                    ],
                    "en": [
                        _link_marele("The starting point for <em>Pronunciation Matters</em> was the Spanish pilot project MAR.ELE. Between 2024 and 2025, this project collected recordings of learners of Spanish at Philipps-Universität Marburg, processed them, and made them accessible through a web app. MAR.ELE showed that authentic learner pronunciation can be documented and also used productively for linguistic analysis, subject-specific didactic discussion, and teaching materials."),
                        _link_marele("At the same time, MAR.ELE made clear where a small pilot project reaches its limits. The project initially connected with existing corpus-phonological research projects; in particular, it adopted the wordlist from the (I)FEC project in order to build on an established design for describing Spanish pronunciation variation. In the work with learners, however, it became clear that such materials cannot simply be transferred to a corpus of learner pronunciation. Some items were lexically unnecessarily difficult, some phenomena relevant to learner pronunciation were not covered often enough, and not every established task format fitted an elicitation design that needs to produce comparable data while remaining manageable for learners."),
                        "<em>Pronunciation Matters</em> builds on these experiences. The project uses existing research designs as important points of orientation, but adapts task formats and materials specifically for work with learners. This creates a platform structure in which data collection, processing, analysis, and didactic use are considered together from the outset.",
                        "The platform begins with the four areas represented in Marburg: Spanish, French, English, and German as a foreign or second language. The project follows a shared basic design: recordings are collected under comparable conditions, task formats are systematic, metadata is recorded transparently, and research data is pseudonymised and transferred into a common platform structure. At the same time, this design needs to be adapted for each language. Not every language requires the same materials, and not every task format is equally suitable for every learning context. For Spanish, French, and German, controlled sentence lists with easily comprehensible individual utterances may be appropriate, whereas in English an established connected text may be more suitable because English as a foreign language is learned, read, and taught under different conditions. The individual language corpora therefore remain comparable without artificially smoothing over their disciplinary differences.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Lehre, Forschung und Transfer",
                    "en": "Teaching, research, and transfer",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> ist als Lehr- und Forschungsprojekt angelegt. Seit Januar 2026 wird die mehrsprachige Plattform konkret aufgebaut; erste Aufnahmen wurden seit Anfang März 2026 durchgeführt. Im Sommersemester 2026 ist das Projekt in vier Lehrveranstaltungen eingebunden, die jeweils auf eine der Projektsprachen bezogen sind. Dort werden Forschung, Datenerhebung, Analyse und Materialentwicklung nicht voneinander getrennt, sondern als zusammenhängender Arbeitsprozess erfahrbar.",
                        "Für die Hochschullehre ist das besonders wichtig. Studierende können an authentischen Forschungsdaten arbeiten, ohne dass diese Daten nur als fertige Beispiele erscheinen. Sie lernen, wie Aufnahmen entstehen, wie Daten strukturiert werden, welche Entscheidungen bei Aufgabenformaten und Annotationen nötig sind und wie sich aus Analyseergebnissen didaktische Materialien entwickeln lassen. Das Projekt verbindet damit fachwissenschaftliche Ausbildung, digitale Methoden und fachdidaktische Reflexion.",
                        "Der Transfer in den schulischen Unterricht ist von Anfang an mitgedacht. Schulmaterialien werden teilweise in Lehrveranstaltungen gemeinsam mit Studierenden konzipiert und verfasst. Dabei geht es nicht darum, Forschungsdaten ungefiltert in den Unterricht zu übertragen. Vielmehr werden aus der Forschung heraus geeignete Ausschnitte, Aufgaben und Erklärformate entwickelt, die Aussprachebewusstsein, Hörwahrnehmung und die Reflexion sprachlicher Variation unterstützen.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> is designed as a teaching and research project. Since January 2026, the multilingual platform has been built in concrete terms; the first recordings have been carried out since early March 2026. In the summer semester of 2026, the project is embedded in four courses, each related to one of the project languages. In these courses, research, data collection, analysis, and material development are not separated from one another, but experienced as parts of one connected work process.",
                        "This is especially important for university teaching. Students can work with authentic research data without encountering it only as finished examples. They learn how recordings are made, how data is structured, which decisions are involved in task formats and annotation, and how didactic materials can be developed from analytical findings. The project therefore connects subject-specific academic training, digital methods, and didactic reflection.",
                        "Transfer to school contexts is built into the project from the beginning. Some teaching materials are designed and written together with students in university courses. This is not about transferring research data into classrooms without mediation. Rather, suitable excerpts, tasks, and explanatory formats are developed from the research process to support pronunciation awareness, listening perception, and reflection on linguistic variation.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Auszeichnung und Weiterentwicklung",
                    "en": "Award and further development",
                },
                "paragraphs_html": {
                    "de": [
                        "Die Idee zu <em>Pronunciation Matters</em> wurde im November 2025 im Ideenwettbewerb Lehre@Philipp der Philipps-Universität Marburg als innovative Lehridee ausgezeichnet und gefördert. Mit dem Preis war eine Förderung von etwas mehr als 10.000 Euro verbunden. Diese Mittel ermöglichten es, den Pilotansatz innerhalb von rund zehn Monaten zu einer mehrsprachigen Plattform auszubauen. Möglich wurde dieser Ausbau durch die Mitwirkung der beteiligten Kolleg:innen, die das Projekt in ihren jeweiligen Sprachen fachlich tragen und in Lehrveranstaltungen, Datenerhebung und Materialentwicklung einbinden.",
                        "Ziel des geförderten Projekts ist nicht der Abschluss eines Forschungsprogramms, sondern der Aufbau einer belastbaren Ausgangsstruktur. <em>Pronunciation Matters</em> schafft die Plattform, legt erste Sprachkorpora an und entwickelt erste Unterrichtsmaterialien. Damit entsteht ein gemeinsamer Arbeitsraum für Forschung, Hochschullehre und schulische Vermittlung, der weiter wachsen soll. Die Plattform ist als Auftakt gedacht: für die beteiligten Fächer in Marburg ebenso wie für interessierte Forschende, Lehrende und Studierende, die künftig mit den Daten, Werkzeugen und Materialien weiterarbeiten möchten.",
                    ],
                    "en": [
                        "The idea for <em>Pronunciation Matters</em> was recognised and funded as an innovative teaching idea in November 2025 through the Lehre@Philipp ideas competition at Philipps-Universität Marburg. The award came with funding of a little over 10,000 euros. These funds made it possible to expand the pilot approach into a multilingual platform within roughly ten months. This expansion was made possible by the involvement of the participating colleagues, who support the project in their respective languages and embed it in teaching, data collection, and material development.",
                        "The aim of the funded project is not to complete a research programme, but to build a solid starting structure. <em>Pronunciation Matters</em> creates the platform, establishes first language corpora, and develops first teaching materials. This creates a shared working space for research, university teaching, and school-based mediation that is intended to grow further. The platform is meant as a starting point: for the participating disciplines in Marburg as well as for interested researchers, teachers, and students who may want to work with the data, tools, and materials in the future.",
                    ],
                },
            },
            {
                "media_embed": {
                    "provider": "youtube",
                    "youtube_id": PROJECT_VIDEO_YOUTUBE_ID,
                    "embed_url": PROJECT_VIDEO_YOUTUBE_EMBED_URL,
                    "source_url": PROJECT_VIDEO_YOUTUBE_SOURCE_URL,
                    "title": {
                        "de": "Projektvideo zu Pronunciation Matters",
                        "en": "Pronunciation Matters project video",
                    },
                    "caption_html": {
                        "de": "Lehre@Philipp 2025: <em>Pronunciation Matters</em> – Fremdsprachen digital erforschen und lehren",
                        "en": "Lehre@Philipp 2025: <em>Pronunciation Matters</em> – Researching and teaching foreign languages digitally",
                    },
                },
            },
        ],
    },
    "structure": {
        "title": {
            "de": "Projektaufbau",
            "en": "Project structure",
        },
        "page_kind": "reading",
        "sections": [
            {
                "heading": {
                    "de": "Eine Plattform, mehrere Sprachkorpora",
                    "en": "One platform, several language corpora",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> ist als mehrsprachige Plattform angelegt. Die WebApp bündelt die Projektsprachen Spanisch, Französisch, Englisch und Deutsch in einer gemeinsamen Struktur. Jede Sprache erhält einen eigenen Korpusbereich mit eigenen Verantwortlichkeiten, eigenen Aufgabenmaterialien und eigenen fachlichen Schwerpunkten. Zugleich bleiben zentrale Strukturprinzipien projektweit stabil.",
                        "Diese Verbindung von gemeinsamer Plattform und sprachspezifischer Ausgestaltung ist wichtig. Ausspracheforschung kann nicht für alle Sprachen identisch organisiert werden. Spanisch, Französisch, Englisch und Deutsch unterscheiden sich in ihren lautlichen Systemen, in ihrer Variation, in didaktischen Traditionen und in den typischen Herausforderungen für Lernende. Ein allgemeines Projektdesign darf diese Unterschiede nicht überdecken. Deshalb werden die konkreten Forschungsdesigns der Sprachkorpora innerhalb der jeweiligen Korpusbereiche dargestellt.",
                        "Die allgemeinen Projektseiten beschreiben dagegen die übergreifende Logik: Warum das Projekt existiert, wie die Plattform aufgebaut ist, welche Datenformen entstehen, wie Forschung und Lehre zusammenhängen und wer am Projekt beteiligt ist.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> is designed as a multilingual platform. The web app brings together the project languages Spanish, French, English, and German in one shared structure. Each language has its own corpus area with its own responsibilities, task materials, and disciplinary priorities. At the same time, central structural principles remain stable across the project.",
                        "This combination of a shared platform and language-specific design is important. Pronunciation research cannot be organised identically for all languages. Spanish, French, English, and German differ in their sound systems, patterns of variation, didactic traditions, and typical challenges for learners. A general project design must not cover up these differences. For this reason, the concrete research designs of the language corpora are presented within the respective corpus areas.",
                        "The general project pages, by contrast, describe the overarching logic: why the project exists, how the platform is structured, what kinds of data are produced, how research and teaching are connected, and who is involved in the project.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Bereiche der WebApp",
                    "en": "Areas of the web app",
                },
                "paragraphs_html": {
                    "de": [
                        "Die öffentliche WebApp gliedert sich in drei inhaltliche Hauptbereiche: Projekt, Forschung und Unterricht.",
                        "Der Projektbereich erklärt die Grundidee, die Entstehung, die Plattformstruktur, die Methodik und die Zusammenarbeit. Er richtet sich an alle Nutzer:innen, die verstehen möchten, was <em>Pronunciation Matters</em> ist und wie das Projekt arbeitet.",
                        "Der Forschungsbereich führt zu den einzelnen Sprachkorpora. Dort werden die jeweiligen Korpusdesigns erläutert. Die geschützten Bereiche enthalten die eigentlichen Sprachdaten und Forschungstools: Über die Seite Sprecher:innen lassen sich die teilnehmenden Informant:innen und ihre sessionbezogenen Player-Einstiege erschließen, über Vergleichsansichten kontrastive Analysen und über phänomenbezogene Item-Sets gezielte Ausschnitte des Materials. Diese Bereiche sind nicht frei zugänglich, weil sie mit pseudonymisierten Sprachdaten und aufnahmebezogenen Metadaten arbeiten.",
                        "Der Unterrichtsbereich bereitet ausgewählte Inhalte für die Aussprachevermittlung auf. Er ist schlanker angelegt als der Forschungsbereich, weil hier nicht die vollständige Forschungsumgebung im Vordergrund steht, sondern thematisch fokussierte Zugänge zu besonders relevanten Aspekten der Aussprache. Solche Themenseiten können kontrastive Vergleiche nutzen, typische Schwierigkeiten sichtbar machen und Material bereitstellen, das Lehrkräfte pragmatisch in bestehende Unterrichtsstunden integrieren können. Dabei geht das Projekt nicht von der Illusion aus, dass Aussprache im schulischen Fremdsprachenunterricht regelmäßig eigene Unterrichtsreihen erhält. Ziel sind vielmehr anschauliche, fachlich fundierte Erweiterungen dort, wo Lehrpläne, Unterrichtssituationen oder konkrete Lernprobleme Raum dafür eröffnen.",
                    ],
                    "en": [
                        "The public web app is divided into three main content areas: Project, Research, and Teaching.",
                        "The Project area explains the basic idea, the development of the project, the platform structure, the methodology, and the collaboration behind it. It is intended for all users who want to understand what <em>Pronunciation Matters</em> is and how the project works.",
                        "The Research area leads to the individual language corpora. The respective corpus designs are explained there. The protected areas contain the actual speech data and research tools: the Speakers page provides access to the participating informants and their session-scoped player entries, comparison views support contrastive analyses, and phenomenon-based item sets allow users to work with targeted excerpts of the material. These areas are not openly accessible because they work with pseudonymised speech data and recording-related metadata.",
                        "The Teaching area presents selected content for pronunciation teaching. It is deliberately leaner than the Research area because the focus here is not the full research environment, but thematically focused access to especially relevant aspects of pronunciation. Such topic pages can use contrastive comparisons, make typical difficulties visible, and provide material that teachers can integrate pragmatically into existing lessons. The project does not assume that pronunciation will regularly be given entire teaching units in school-based foreign language instruction. Rather, the aim is to provide clear and academically sound extensions for moments where curricula, teaching situations, or concrete learning problems allow room for them.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Öffentliche Orientierung und geschützter Forschungszugang",
                    "en": "Public orientation and protected research access",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> unterscheidet zwischen öffentlichen Informations- und Materialbereichen und geschützten Forschungsdaten. Diese Trennung ist nicht bloß eine technische Entscheidung, sondern fachlich und datenschutzrechtlich notwendig.",
                        "Sprachaufnahmen sind personenbezogene bzw. pseudonymisierte Forschungsdaten. Auch wenn Klarnamen nicht in der WebApp erscheinen, können Stimme, Metadaten und Aufnahmekontexte sensible Informationen enthalten. Deshalb werden detaillierte Forschungszugänge nicht frei öffentlich bereitgestellt. Der Zugriff auf Player, Vergleichsansichten, Sprecherprofile und phänomenbezogene Arbeitsflächen bleibt kontrolliert und ist für berechtigte Nutzer:innen aus Forschungs- und Bildungseinrichtungen vorgesehen.",
                        "Öffentlich zugänglich bleiben dagegen Projektinformationen, allgemeine Methodenseiten, sprachspezifische Designbeschreibungen und freigegebene Unterrichtsmaterialien. So bleibt das Projekt transparent, ohne Forschungsdaten unkontrolliert zu veröffentlichen.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> distinguishes between public information and material areas on the one hand, and protected research data on the other. This separation is not merely a technical decision; it is necessary for disciplinary and data-protection reasons.",
                        "Speech recordings are personal or pseudonymised research data. Even when clear names do not appear in the web app, voice, metadata, and recording contexts can contain sensitive information. For this reason, detailed research access is not made freely available to the public. Access to the player, comparison views, speaker profiles, and phenomenon-based work surfaces remains controlled and is intended for authorised users from research and educational institutions.",
                        "Publicly accessible content includes project information, general methodology pages, language-specific design descriptions, and released teaching materials. In this way, the project remains transparent without publishing research data in an uncontrolled manner.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Forschung und Unterricht als getrennte, aber verbundene Räume",
                    "en": "Research and teaching as separate but connected spaces",
                },
                "paragraphs_html": {
                    "de": [
                        "Die Plattform trennt Forschung und Unterricht bewusst. Diese Trennung verhindert, dass Unterrichtsmaterialien wie eine reduzierte Forschungsdatenbank wirken oder dass Forschungsoberflächen didaktische Funktionen übernehmen müssen, für die sie nicht gedacht sind.",
                        "Im Forschungsbereich können Nutzer:innen mit detaillierten Daten arbeiten. Sie können sessionbezogene Player-Ansichten gezielt aufrufen, Materialausschnitte auswählen, kontrastive Vergleiche anlegen und phänomenbezogene Sets erstellen oder modifizieren. Der Forschungsbereich ist damit ein Arbeitsraum für Analyse und Hochschullehre.",
                        "Im Unterrichtsbereich werden ausgewählte Inhalte didaktisch gefasst. Dort geht es um verständliche Erklärungen, Aufgaben, Hörbeispiele und Materialien, die für schulische oder hochschuldidaktische Kontexte geeignet sind. Diese Materialien können aus der Arbeit mit den Forschungsdaten hervorgehen, werden aber nicht einfach direkt aus dem geschützten Datenraum ausgespielt.",
                    ],
                    "en": [
                        "The platform deliberately separates research and teaching. This prevents teaching materials from appearing as a reduced research database and prevents research surfaces from having to take on didactic functions for which they were not designed.",
                        "In the Research area, users can work with detailed data. They can open session-scoped player views, select excerpts of material, build contrastive comparisons, and create or modify phenomenon-based sets. The Research area is therefore a workspace for analysis and university teaching.",
                        "In the Teaching area, selected content is presented didactically. The focus is on clear explanations, tasks, listening examples, and materials suitable for school or university teaching contexts. These materials can emerge from work with the research data, but they are not simply delivered directly from the protected data space.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Technische Grundlage als Teil der Projektidee",
                    "en": "Technical infrastructure as part of the project idea",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> ist auch ein Digital-Humanities-Projekt. Die technische Infrastruktur ist nicht nachträgliche Verpackung, sondern Teil der wissenschaftlichen und didaktischen Arbeitsweise. Datenmodellierung, strukturierte Metadaten, Annotationen, Audioverarbeitung, WebApp-Design und geschützte Zugriffsräume ermöglichen erst, dass die erhobenen Sprachdaten praktisch nutzbar werden.",
                        "Die Plattform soll Forschung und Hochschullehre komfortabel unterstützen. Wer mit den Daten arbeitet, soll nicht zuerst Ordnerstrukturen, Dateinamen oder Rohformate verstehen müssen. Die WebApp bietet stattdessen geordnete Zugänge über Sprachen, Personen, sessionbezogene Player-Ansichten, Vergleichsansichten und Aussprachephänomene. Dadurch wird die technische Komplexität nicht unsichtbar gemacht, aber so organisiert, dass sie wissenschaftliches Arbeiten erleichtert.",
                        "Eine ergänzende technische Projektseite zu <em>Pronunciation Matters</em> wird im Kontext von Hispanistica @ Marburg geführt: https://hispanistica.com/projects/promat/. Die öffentliche WebApp selbst stellt dagegen primär die Projektidee, die Forschungs- und Unterrichtslogik sowie die nutzbaren Inhalte in den Vordergrund.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> is also a digital humanities project. The technical infrastructure is not a layer added after the fact; it is part of the scholarly and didactic method. Data modelling, structured metadata, annotations, audio processing, web app design, and protected access spaces are what make the collected speech data practically usable in the first place.",
                        "The platform is intended to support research and university teaching comfortably. Users working with the data should not first have to understand folder structures, filenames, or raw formats. Instead, the web app offers structured access through languages, persons, session-scoped player views, comparison views, and pronunciation phenomena. Technical complexity is not made invisible, but organised in a way that facilitates scholarly work.",
                        "A supplementary technical project page on <em>Pronunciation Matters</em> is maintained in the context of Hispanistica @ Marburg: https://hispanistica.com/projects/promat/. The public web app itself, however, foregrounds the project idea, the research and teaching logic, and the usable content.",
                    ],
                },
            },
        ],
    },
    "data-methods": {
        "title": {
            "de": "Daten & Methodik",
            "en": "Data & methods",
        },
        "page_kind": "reading",
        "sections": [
            {
                "heading": {
                    "de": "Welche Daten entstehen",
                    "en": "What data is produced",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> arbeitet mit Sprachaufnahmen von Lernenden und Referenzsprecher:innen. Zu jeder Aufnahme gehören Metadaten, die die wissenschaftliche Einordnung ermöglichen, ohne Klardaten in der WebApp offenzulegen. Dazu zählen je nach Sprechergruppe unter anderem Zielsprache, Sprecherstatus, Sprachniveau, Erstsprache, Geschlecht, Aufnahmejahr, Aufnahmekontext, Aufenthalte im Zielsprachenraum oder bei Referenzsprecher:innen Angaben zu Herkunft und Standardvarietät.",
                        "Die Daten werden pseudonymisiert geführt. Klardaten, Einwilligungen und organisatorische Dokumente bleiben getrennt von der Forschungsumgebung. Die WebApp arbeitet nicht mit Klarnamen, sondern mit stabilen Personen- und Session-IDs. Diese Trennung ist Grundlage dafür, dass die Daten wissenschaftlich nutzbar sind und zugleich datenschutzgerecht verwaltet werden.",
                        "Neben den Audioaufnahmen entstehen strukturierte Begleitdaten: Aufgabenlisten, Item-IDs, Transkripte, Zeitmarken, Alignment-Daten, Interviewsegmente und Materialverweise. Ziel ist nicht eine bloße Sammlung von Audiodateien, sondern ein analysierbares Korpus, in dem Aufnahmen, Aufgaben, Metadaten und WebApp-Funktionen zusammenpassen.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> works with speech recordings from learners and reference speakers. Each recording is accompanied by metadata that allows scholarly classification without disclosing clear names in the web app. Depending on the speaker group, this may include target language, speaker status, language level, first language, gender, year of recording, recording context, stays in the target-language area, or, for reference speakers, information on origin and standard variety.",
                        "The data is managed in pseudonymised form. Clear names, consent forms, and organisational documents remain separate from the research environment. The web app does not work with clear names, but with stable person and session IDs. This separation is the basis for making the data usable for research while managing it in accordance with data-protection requirements.",
                        "In addition to the audio recordings, structured accompanying data is produced: task lists, item IDs, transcripts, timestamps, alignment data, interview segments, and material references. The aim is not simply to collect audio files, but to create an analysable corpus in which recordings, tasks, metadata, and web app functions fit together.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Aufgabenformate",
                    "en": "Task formats",
                },
                "paragraphs_html": {
                    "de": [
                        "Die Projektkorpora arbeiten mit mehreren Aufgabenformaten. Projektweit wichtig sind Wortliste, Satz- bzw. Textaufgabe und Interview. Die genaue Ausgestaltung kann je nach Sprache variieren und wird in den jeweiligen Korpusbereichen beschrieben.",
                        "Die Wortliste dient der kontrollierten Erhebung isolierter Aussprache. Sie ist kein Übungsmaterial, sondern ein Elizitationsinstrument. Die Items werden so ausgewählt, dass relevante Aussprachephänomene mehrfach und unter vergleichbaren Bedingungen auftreten. Dabei stehen Intelligibilität, systematische Realisationen und Kontraste im Vordergrund, nicht eine möglichst große Nähe zu einem einzelnen muttersprachlichen Ideal.",
                        "Die Satz- oder Textaufgabe ergänzt die Wortliste. Sie prüft, wie Aussprachemuster unter satzprosodischen oder zusammenhängenden Bedingungen auftreten. Für einzelne Korpora kann dies als Satzliste oder als zusammenhängender Text umgesetzt sein. Entscheidend ist, dass die Aufgabe nicht zufällig aus beliebigen Texten besteht, sondern auf die jeweilige Forschungslogik zugeschnitten wird.",
                        "Das Interview ergänzt die kontrollierten Leseaufgaben um eine reflexive und weniger stark gesteuerte Komponente. Lernende können über ihre eigene Aussprache, wahrgenommene Schwierigkeiten und auffällige Stellen im Material sprechen. Dadurch wird nicht nur dokumentiert, wie bestimmte Formen realisiert werden, sondern auch, wie Lernende Aussprache wahrnehmen und beschreiben.",
                    ],
                    "en": [
                        "The project corpora work with several task formats. Across the project, the wordlist, sentence or text task, and interview are central. The exact design may vary by language and is described in the respective corpus areas.",
                        "The wordlist is used for the controlled elicitation of isolated pronunciation. It is not practice material, but an elicitation instrument. Items are selected so that relevant pronunciation phenomena occur repeatedly and under comparable conditions. The focus is on intelligibility, systematic realisations, and contrasts, not on maximum proximity to a single native-speaker ideal.",
                        "The sentence or text task complements the wordlist. It examines how pronunciation patterns occur under sentence-prosodic or connected conditions. For individual corpora, this may be implemented as a sentence list or as a connected text. What matters is that the task does not consist of arbitrary texts, but is tailored to the respective research logic.",
                        "The interview adds a reflective and less tightly controlled component to the controlled reading tasks. Learners can talk about their own pronunciation, perceived difficulties, and notable points in the material. This makes it possible not only to document how certain forms are realised, but also to examine how learners perceive and describe pronunciation.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Lernendengerechte Item-Auswahl",
                    "en": "Learner-oriented item selection",
                },
                "paragraphs_html": {
                    "de": [
                        "Die Aufgabenitems werden nicht nur nach fachlichen Phänomenlisten ausgewählt. Sie müssen auch für Lernende bearbeitbar sein. Ein Item kann phonologisch interessant sein und trotzdem ungeeignet, wenn es unnötig selten, morphologisch komplex, stark kulturgebunden oder für die Zielgruppe kaum lesbar ist.",
                        _link_marele("Eine zentrale Erfahrung aus MAR.ELE war, dass vorhandene Forschungsdesigns und etablierte Materiallisten wichtige Anknüpfungspunkte bieten, aber nicht automatisch zu einem lernendengerechten Aussprachekorpus passen. <em>Pronunciation Matters</em> nutzt diese Erfahrung. Wo vorhandene Projekte, Korpora oder Aufgabenformate tragfähig sind, können sie als Referenz dienen. Wo sie für Lernende zu viele Nebenprobleme erzeugen, werden sie angepasst oder durch eigene, kontrollierte Formate ersetzt."),
                        "Für die Wortlisten bedeutet das: Die Itemauswahl ist phonologisch motiviert, aber auf Lesbarkeit und Zielgruppenangemessenheit geprüft. Relevante Phänomene sollen mehrfach vorkommen, ohne dass die Liste offen nach Phänomenen sortiert ist. Dadurch wird strategisches oder metasprachlich gesteuertes Lesen reduziert.",
                        "Für Satz- und Textaufgaben bedeutet das: Die Materialien sollen verständlich und formal kontrolliert sein. Bei Satzlisten werden Items aus der Wortliste unter satzprosodischen Bedingungen erneut aufgegriffen, ohne neue Aussprachephänomene ungeprüft einzuführen. Bei zusammenhängenden Texten wird darauf geachtet, dass die Struktur des Materials zur jeweiligen Forschungsfrage passt.",
                    ],
                    "en": [
                        "Task items are not selected solely according to lists of linguistic phenomena. They must also be manageable for learners. An item may be phonologically interesting and still unsuitable if it is unnecessarily rare, morphologically complex, strongly culture-specific, or hardly readable for the target group.",
                        _link_marele("A central lesson from MAR.ELE was that existing research designs and established material lists provide important points of connection, but do not automatically fit a learner-oriented pronunciation corpus. <em>Pronunciation Matters</em> uses this experience. Where existing projects, corpora, or task formats are suitable, they can serve as references. Where they create too many additional problems for learners, they are adapted or replaced by controlled formats developed for the project."),
                        "For the wordlists, this means that item selection is phonologically motivated, but checked for readability and suitability for the target group. Relevant phenomena should occur repeatedly without the list being openly ordered by phenomenon. This reduces strategic or metalinguistically controlled reading.",
                        "For sentence and text tasks, this means that the materials should be comprehensible and formally controlled. In sentence lists, items from the wordlist are taken up again under sentence-prosodic conditions without introducing new pronunciation phenomena without control. In connected texts, attention is paid to whether the structure of the material fits the respective research question.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Audioaufbereitung und Annotation",
                    "en": "Audio processing and annotation",
                },
                "paragraphs_html": {
                    "de": [
                        "Die zeitliche Struktur der Aufnahmen entsteht bei Wortliste und Satz- bzw. Textaufgaben nicht durch eine pauschale automatische Transkription. Stattdessen wird ein kontrollierter Audio- und Alignment-Workflow verwendet.",
                        "Zunächst werden die Audioaufnahmen in einem verlustfreien Arbeitsformat vorbereitet. Relevante Aufnahmen werden gesäubert, und zwischen den Items werden standardisierte Pausen gesetzt. Diese Pausen sind kein nebensächlicher Bearbeitungsschritt. Sie ermöglichen es, die Aufnahmen zuverlässig in Item- oder Satzsegmente zu zerlegen.",
                        "Für die Segmentierung wird Praat eingesetzt. Über Praat-Annotationen und Scripts können Itemgrenzen erkannt und mit den festen Masterlisten des jeweiligen Materials verbunden werden. Bei Wortlisten lassen sich die sounding-Intervalle den einzelnen Items zuordnen. Bei Satzlisten und Textsegmenten werden die Segmentgrenzen mit den kanonischen Materialkatalogen abgeglichen.",
                        "Für Satz- und Textaufgaben wird zusätzlich Montreal Forced Aligner genutzt. Dabei werden Audio, Transkript bzw. Mastertext, Akustikmodell und Aussprachelexikon zusammengeführt, um Wortgrenzen innerhalb der Segmente zu erzeugen. So entstehen Zeitmarken, die nicht nur ganze Items, sondern bei geeigneten Daten auch einzelne Wörter innerhalb von Sätzen oder Textabschnitten abbilden können.",
                        "Die Ergebnisse werden in strukturierte Zielformate überführt. TextGrid-Dateien, Alignment-Daten und kanonische JSON-Strukturen bilden die Grundlage für den späteren Player, für Hervorhebungen im Text und für gezielte Vergleichsfunktionen in der WebApp.",
                    ],
                    "en": [
                        "For wordlist and sentence or text tasks, the temporal structure of the recordings is not produced by general automatic transcription. Instead, a controlled audio and alignment workflow is used.",
                        "First, the audio recordings are prepared in a lossless working format. Relevant recordings are cleaned, and standardised pauses are inserted between items. These pauses are not a minor editing step. They make it possible to segment the recordings reliably into item or sentence units.",
                        "Praat is used for segmentation. Praat annotations and scripts can identify item boundaries and connect them with the fixed master lists of the respective material. In wordlists, the sounding intervals can be assigned to individual items. In sentence lists and text segments, the segment boundaries are checked against the canonical material catalogues.",
                        "For sentence and text tasks, Montreal Forced Aligner is additionally used. Audio, transcript or master text, acoustic model, and pronunciation dictionary are combined to generate word boundaries within the segments. This produces timestamps that can represent not only whole items, but, where the data is suitable, individual words within sentences or text passages.",
                        "The results are transferred into structured target formats. TextGrid files, alignment data, and canonical JSON structures form the basis for the later player, for highlighting in the text, and for targeted comparison functions in the web app.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Interviewtranskription",
                    "en": "Interview transcription",
                },
                "paragraphs_html": {
                    "de": [
                        "Für Interviews gilt eine andere Logik als für Wortlisten und Satz- bzw. Textaufgaben. Das Interview ist nicht primär ein phonetisches Feinalignment, sondern ein inhaltlich auswertbares Gespräch über Aussprache, Aufgabenwahrnehmung und subjektive Schwierigkeiten.",
                        "Die Interviewtranskripte folgen einem einfachen, inhaltsorientierten Transkriptionsschema in Anlehnung an Dresing/Pehl. Ergänzend werden wenige für das Projekt relevante Phänomene standardisiert mitgeführt: Fülllaute, Selbstkorrekturen und Abbrüche, relevante kurze Pausen sowie relevantes Lachen oder Seufzen. Auf eine gesprächsanalytische Feinnotation, detaillierte Prosodiemarkierung oder phonetische Detailtranskription wird bewusst verzichtet.",
                        "Für die Interviewbearbeitung kann ein automatisch erzeugtes Rohtranskript als Arbeitsgrundlage genutzt werden. Dieses Rohtranskript wird redaktionell überprüft. Sprecherzuordnung, Segmentierung, Interpunktion, Fülllaute und relevante Materialverweise werden korrigiert oder ergänzt. Anschließend wird der Export per Script in ein kanonisches PROMAT-Interview-JSON transformiert.",
                        "Die Interviewdaten sind segmentbasiert. Das heißt: Sprecherwechsel und Gesprächssegmente sind die primäre Struktur. Tokenzeiten können für Anzeige, Suche, Hervorhebung oder spätere Erweiterungen erhalten bleiben, werden aber nicht als phonetisch hochpräzises Feinalignment behauptet.",
                    ],
                    "en": [
                        "Interviews follow a different logic from wordlists and sentence or text tasks. The interview is not primarily a phonetic fine alignment, but a content-oriented conversation about pronunciation, task perception, and subjective difficulties.",
                        "The interview transcripts follow a simple content-oriented transcription scheme based on Dresing/Pehl. In addition, a small number of phenomena relevant to the project are retained in standardised form: filled pauses, self-repairs and cut-offs, relevant short pauses, and relevant laughter or sighing. Conversation-analytic fine notation, detailed prosodic marking, and phonetic detail transcription are deliberately not used.",
                        "For interview processing, an automatically generated raw transcript can be used as a working basis. This raw transcript is reviewed editorially. Speaker assignment, segmentation, punctuation, filled pauses, and relevant material references are corrected or added. The export is then transformed by script into a canonical PROMAT interview JSON.",
                        "The interview data is segment-based. This means that speaker changes and conversation segments are the primary structure. Token times can be retained for display, search, highlighting, or later extensions, but they are not presented as phonetically precise fine-alignment data.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Intake, Pseudonymisierung und Datenintegration",
                    "en": "Intake, pseudonymisation, and data integration",
                },
                "paragraphs_html": {
                    "de": [
                        "Vor dem Import in die WebApp durchlaufen die Daten einen Intake-Prozess. Dieser Prozess dient der kontrollierten Erfassung und Prüfung von Teilnehmendendaten, Sessiondaten, Dokumentverweisen und aufnahmebezogenen Informationen. Er ist nicht die Forschungsdatenbank selbst, sondern eine vorbereitende Arbeits- und Prüfschicht.",
                        "Klardaten und Einwilligungsdokumente bleiben im Secure-Bereich. Pseudonymisierte Personendaten, Sessiondaten und Exposure-Angaben werden getrennt davon erfasst. Eine stabile <code>person_id</code> verbindet die Ebenen, ohne Klarnamen in die Forschungsdaten zu übernehmen. Die finale <code>session_id</code> wird nicht frei manuell erfunden, sondern aus den geprüften Sessioninformationen erzeugt.",
                        "Nach der Erfassung werden Audio-, Annotation- und Metadaten in eine Zielstruktur überführt. Dort liegen Rohdaten, bearbeitete Arbeitsdateien, Alignment-Dateien, Web-Derivate und itembezogene Audiodateien getrennt vor. Scripts integrieren die Daten in die WebApp und in die Forschungsdatenstruktur. Dadurch bleibt nachvollziehbar, welche Dateien ursprüngliche Aufnahmen sind, welche Dateien Bearbeitungsergebnisse darstellen und welche Artefakte für die Webnutzung bereitgestellt werden.",
                    ],
                    "en": [
                        "Before data is imported into the web app, it passes through an intake process. This process serves the controlled collection and checking of participant data, session data, document references, and recording-related information. It is not the research database itself, but a preparatory working and review layer.",
                        "Clear names and consent documents remain in the secure area. Pseudonymised person data, session data, and exposure information are recorded separately. A stable <code>person_id</code> connects the layers without transferring clear names into the research data. The final <code>session_id</code> is not freely invented by hand, but generated from the checked session information.",
                        "After collection, audio, annotation, and metadata are transferred into a target structure. There, raw data, processed working files, alignment files, web derivatives, and item-level audio files are kept separate. Scripts integrate the data into the web app and research data structure. This keeps it traceable which files are original recordings, which files are processing results, and which artefacts are provided for web use.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "WebApp als Forschungsinstrument",
                    "en": "The web app as a research instrument",
                },
                "paragraphs_html": {
                    "de": [
                        "Die WebApp ist nicht nur ein Ablageort für Audiodateien. Sie ist ein Arbeitsinstrument für Forschung und Hochschullehre.",
                        "Nutzer:innen können Aufnahmen gezielt aufrufen, Aufgabenformate wechseln und Sprecher:innen vergleichen. Der Player verbindet Audio, Zeitmarken und Materialtexte, sodass Wortlisten, Satzlisten, Texte und Interviews jeweils in einer passenden Darstellung genutzt werden können.",
                        "Für vergleichende Analysen bietet die WebApp eigene Forschungsoberflächen. Aufzeichnungen können nach Personen, Sessions, Aufgabenformaten oder phänomenbezogenen Zusammenstellungen untersucht werden. Für die Analyse bestimmter Aussprachephänomene lassen sich Sets von Items vorauswählen, anlegen und modifizieren. Solche Sets können anschließend in Vergleichsansichten oder im Player genutzt werden, ohne dass die zugrunde liegenden Datenstrukturen von Hand bearbeitet werden müssen.",
                        "Referenzaufnahmen spielen dabei eine besondere Rolle. Sie bilden in den jeweiligen Sprachen wichtige Standardaussprachen ab und dienen nicht als eigenes Untersuchungsobjekt. Ihre Funktion besteht darin, ein tertium comparationis bereitzustellen: Lernendenaussprache und Zielaussprache können anhand derselben Items akustisch sauber miteinander verglichen werden. Die Referenzaufnahmen sind damit keine einfache Normfolie, sondern eine kontrollierte Vergleichsachse für Forschung, Lehre und Materialentwicklung.",
                        "Diese Funktionen sind besonders für die Hochschullehre relevant. Studierende können nicht nur einzelne Beispiele anhören, sondern systematisch mit ausgewählten Daten arbeiten: etwa um segmentale Kontraste, prosodische Muster, typische Lernendenschwierigkeiten oder Unterschiede zwischen Lernenden- und Referenzaufnahmen zu untersuchen.",
                    ],
                    "en": [
                        "The web app is not merely a storage location for audio files. It is a working instrument for research and university teaching.",
                        "Users can access recordings, switch between task formats, and compare speakers in targeted ways. The player connects audio, timestamps, and material texts so that wordlists, sentence lists, texts, and interviews can each be used in an appropriate display format.",
                        "The web app provides dedicated research surfaces for comparative analyses. Recordings can be investigated by persons, sessions, task formats, or phenomenon-based selections. For the analysis of specific pronunciation phenomena, sets of items can be preselected, created, and modified. These sets can then be used in comparison views or in the player without requiring users to edit the underlying data structures by hand.",
                        "Reference recordings have a special role in this context. They represent important standard pronunciations in the respective languages and do not serve as an independent object of investigation. Their function is to provide a tertium comparationis: learner pronunciation and target pronunciation can be compared acoustically and systematically using the same items. The reference recordings are therefore not a simple normative template, but a controlled axis of comparison for research, teaching, and material development.",
                        "These functions are especially relevant for university teaching. Students can do more than listen to isolated examples; they can work systematically with selected data, for example to investigate segmental contrasts, prosodic patterns, typical learner difficulties, or differences between learner and reference recordings.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Zugriff, Schutz und Veröffentlichung",
                    "en": "Access, protection, and publication",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> unterscheidet zwischen geschützten Forschungsdaten und öffentlich freigegebenen Materialien.",
                        "Geschützte Forschungsdaten umfassen insbesondere Sprachaufnahmen, pseudonymisierte Metadaten, Playerzugänge, detaillierte Vergleichsansichten und Arbeitsflächen zur phänomenbezogenen Auswahl. Diese Bereiche stehen nicht frei im öffentlichen Web, weil Stimme und Metadaten auch in pseudonymisierter Form sensible Forschungsdaten bleiben.",
                        "Öffentliche Inhalte sind Projektinformationen, allgemeine Methodenbeschreibungen, sprachspezifische Designinformationen und freigegebene Unterrichtsmaterialien. Unterrichtsmaterialien können aus der Forschungsarbeit hervorgehen, werden aber erst nach fachlicher und rechtlicher Prüfung öffentlich bereitgestellt.",
                        "Auf diese Weise verbindet die Plattform Transparenz und Schutz. Das Projekt soll nachvollziehbar sein und Materialien für Lehre und Unterricht verfügbar machen, ohne personenbezogene Forschungsdaten unkontrolliert zu veröffentlichen.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> distinguishes between protected research data and publicly released materials.",
                        "Protected research data includes, in particular, speech recordings, pseudonymised metadata, player access, detailed comparison views, and work surfaces for phenomenon-based selection. These areas are not freely available on the public web because voice and metadata remain sensitive research data even in pseudonymised form.",
                        "Public content includes project information, general methodology descriptions, language-specific design information, and released teaching materials. Teaching materials can emerge from the research work, but they are published only after disciplinary and legal review.",
                        "In this way, the platform connects transparency and protection. The project should be understandable and make materials available for teaching, without publishing personal research data in an uncontrolled way.",
                    ],
                },
            },
        ],
    },
    "team": {
        "title": {
            "de": "Team & Mitwirkende",
            "en": "Team & contributors",
        },
        "page_kind": "reading",
        "sections": [
            {
                "heading": {
                    "de": "Projektleitung und Koordination",
                    "en": "Project lead and coordination",
                },
                "meta_cards_layout": "team-lead",
                "meta_cards": [
                    {
                        "title": {
                            "de": "Gesamtprojektleitung",
                            "en": "Project lead",
                        },
                        "text": "Prof. Dr. Felix Tacke",
                        "modifier": "pm-meta-card--lead",
                        "metadata_rows": {
                            "de": [
                                {
                                    "label": "Funktion",
                                    "value": "Gesamtprojektleitung und digitale Projektarchitektur",
                                },
                                {
                                    "label": "Schwerpunkte",
                                    "value": "Konzeption, mehrsprachiger Plattformaufbau, Forschungsdatenmodellierung, Datenpipelines, WebApp-Entwicklung",
                                },
                            ],
                            "en": [
                                {
                                    "label": "Role",
                                    "value": "Overall project lead and digital project architecture",
                                },
                                {
                                    "label": "Focus areas",
                                    "value": "Conception, multilingual platform development, research data modelling, data pipelines, web app development",
                                },
                            ],
                        },
                    },
                    {
                        "title": {
                            "de": "Ausführende Koordination",
                            "en": "Executive coordination",
                        },
                        "text": "Marlon Merte",
                        "modifier": "pm-meta-card--lead",
                        "metadata_rows": {
                            "de": [
                                {
                                    "label": "Funktion",
                                    "value": "Ausführende Koordination der Aufnahmen und korpusübergreifenden Arbeitsabläufe",
                                },
                                {
                                    "label": "Schwerpunkte",
                                    "value": "Aufnahmeorganisation, Postproduktion, operative Korpusarbeit, Durchführung im Spanisch- und Englischbereich",
                                },
                            ],
                            "en": [
                                {
                                    "label": "Role",
                                    "value": "Executive coordination of recordings and cross-corpus workflows",
                                },
                                {
                                    "label": "Focus areas",
                                    "value": "Recording organisation, post-production, operative corpus work, implementation in the Spanish and English areas",
                                },
                            ],
                        },
                    },
                ],
            },
            {
                "heading": {
                    "de": "Sprachkorpora",
                    "en": "Language corpora",
                },
                "meta_cards_layout": "team-corpus",
                # Filled from content/publication/resources.yaml (public_content._fill_team_corpus_cards).
                "meta_cards": [],
            },
            {
                "heading": {
                    "de": "Sprachenzentrum",
                    "en": "Language Center",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> arbeitet mit dem Sprachenzentrum der Philipps-Universität Marburg zusammen, wo mit Unterstützung der Lehrenden Teilnehmende für das Projekt gewonnen werden konnten.",
                        "Besonderer Dank gilt Dr. Edmund Voges für die Unterstützung im Bereich Spanisch und Ariane Wenz für die Unterstützung im Bereich Französisch.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> cooperates with the Language Center of Philipps-Universität Marburg, where participants could be recruited for the project with the support of its teachers.",
                        "Special thanks go to Dr. Edmund Voges for his support in the Spanish area and to Ariane Wenz for her support in the French area.",
                    ],
                },
            },
            {
                "heading": {
                    "de": "Dank",
                    "en": "Acknowledgements",
                },
                "paragraphs_html": {
                    "de": [
                        "<em>Pronunciation Matters</em> dankt allen Studierenden und weiteren Teilnehmenden, die ihre Sprachdaten für das Projekt zur Verfügung gestellt haben.",
                        "Besonderer Dank gilt den Referenzsprecher:innen. Ihre Aufnahmen bilden wichtige Standardaussprachen ab und dienen als tertium comparationis, damit Lernendenaussprache und Zielaussprache anhand derselben Items verglichen werden können.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> thanks all students and other participants who made their speech data available to the project.",
                        "Special thanks go to the reference speakers. Their recordings represent important standard pronunciations and serve as a tertium comparationis so that learner pronunciation and target pronunciation can be compared using the same items.",
                    ],
                },
                "bullets": {
                    "de": [
                        "Dr. Pedro Alonso",
                        "Ana Goás Pérez",
                        "Aoife Holmes-Rein, M.A.",
                    ],
                    "en": [
                        "Dr. Pedro Alonso",
                        "Ana Goás Pérez",
                        "Aoife Holmes-Rein, M.A.",
                    ],
                },
            },
        ],
    },
}


SPANISH_DESIGN_PAGE_CONTENT: dict[str, object] = {
    "title": {
        "de": "Die Aussprache von Spanischlernenden erfassen: Das Erhebungsdesign des spanischen Korpus von Pronunciation Matters",
        "en": "Capturing the Pronunciation of Spanish Learners: The Data Collection Design of the Spanish Corpus of Pronunciation Matters",
    },
    "title_html": {
        "de": "Die Aussprache von Spanischlernenden erfassen: Das Erhebungsdesign des spanischen Korpus von <em>Pronunciation Matters</em>",
        "en": "Capturing the Pronunciation of Spanish Learners: The Data Collection Design of the Spanish Corpus of <em>Pronunciation Matters</em>",
    },
    "article_header": {
        "de": {
            "abstract_html": "Der Beitrag stellt das Erhebungsdesign des spanischen Lernendenkorpus von <em>Pronunciation Matters</em> vor. Ausgehend von etablierten korpusphonologischen Protokollen und den Erfahrungen des Vorgängerprojekts MAR.ELE werden die Entwicklung einer phonologisch motivierten Wortliste, einer kontrollierten Satzliste und einer ergänzenden Interviewkomponente erläutert. Im Mittelpunkt stehen die systematische Erhebung ausgewählter Aussprachephänomene, die Vergleichbarkeit isolierter und satzgebundener Realisierungen sowie die Anpassung der Aufgaben an die Voraussetzungen von Spanischlernenden. Der Beitrag begründet die zentralen Auswahlentscheidungen und diskutiert die Reichweite und Grenzen des Protokolls.",
            "keywords": [
                "Spanisch als Fremdsprache",
                "Lernendenphonetik",
                "Korpusphonologie",
                "Aussprache",
                "Erhebungsdesign",
            ],
        },
        "en": {
            "abstract_html": "This article presents the data collection design of the Spanish learner corpus of <em>Pronunciation Matters</em>. Drawing on established corpus-phonological protocols and the experience of the predecessor project MAR.ELE, it explains the development of a phonologically motivated wordlist, a controlled sentence list and a supplementary interview component. The focus is on the systematic elicitation of selected pronunciation phenomena, the comparability of isolated and sentence-bound realisations, and the adaptation of the tasks to the prerequisites of Spanish learners. The article justifies the central selection decisions and discusses the scope and limitations of the protocol.",
            "keywords": [
                "Spanish as a foreign language",
                "learner phonetics",
                "corpus phonology",
                "pronunciation",
                "data collection design",
            ],
        },
    },
    "nav_current_label": {
        "de": "Erhebungsdesign",
        "en": "Data Collection Design",
    },
    "eyebrow": {
        "de": "Forschung · Spanisch",
        "en": "Research · Spanish",
    },
    "page_kind": "reading",
    "access": "public",
    "sections": [
        {
            "heading": {
                "de": "Forschungskontext und Zielsetzung",
                "en": "Research context and aims",
            },
            "paragraphs_html": {
                "de": [
                    'Das spanische Korpus von <em>Pronunciation Matters</em> setzt dort an, wo sich zwei Entwicklungen berühren: einerseits korpusphonologische Erhebungsdesigns, die Aussprache kontrolliert und vergleichbar dokumentieren wollen, andererseits eine ELE-Didaktik und universitäre Phonetik/Phonologie, in der Aussprache als Lerngegenstand und die Aussprache Lernender als Forschungsgegenstand zunehmend ausdrücklich mitgedacht werden.<sup class="pm-footnote-ref" id="fnref-spanish-design-1-de"><a href="#fn-spanish-design-1-de" aria-label="Fußnote 1">1</a></sup> Empirische Daten zur Aussprache Lernender entstehen dabei nicht voraussetzungslos: Sie werden über Aufgabenformate gesteuert, die bestimmen, welche sprachlichen Einheiten gelesen oder gesprochen werden, unter welchen Bedingungen dies geschieht und wie vergleichbar die entstehenden Aufnahmen sind.',
                    "Ziel ist daher ein Aufgabenprotokoll, das zentrale Phänomene spanischer Lernendenaussprache systematisch erhebt, ohne die Erhebung durch unnötig schwierige Lexik, komplexe Lesetexte oder eine implizite Orientierung an erstsprachlichen Zielnormen zu überfrachten.",
                    "Dass Aussprache als Lerngegenstand und Lernendenaussprache als Forschungsgegenstand inzwischen stärker in die spanische Phonetik und Phonologie integriert werden, zeigt sich auch in einschlägigen Einführungen der deutschsprachigen Hispanistik: Pustka (2021) widmet der „Aussprache im Fremdsprachenunterricht“ bereits zu Beginn ihrer korpuslinguistischen Einführung ein eigenes Kapitel; Gabriel/Meisenburg/Selig (2025) nehmen in der zweiten, überarbeiteten Auflage erstmals ein eigenes Kapitel zu „Spanisch als Fremdsprache im deutschsprachigen Kontext“ auf, mit Abschnitten zu segmentalen Aspekten und Prosodie.",
                    "<em>Pronunciation Matters</em> knüpft an diese Entwicklung an und ergänzt sie um eine Plattform, die kontrolliert erhobene Lernendendaten für empirische Untersuchungen, forschungsnahe Hochschullehre und didaktische Anschlussfragen zugänglich macht.",
                    "Die didaktische Perspektive schließt zugleich an grundlegende Arbeiten zur Aussprachevermittlung im ELE-Unterricht an, insbesondere Gil Fernández (2007), und an praxisorientierte Beiträge zur Arbeit mit Fremdakzent im Unterricht wie Benet/Pešková (2017). Auch neuere ELE-didaktische Arbeiten bestimmen Aussprache nicht primär über die Annäherung an erstsprachliche Normen, sondern über Intelligibilität, Verständlichkeit und kommunikative Funktion (vgl. Santamaría Busto 2024; Bárkányi/Galindo Merino/Pérez-Bernabeu 2024).",
                    "Aus dieser doppelten Verortung ergibt sich die zentrale Designentscheidung des spanischen Aufgabenprotokolls: Bestehende Modelle bieten wichtige Vorarbeiten, können für die gezielte Untersuchung von Lernendenaussprache aber nur teilweise direkt übernommen werden. Das betrifft vor allem Wortschatzschwierigkeit, inhaltliche Ablenkungen durch Lesetexte und die Frage, welche lautlichen Phänomene mehrfach und kontrolliert erhoben werden müssen.",
                    "Leitend sind daher Intelligibilität, kontrollierte Elizitation, empirische Vergleichbarkeit und eine für Lernende sinnvolle Materialgestaltung.",
                ],
                "en": [
                    'The Spanish corpus of <em>Pronunciation Matters</em> is situated where two developments meet: on the one hand, corpus-phonological elicitation designs that aim to document pronunciation in a controlled and comparable way; on the other, ELE didactics and university-level phonetics and phonology, in which pronunciation as an object of learning and learner pronunciation as an object of research are increasingly being considered explicitly.<sup class="pm-footnote-ref" id="fnref-spanish-design-1-en"><a href="#fn-spanish-design-1-en" aria-label="Footnote 1">1</a></sup> Empirical data on learner pronunciation do not arise without prior structuring: they are shaped by task formats that determine which linguistic units are read or spoken, under what conditions this happens and how comparable the resulting recordings are.',
                    "The aim is therefore a task protocol that systematically elicits central phenomena of Spanish learner pronunciation without overburdening the elicitation with unnecessarily difficult vocabulary, complex reading passages or an implicit orientation towards first-language target norms.",
                    "That pronunciation as an object of learning and learner pronunciation as an object of research are now being integrated more strongly into Spanish phonetics and phonology is also evident in relevant introductions in German-language Hispanic studies: Pustka (2021) devotes a separate chapter to “pronunciation in foreign language teaching” right at the beginning of her corpus-linguistic introduction; Gabriel/Meisenburg/Selig (2025), in the second, revised edition, include for the first time a separate chapter on “Spanish as a foreign language in the German-speaking context”, with sections on segmental aspects and prosody.",
                    "<em>Pronunciation Matters</em> builds on this development and complements it with a platform that makes controlled learner data available for empirical research, research-oriented university teaching and didactic follow-up questions.",
                    "The didactic perspective also connects with foundational work on teaching pronunciation in ELE, in particular Gil Fernández (2007), and with practice-oriented contributions on dealing with foreign accent in the classroom such as Benet/Pešková (2017). More recent ELE-didactic work, too, defines pronunciation not primarily through approximation to first-language norms, but through intelligibility, comprehensibility and communicative function (cf. Santamaría Busto 2024; Bárkányi/Galindo Merino/Pérez-Bernabeu 2024).",
                    "This twofold positioning leads to the central design decision of the Spanish task protocol: existing models offer important groundwork, but can only partly be adopted directly for the targeted study of learner pronunciation. This concerns above all lexical difficulty, content-related distraction through reading passages, and the question of which phonetic phenomena have to be elicited repeatedly and under controlled conditions.",
                    "The guiding principles are therefore intelligibility, controlled elicitation, empirical comparability and a material design that makes sense for learners.",
                ],
            },
        },
        {
            "heading": {
                "de": "Vorarbeiten und empirische Ausgangslage",
                "en": "Previous work and empirical starting point",
            },
            "paragraphs_html": {
                "de": [
                    'Ein wichtiger Zwischenschritt war das frühere Projekt <a href="https://hispanistica.com/projects/marele/">MAR.ELE</a> – <em>Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg</em>. In diesem kleineren Vorprojekt wurden 22 Aufnahmen mit Studierenden der Universität Marburg erstellt. MAR.ELE diente dazu, spanische Lernendenaussprache als Korpusmaterial zugänglich und empirisch auswertbar zu machen.',
                    'In der praktischen Arbeit mit diesem Korpus wurden jedoch auch die Grenzen eines stark übernommenen Designs sichtbar. Gerade diese Erfahrungen waren entscheidend für die weitergehende Überarbeitung im vorliegenden Projekt und stehen zugleich in engem Zusammenhang mit der allgemeinen Projektentwicklung, die <a href="/de/project/about">hier</a> nachgelesen werden kann.',
                    "Für MAR.ELE wurde die Wortliste des Projekts (I)FEC vollständig übernommen, um die Anschlussfähigkeit an ein etabliertes korpusphonologisches Design des Spanischen zu sichern. Das war methodisch sinnvoll, zeigte in der Arbeit mit Lernenden jedoch auch deutliche Grenzen: Einige Items erwiesen sich als unnötige lexikalische Stolperstellen, was sich unter anderem in wiederholten Leseversuchen, Versprechern (etwa Laut- und Silbenvertauschungen), Lautersetzungen, spontanen Reaktionen wie Lachen oder Schmunzeln sowie gelegentlichen Leseabbrüchen äußerte. In solchen Fällen ließ sich nicht immer eindeutig bestimmen, ob auffällige Realisierungen auf systematische Aussprachemuster oder auf Schwierigkeiten beim Erfassen der geschriebenen Wortform zurückgingen. Zugleich waren einige für die Lernendenaussprache besonders aufschlussreiche Phänomene im Material nicht ausreichend oder nicht ausgewogen vertreten.",
                    "Auch der in MAR.ELE verwendete Text war als Vergleichstext nützlich, erwies sich aber für die Zielgruppe als zu voraussetzungsreich. Die Überarbeitung des Erhebungsprotokolls beruht somit wesentlich auf den praktischen Erfahrungen mit den bisherigen Materialien und den dabei erkennbar gewordenen methodischen Schwierigkeiten.",
                ],
                "en": [
                    'An important intermediate step was the earlier project <a href="https://hispanistica.com/projects/marele/">MAR.ELE</a> – <em>Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg</em>. In this smaller preliminary project, 22 recordings were made with students of Marburg University. MAR.ELE served to make Spanish learner pronunciation accessible as corpus material and open to empirical analysis.',
                    'In practical work with this corpus, however, the limits of a heavily adopted design also became visible. These very experiences were decisive for the further revision in the present project and are closely connected with the general project development, which can be read about <a href="/en/project">here</a>.',
                    "For MAR.ELE, the wordlist of the (I)FEC project was adopted in full in order to ensure compatibility with an established corpus-phonological design for Spanish. That was methodologically sensible, but it also showed clear limits in work with learners: some items proved to be unnecessary lexical stumbling blocks, which showed up, among other things, in repeated reading attempts, slips of the tongue (such as sound and syllable transpositions), sound substitutions, spontaneous reactions such as laughing or smiling, and occasional abandoned readings. In such cases it was not always possible to determine unambiguously whether conspicuous realisations were due to systematic pronunciation patterns or to difficulties in grasping the written word form. At the same time, some phenomena that are particularly revealing for learner pronunciation were not sufficiently or not evenly represented in the material.",
                    "The text used in MAR.ELE was also useful as a comparison text, but proved too demanding for the target group. The revision of the elicitation protocol is thus essentially based on practical experience with the earlier materials and the methodological difficulties that became apparent in the process.",
                ],
            },
        },
        {
            "heading": {
                "de": "Methodische Grundidee",
                "en": "Methodological starting point",
            },
            "paragraphs_html": {
                "de": [
                    "Ein zentrales Ziel korpusphonologischer Projekte besteht darin, Sprachdaten projektübergreifend vergleichbar zu erheben. Diese Logik steht auch hinter etablierten Protokollen wie PFC/IPFC für das Französische und dem daran anschließenden spanischen Projekt (I)FEC. Ausgangspunkt ist Labovs Unterscheidung unterschiedlicher Grade von Selbstkontrolle bzw. Aufmerksamkeit auf die eigene Sprache: Kontrollierte Leseaufgaben, Wortlisten, Texte und offenere Gesprächsformate erzeugen unterschiedliche Datentypen, die zusammen ein differenzierteres Bild lautlicher Variation ermöglichen (vgl. Labov 1972; Detey/Durand/Laks/Lyche 2016; Racine/Zay/Detey/Kawaguchi 2012; Pustka et al. 2018).",
                    "Diese Standardisierung schafft die Grundlage dafür, Ausspracheproduktionen verschiedener Sprecher und Lernendengruppen miteinander zu vergleichen. Die ergänzende Erfassung sprachbiographischer Angaben ermöglicht es, die erhobenen Realisierungen im jeweiligen Sprachlernkontext einzuordnen. Für <em>Pronunciation Matters</em> musste das Prinzip der Standardisierung jedoch an ein spezifisches Erkenntnisinteresse angepasst werden: Im Zentrum steht kein allgemeines Referenzkorpus für das spanische Lautsystem, sondern ein Lernendenkorpus, das möglichst störungsarme Daten zur Untersuchung von Aussprachemustern und didaktisch relevanten Kontrasten bereitstellen soll.",
                ],
                "en": [
                    "A central aim of corpus-phonological projects is to elicit speech data in a way that is comparable across projects. This logic also underlies established protocols such as PFC/IPFC for French and the Spanish project (I)FEC that builds on it. The starting point is Labov’s distinction between different degrees of self-monitoring, or attention paid to one’s own speech: controlled reading tasks, wordlists, texts and more open conversational formats produce different types of data which, taken together, allow a more differentiated picture of phonetic variation (cf. Labov 1972; Detey/Durand/Laks/Lyche 2016; Racine/Zay/Detey/Kawaguchi 2012; Pustka et al. 2018).",
                    "This standardisation creates the basis for comparing the pronunciation productions of different speakers and learner groups. The additional recording of language-biographical information makes it possible to place the elicited realisations in their respective language-learning context. For <em>Pronunciation Matters</em>, however, the principle of standardisation had to be adapted to a specific research interest: the focus is not on a general reference corpus for the Spanish sound system, but on a learner corpus that is to provide data with as little interference as possible for studying pronunciation patterns and didactically relevant contrasts.",
                ],
            },
        },
        {
            "heading": {
                "de": "Konzeption der Wortliste",
                "en": "Design of the wordlist",
            },
            "paragraphs_html": {
                "de": None,
                "en": None,
            },
            "blocks": {
                "de": [
                    {
                        "type": "paragraph_html",
                        "html": "Die (I)FEC-Wortliste ist für ein breites korpusphonologisches Programm konzipiert. Sie soll zahlreiche Phänomene des spanischen Lautsystems, regionale Variation und mögliche Kontraste erfassen. Für ein Lernendenkorpus ist diese Breite nur teilweise sinnvoll.",
                    },
                    {
                        "type": "paragraph_html",
                        "html": 'Einige Items sind phonologisch interessant, erwiesen sich aber für Lernende als unnötige Stolperstellen oder wiesen praktisch keinen analytischen Nutzen auf: morphologisch komplexe Formen wie <em>estudiéis</em>, seltene Diphthonge oder Triphthonge in Items wie <em>bou</em>, <em>miau</em> und <em>guau</em>, Lehnwörter wie <em>kétchup</em> und <em>iceberg</em> oder lexikalisch randständige Wörter wie <em>ñandú</em>, <em>yunque</em> und <em>ciempiés</em>.<sup class="pm-footnote-ref" id="fnref-spanish-design-2-de"><a href="#fn-spanish-design-2-de" aria-label="Fußnote 2">2</a></sup> Solche Wörter können dazu führen, dass nicht mehr primär Aussprache erhoben wird, sondern Wortkenntnis, Lesesicherheit oder Unsicherheit im Umgang mit unbekannten Formen vom eigentlichen Fokus ablenken.',
                    },
                    {
                        "type": "paragraph_html",
                        "html": 'Die neue Wortliste verlässt daher bewusst das Ideal einer vollständigen Protokollübernahme. Sie ist aber weiterhin stark an (I)FEC gebunden: 58 unterschiedliche Wortformen aus (I)FEC wurden übernommen.<sup class="pm-footnote-ref" id="fnref-spanish-design-3-de"><a href="#fn-spanish-design-3-de" aria-label="Fußnote 3">3</a></sup> Die Abfolge aus randomisiertem Hauptteil mit Einzellexemen und einem abschließenden Block mit Kontrastgruppen wurde ebenfalls beibehalten. Gleichzeitig wurden 31 Wortformen neu ergänzt, um die Liste besser an Lernende und an die geplanten Analysen anzupassen.<sup class="pm-footnote-ref" id="fnref-spanish-design-4-de"><a href="#fn-spanish-design-4-de" aria-label="Fußnote 4">4</a></sup> Dazu gehören u. a. Items zur besseren Abdeckung bestimmter Konsonantenphänomene, etwa finales /d/ in <em>ciudad</em>, <em>usted</em> und <em>verdad</em>. Da wortfinales /d/ in (I)FEC nicht systematisch berücksichtigt wird, wurde es bei der Konzeption der Wortliste für <em>Pronunciation Matters</em> gezielt stärker einbezogen.',
                    },
                    {
                        "type": "paragraph_html",
                        "html": "Die Wortliste wurde somit nicht neu erfunden, sondern gezielt überarbeitet. Entscheidend sind Intelligibilität, systematische Realisationen und relevante Kontraste. Die Liste umfasst 92 Aufgabenitems: 86 Einzelwörter und einen abschließenden Block mit sechs Kontrastgruppen. Darunter finden sich phonologische Kontraste wie <em>caro – carro</em> und <em>pero – perro</em>, orthographische Kontraste wie <em>ola – hola</em> und <em>bienes – vienes</em> sowie das Akzenttripel <em>número – numero – numeró</em>. Die Items sind phonologisch motiviert ausgewählt, aber lernendengerecht gefiltert.",
                    },
                    {
                        "type": "paragraph_html",
                        "html": "Bevorzugt werden hochfrequente, frühen Lernniveaus entsprechende und orthographisch möglichst transparente Wörter. Relevante Phänomene sollen mehrfach vertreten sein, in der Regel durch drei bis fünf Items, damit Einzelbeobachtungen nicht überinterpretiert werden.",
                    },
                    {
                        "type": "paragraph_html",
                        "html": "Bei der Zusammenstellung der Wortliste wurden phonetisch-phonologische und didaktische Gesichtspunkte miteinander verbunden. Berücksichtigt wurden zentrale Beschreibungsbereiche der spanischen Phonetik und Phonologie, darunter segmentale Kontraste, Silbenstruktur, Wortakzent, Graphem-Phonem-Beziehungen und prosodische Einbettung. Wichtige fachliche Bezugspunkte bilden dabei Pustka (2021) und Gabriel/Meisenburg/Selig (2025). Gerade den Graphem-Phonem-Beziehungen kommt im Spanischen auch aus didaktischer Perspektive besondere Bedeutung zu, da die vergleichsweise hohe Transparenz der Schreib-Laut-Zuordnungen nicht mit einer problemlosen Ausspracheproduktion gleichzusetzen ist (vgl. Díez Plaza 2024). Darüber hinaus berücksichtigt die Konzeption Arbeiten, die die lautliche Form als Bestandteil lexikalischen Wissens verstehen und Aussprache, phonologische Bewusstheit und Wortschatzarbeit eng miteinander verbinden (vgl. Hidalgo Gallardo/Pérez Serrano 2024).",
                    },
                    {
                        "type": "paragraph_html",
                        "html": "Wie sich diese Auswahlkriterien in der Zusammenstellung der Stimuli niederschlagen, verdeutlichen die folgenden Beispiele:",
                    },
                    {
                        "type": "table",
                        "columns": [
                            "Phänomenbereich",
                            "Wörter und Kontraste (Auswahl)",
                            "Untersuchungsperspektive",
                        ],
                        "rows": [
                            [
                                "Allophonie von /b/ und Grapheme ⟨b⟩/⟨v⟩",
                                "<em>labio, vino, lavar, vida</em>",
                                "Plosive und approximantische Realisierungen in unterschiedlichen lautlichen Kontexten; mögliche orthographisch beeinflusste Aussprache von ⟨v⟩",
                            ],
                            [
                                "Rhotische Kontraste",
                                "<em>caro – carro; pero – perro; reloj</em>",
                                "Einfache und mehrfache Vibranten sowie ihre Stellungsbedingungen",
                            ],
                            [
                                "Diphthonge",
                                "<em>viuda, deuda, tierra, baile</em>",
                                "Realisierung unterschiedlicher Vokalverbindungen innerhalb der Silbe",
                            ],
                            [
                                "Hiatus",
                                "<em>caída, oído, oír, reír</em>",
                                "Realisierung heterosyllabischer Vokalfolgen",
                            ],
                            [
                                "Konsonanten im Wortauslaut",
                                "<em>ciudad, usted, verdad</em>",
                                "Erhalt, Abschwächung oder Tilgung von finalem /d/",
                            ],
                            [
                                "Lexikalischer Wortakzent",
                                "<em>número – numero – numeró</em>",
                                "Unterscheidung bedeutungsrelevanter Akzentpositionen",
                            ],
                        ],
                    },
                    {
                        "type": "paragraph_html",
                        "html": 'Die gezielte Kombination der Stimuli ermöglicht es, einzelne Aussprachephänomene in unterschiedlichen lautlichen Kontexten zu untersuchen und ihre Realisierung gegebenenfalls zwischen isolierten Wörtern und satzgebundener Produktion zu vergleichen.<sup class="pm-footnote-ref" id="fnref-spanish-design-5-de"><a href="#fn-spanish-design-5-de" aria-label="Fußnote 5">5</a></sup>',
                    },
                    {
                        "type": "content_element",
                        "ref": "spanish-final-wordlist",
                    },
                ],
                "en": [
                    {
                        "type": "paragraph_html",
                        "html": "The (I)FEC wordlist is designed for a broad corpus-phonological programme. It is meant to capture numerous phenomena of the Spanish sound system, regional variation and possible contrasts. For a learner corpus, this breadth is only partly useful.",
                    },
                    {
                        "type": "paragraph_html",
                        "html": 'Some items are phonologically interesting but proved to be unnecessary stumbling blocks for learners or had practically no analytical use: morphologically complex forms such as <em>estudiéis</em>, rare diphthongs or triphthongs in items such as <em>bou</em>, <em>miau</em> and <em>guau</em>, loanwords such as <em>kétchup</em> and <em>iceberg</em>, or lexically marginal words such as <em>ñandú</em>, <em>yunque</em> and <em>ciempiés</em>.<sup class="pm-footnote-ref" id="fnref-spanish-design-2-en"><a href="#fn-spanish-design-2-en" aria-label="Footnote 2">2</a></sup> Such words can mean that the elicitation no longer primarily captures pronunciation, but word knowledge, reading confidence, or uncertainty with unfamiliar forms distracts from the actual focus.',
                    },
                    {
                        "type": "paragraph_html",
                        "html": 'The new wordlist therefore deliberately abandons the ideal of adopting the protocol in full. It remains, however, strongly tied to (I)FEC: 58 distinct word forms from (I)FEC were retained.<sup class="pm-footnote-ref" id="fnref-spanish-design-3-en"><a href="#fn-spanish-design-3-en" aria-label="Footnote 3">3</a></sup> The sequence of a randomised main part with individual lexemes and a final block of contrast groups was also kept. At the same time, 31 word forms were newly added in order to adapt the list better to learners and to the planned analyses.<sup class="pm-footnote-ref" id="fnref-spanish-design-4-en"><a href="#fn-spanish-design-4-en" aria-label="Footnote 4">4</a></sup> These include, among others, items that improve the coverage of certain consonant phenomena, for example final /d/ in <em>ciudad</em>, <em>usted</em> and <em>verdad</em>. Since word-final /d/ is not systematically covered in (I)FEC, it was deliberately given greater weight in designing the wordlist for <em>Pronunciation Matters</em>.',
                    },
                    {
                        "type": "paragraph_html",
                        "html": "The wordlist was thus not invented anew, but revised in a targeted way. What matters are intelligibility, systematic realisations and relevant contrasts. The list comprises 92 task items: 86 individual words and a final block of six contrast groups. Among them are phonological contrasts such as <em>caro – carro</em> and <em>pero – perro</em>, orthographic contrasts such as <em>ola – hola</em> and <em>bienes – vienes</em>, and the accent triple <em>número – numero – numeró</em>. The items are selected on phonological grounds, but filtered to suit learners.",
                    },
                    {
                        "type": "paragraph_html",
                        "html": "Preference is given to high-frequency words that match early learning levels and are as orthographically transparent as possible. Relevant phenomena should be represented repeatedly, as a rule by three to five items, so that individual observations are not over-interpreted.",
                    },
                    {
                        "type": "paragraph_html",
                        "html": "In compiling the wordlist, phonetic-phonological and didactic considerations were combined. Central areas of description in Spanish phonetics and phonology were taken into account, including segmental contrasts, syllable structure, word stress, grapheme–phoneme relations and prosodic embedding. Important reference points here are Pustka (2021) and Gabriel/Meisenburg/Selig (2025). From a didactic perspective, too, grapheme–phoneme relations are of particular importance in Spanish, since the comparatively high transparency of spelling–sound correspondences must not be equated with unproblematic pronunciation (cf. Díez Plaza 2024). In addition, the design takes into account work that understands phonetic form as a component of lexical knowledge and closely links pronunciation, phonological awareness and vocabulary work (cf. Hidalgo Gallardo/Pérez Serrano 2024).",
                    },
                    {
                        "type": "paragraph_html",
                        "html": "How these selection criteria are reflected in the compilation of the stimuli is illustrated by the following examples:",
                    },
                    {
                        "type": "table",
                        "columns": [
                            "Phenomenon area",
                            "Words and contrasts (selection)",
                            "Perspective of investigation",
                        ],
                        "rows": [
                            [
                                "Allophony of /b/ and graphemes ⟨b⟩/⟨v⟩",
                                "<em>labio, vino, lavar, vida</em>",
                                "Plosive and approximant realisations in different phonetic contexts; possible orthographically influenced pronunciation of ⟨v⟩",
                            ],
                            [
                                "Rhotic contrasts",
                                "<em>caro – carro; pero – perro; reloj</em>",
                                "Single and multiple vibrants and their positional conditions",
                            ],
                            [
                                "Diphthongs",
                                "<em>viuda, deuda, tierra, baile</em>",
                                "Realisation of different vowel combinations within the syllable",
                            ],
                            [
                                "Hiatus",
                                "<em>caída, oído, oír, reír</em>",
                                "Realisation of heterosyllabic vowel sequences",
                            ],
                            [
                                "Consonants in word-final position",
                                "<em>ciudad, usted, verdad</em>",
                                "Retention, weakening or deletion of final /d/",
                            ],
                            [
                                "Lexical stress",
                                "<em>número – numero – numeró</em>",
                                "Distinction of stress positions that carry a difference in meaning",
                            ],
                        ],
                    },
                    {
                        "type": "paragraph_html",
                        "html": 'The targeted combination of the stimuli makes it possible to examine individual pronunciation phenomena in different phonetic contexts and, where appropriate, to compare their realisation between isolated words and sentence-bound production.<sup class="pm-footnote-ref" id="fnref-spanish-design-5-en"><a href="#fn-spanish-design-5-en" aria-label="Footnote 5">5</a></sup>',
                    },
                    {
                        "type": "content_element",
                        "ref": "spanish-final-wordlist",
                    },
                ],
            },
            "content_elements": [
                {
                    "type": "pm_expandable_text",
                    "id": "spanish-final-wordlist",
                    "title": {
                        "de": "Wortliste",
                        "en": "Wordlist",
                    },
                    "summary_html": {
                        "de": "Die spanische Wortliste umfasst 92 Aufgabenitems: 86 Einzelwörter und sechs abschließende Kontrastgruppen.",
                        "en": "The Spanish wordlist comprises 92 task items: 86 individual words and six final contrast groups.",
                    },
                    "items": [
                        {"label": "1", "text": "mesa"},
                        {"label": "2", "text": "reloj"},
                        {"label": "3", "text": "viuda"},
                        {"label": "4", "text": "tabúes"},
                        {"label": "5", "text": "neutro"},
                        {"label": "6", "text": "querría"},
                        {"label": "7", "text": "caída"},
                        {"label": "8", "text": "ciudad"},
                        {"label": "9", "text": "lavar"},
                        {"label": "10", "text": "avión"},
                        {"label": "11", "text": "jamón"},
                        {"label": "12", "text": "numeró"},
                        {"label": "13", "text": "toros"},
                        {"label": "14", "text": "gente"},
                        {"label": "15", "text": "regla"},
                        {"label": "16", "text": "flor"},
                        {"label": "17", "text": "ríe"},
                        {"label": "18", "text": "hoy"},
                        {"label": "19", "text": "juzgar"},
                        {"label": "20", "text": "signo"},
                        {"label": "21", "text": "labio"},
                        {"label": "22", "text": "deuda"},
                        {"label": "23", "text": "queja"},
                        {"label": "24", "text": "euforia"},
                        {"label": "25", "text": "oír"},
                        {"label": "26", "text": "ladrón"},
                        {"label": "27", "text": "club"},
                        {"label": "28", "text": "vainilla"},
                        {"label": "29", "text": "número"},
                        {"label": "30", "text": "usted"},
                        {"label": "31", "text": "ángel"},
                        {"label": "32", "text": "giro"},
                        {"label": "33", "text": "cuidado"},
                        {"label": "34", "text": "caza"},
                        {"label": "35", "text": "logro"},
                        {"label": "36", "text": "solo"},
                        {"label": "37", "text": "mismo"},
                        {"label": "38", "text": "vino"},
                        {"label": "39", "text": "admirar"},
                        {"label": "40", "text": "sueño"},
                        {"label": "41", "text": "vacío"},
                        {"label": "42", "text": "traer"},
                        {"label": "43", "text": "jefe"},
                        {"label": "44", "text": "álbum"},
                        {"label": "45", "text": "vida"},
                        {"label": "46", "text": "ustedes"},
                        {"label": "47", "text": "chico"},
                        {"label": "48", "text": "algo"},
                        {"label": "49", "text": "ahí"},
                        {"label": "50", "text": "enfermo"},
                        {"label": "51", "text": "diablo"},
                        {"label": "52", "text": "nadie"},
                        {"label": "53", "text": "causa"},
                        {"label": "54", "text": "tirar"},
                        {"label": "55", "text": "llave"},
                        {"label": "56", "text": "perro"},
                        {"label": "57", "text": "carro"},
                        {"label": "58", "text": "cuidar"},
                        {"label": "59", "text": "tierra"},
                        {"label": "60", "text": "baile"},
                        {"label": "61", "text": "drama"},
                        {"label": "62", "text": "vienes"},
                        {"label": "63", "text": "gracias"},
                        {"label": "64", "text": "oído"},
                        {"label": "65", "text": "casa"},
                        {"label": "66", "text": "ración"},
                        {"label": "67", "text": "tampoco"},
                        {"label": "68", "text": "muchacho"},
                        {"label": "69", "text": "salud"},
                        {"label": "70", "text": "quería"},
                        {"label": "71", "text": "paz"},
                        {"label": "72", "text": "champán"},
                        {"label": "73", "text": "hambre"},
                        {"label": "74", "text": "obtiene"},
                        {"label": "75", "text": "oye"},
                        {"label": "76", "text": "reír"},
                        {"label": "77", "text": "suave"},
                        {"label": "78", "text": "lleno"},
                        {"label": "79", "text": "barrio"},
                        {"label": "80", "text": "Europa"},
                        {"label": "81", "text": "allí"},
                        {"label": "82", "text": "numero"},
                        {"label": "83", "text": "otros"},
                        {"label": "84", "text": "verdad"},
                        {"label": "85", "text": "caro"},
                        {"label": "86", "text": "bienes"},
                        {"label": "87", "text": "número – numero – numeró"},
                        {"label": "88", "text": "caro – carro"},
                        {"label": "89", "text": "ahí – allí"},
                        {"label": "90", "text": "pero – perro"},
                        {"label": "91", "text": "ola – hola"},
                        {"label": "92", "text": "bienes – vienes"},
                    ],
                },
            ],
        },
        {
            "heading": {
                "de": "Grenzen klassischer Lesetexte",
                "en": "Limitations of traditional reading passages",
            },
            "paragraphs_html": {
                "de": [
                    "Auch für den zweiten Aufgabenbereich stellte sich die Frage, ob ein bestehender Lesetext übernommen werden sollte. In der phonetischen Tradition ist <em>El viento norte y el sol</em> ein etablierter Vergleichstext, der seit langem im Kontext der International Phonetic Association verwendet wird (vgl. International Phonetic Association 1999). Der Vorteil liegt auf der Hand: Wenn viele Projekte denselben Text nutzen, werden Daten leichter vergleichbar. Gleichzeitig ist die Texttradition selbst nicht unproblematisch.",
                    "Coloma (2015) zeigt für die spanische Version, warum auch der Standardtext nicht optimal balanciert war, und schlägt eine modifizierte Version vor, die zusätzliche Phoneme enthält, weniger Wortwiederholungen aufweist und phonetisch ausgewogener ist. Die Diskussion um alternative Versionen solcher Vergleichstexte zeigt zugleich, dass selbst etablierte Standardtexte immer auch phonologisch und didaktisch selektiv sind (vgl. Deterding 2006; Coloma 2015).",
                    "Auch (I)FEC verwendet nicht einfach den IPA-Standardtext, sondern einen eigenen Lesetext. Dieser Text ist für ein allgemeines korpusphonologisches Protokoll sinnvoll, für ein Lernendenkorpus aber ebenfalls nur begrenzt geeignet. Er umfasst 381 Wörter und ist damit für viele Lernende sehr lang; die Leseaufgabe kann entsprechend ermüdend wirken.",
                    "Hinzu kommen zahlreiche lexikalisch, syntaktisch oder semantisch anspruchsvolle Stellen, etwa <em>se agrava</em>, <em>perrera</em>, <em>lugar de los hechos</em>, <em>inspeccionar</em>, <em>suntuosa</em> oder Sätze wie <em>Tan suntuosa por fuera, y por dentro parece un zoológico obtenido por la caza nocturna en selvas y pantanos</em>. Vergleichbare Probleme zeigten sich auch im MAR.ELE-Text, dessen Auswahl an Andrea Peškovás <em>Archivo de los acentos en el ELE</em> angelehnt war. Der dort mit Blick auf teils ganz andere Phänomene verwendete, modifizierte Ausschnitt aus <em>El Principito</em> enthält u. a. Formen wie <em>sinnúmero</em>, <em>lúgubre</em>, <em>inquirió</em>, <em>compadecido</em> und <em>vergüenza</em>.",
                    "Solche Texte wollen nicht Wortschatz, Textverstehen, literarische Leseerfahrung, Aufmerksamkeit und Ermüdung testen. Für lesende Lernende werden diese Faktoren aber de facto Teil der Aufgabe. Sie können die Aussprachedaten überlagern und erschweren die Interpretation: Man weiß dann nicht immer, ob eine auffällige Realisierung auf ein Aussprachemuster zurückgeht oder auf Unsicherheit beim Lesen, auf unbekannte Lexik oder auf Überforderung durch den Text.",
                    "Hinzu kommt ein strukturelles Problem: Zusammenhängende Texte bilden relevante Phänomene selten gleichmäßig ab. Manche Phänomene treten mehrfach auf, andere gar nicht oder nur zufällig. Gerade lernendentypische Ausspracheprobleme sind darin nicht systematisch genug vertreten. Ein Lesetext ist daher für globale Leseaussprache, Rhythmus und prosodische Beobachtungen interessant, aber nicht optimal, wenn bestimmte Lernendenphänomene kontrolliert und mehrfach erhoben werden sollen.",
                ],
                "en": [
                    "For the second task area, too, the question arose whether an existing reading passage should be adopted. In the phonetic tradition, <em>El viento norte y el sol</em> is an established comparison text that has long been used in the context of the International Phonetic Association (cf. International Phonetic Association 1999). The advantage is obvious: if many projects use the same text, data become easier to compare. At the same time, the text tradition itself is not unproblematic.",
                    "Coloma (2015) shows for the Spanish version why even the standard text was not optimally balanced, and proposes a modified version that contains additional phonemes, has fewer word repetitions and is phonetically better balanced. The discussion about alternative versions of such comparison texts shows at the same time that even established standard texts are always phonologically and didactically selective (cf. Deterding 2006; Coloma 2015).",
                    "(I)FEC, too, does not simply use the IPA standard text but its own reading passage. This text is sensible for a general corpus-phonological protocol, but likewise only of limited suitability for a learner corpus. It comprises 381 words and is therefore very long for many learners; the reading task can accordingly be tiring.",
                    "In addition, there are numerous lexically, syntactically or semantically demanding passages, for example <em>se agrava</em>, <em>perrera</em>, <em>lugar de los hechos</em>, <em>inspeccionar</em>, <em>suntuosa</em> or sentences such as <em>Tan suntuosa por fuera, y por dentro parece un zoológico obtenido por la caza nocturna en selvas y pantanos</em>. Comparable problems also appeared in the MAR.ELE text, whose selection was modelled on Andrea Pešková’s <em>Archivo de los acentos en el ELE</em>. The modified excerpt from <em>El Principito</em> used there, with a view to partly quite different phenomena, contains, among others, forms such as <em>sinnúmero</em>, <em>lúgubre</em>, <em>inquirió</em>, <em>compadecido</em> and <em>vergüenza</em>.",
                    "Such texts are not meant to test vocabulary, text comprehension, literary reading experience, attention and fatigue. For learners reading aloud, however, these factors de facto become part of the task. They can overlay the pronunciation data and make interpretation more difficult: one cannot always tell whether a conspicuous realisation goes back to a pronunciation pattern or to uncertainty in reading, to unknown vocabulary or to being overwhelmed by the text.",
                    "A structural problem is added: connected texts rarely represent relevant phenomena evenly. Some phenomena occur several times, others not at all or only by chance. Learner-typical pronunciation problems in particular are not represented systematically enough in them. A reading passage is therefore of interest for global reading pronunciation, rhythm and prosodic observations, but it is not optimal when certain learner phenomena are to be elicited repeatedly and under controlled conditions.",
                ],
            },
        },
        {
            "heading": {
                "de": "Satzliste als kontrollierte Alternative",
                "en": "The sentence list as a controlled alternative",
            },
            "paragraphs_html": {
                "de": [
                    "Für <em>Pronunciation Matters</em> wurde deshalb statt eines klassischen Lesetextes eine Satzliste entwickelt. Sie ersetzt nicht die Wortliste, sondern ergänzt sie funktional. Die Satzliste prüft, ob Aussprachemuster, die in isolierten Wörtern beobachtet werden, auch unter einfachen satzprosodischen Bedingungen stabil bleiben. Bei der Konstruktion der Sätze wurden jeweils zwei gezielt ausgewählte Items aus der Wortliste zugrunde gelegt. Diese Items erscheinen in der Regel in derselben Wortform; Flexion ist nur zulässig, wenn sie phonologisch neutral bleibt und kein neues Zielphänomen einführt. Vereinzelt treten weitere Wortformen aus der Wortliste auf, ohne dass sie als zusätzliche Zielitems vorgesehen waren. Die Satzliste führt damit keine neuen primären Zielphänomene ein, eröffnet durch die Einbettung in Äußerungen jedoch zusätzliche lautliche und prosodische Kontexte, insbesondere an Wortgrenzen.",
                    "Die Satzliste folgt damit einer Progressionslogik von kontrollierter Produktion hin zu komplexeren Satzkontexten und nimmt Intelligibilität und Verständlichkeit als zentrale Bezugsgrößen ernst (vgl. Marrero 2024; Santamaría Busto 2024). Die Verbindung von phonologischer Bewusstheit und mündlicher Produktion in kommunikativen Aufgaben bietet darüber hinaus einen Anschluss an Fullana/Pujolà (2024).",
                    "Der Umfang liegt bei etwa 50 Sätzen: 30 Aussagesätze, 10 Entscheidungsfragen und 10 W-Fragen. Die Sätze sind überwiegend 8–14 Wörter lang, syntaktisch einfach und A1–B1-orientiert. Vermieden werden Schachtelsätze, Nebensatzkaskaden, idiomatische Wendungen, stilistisch auffällige Formulierungen und semantisch stark ablenkende Inhalte.",
                    "Damit entsteht kein Ersatz für freie Sprachdaten. Freieres Sprechen wird in korpusphonologischen Traditionen häufig zusätzlich erhoben, ist aber für Anfänger und viele Lernendengruppen nicht immer der geeignete Ort, um bestimmte segmentale Phänomene systematisch zu prüfen.",
                    "Die Satzliste ist vielmehr eine kontrollierte Alternative zum klassischen Lesetext: weniger komplex als ein zusammenhängender narrativer Text, aber aussagekräftiger als isolierte Einzelwörter, weil Satzrhythmus, Satzakzent und Intonation mit ins Spiel kommen und zumindest ansatzweise analysierbar werden. Die drei Satztypen eröffnen dabei erste Vergleiche intonatorischer Realisierungen. Da die Äußerungen jedoch nicht in spezifische pragmatische Kontexte eingebettet sind, erlaubt das Material keine systematische Untersuchung diskurspragmatisch differenzierter Intonationsmuster.",
                ],
                "en": [
                    "For <em>Pronunciation Matters</em>, a sentence list was therefore developed instead of a traditional reading passage. It does not replace the wordlist but complements it functionally. The sentence list tests whether pronunciation patterns observed in isolated words also remain stable under simple sentence-prosodic conditions. In constructing the sentences, two specifically selected items from the wordlist were used as a basis for each. These items generally appear in the same word form; inflection is permitted only where it remains phonologically neutral and does not introduce a new target phenomenon. Occasionally, further word forms from the wordlist occur without being intended as additional target items. The sentence list thus introduces no new primary target phenomena, but through embedding in utterances opens up additional phonetic and prosodic contexts, especially at word boundaries.",
                    "The sentence list thus follows a progression logic from controlled production to more complex sentence contexts and takes intelligibility and comprehensibility seriously as central reference points (cf. Marrero 2024; Santamaría Busto 2024). The link between phonological awareness and oral production in communicative tasks also offers a connection to Fullana/Pujolà (2024).",
                    "The list contains about 50 sentences: 30 declarative sentences, 10 yes/no questions and 10 wh-questions. The sentences are mostly 8–14 words long, syntactically simple and oriented towards A1–B1. Embedded clauses, cascades of subordinate clauses, idiomatic expressions, stylistically conspicuous formulations and semantically strongly distracting content are avoided.",
                    "This does not create a substitute for free speech data. Freer speech is often additionally elicited in corpus-phonological traditions, but for beginners and many learner groups it is not always the right place to examine certain segmental phenomena systematically.",
                    "The sentence list is rather a controlled alternative to the traditional reading passage: less complex than a connected narrative text, but more informative than isolated single words, because sentence rhythm, sentence stress and intonation come into play and become analysable, at least to some extent. The three sentence types allow first comparisons of intonational realisations. Since the utterances are not embedded in specific pragmatic contexts, however, the material does not permit a systematic investigation of discourse-pragmatically differentiated intonation patterns.",
                ],
            },
            "content_elements": [
                {
                    "type": "pm_expandable_text",
                    "id": "spanish-final-sentence-list",
                    "title": {
                        "de": "Satzliste",
                        "en": "Sentence list",
                    },
                    "summary_html": {
                        "de": "Die spanische Satzliste umfasst 50 Sätze: 30 Aussagesätze, 10 Entscheidungsfragen und 10 W-Fragen. Jeder Satz wurde mit zwei primären Zielitems aus der Wortliste konzipiert; vereinzelt treten weitere Wortlistenformen auf.",
                        "en": "The Spanish sentence list comprises 50 sentences: 30 declarative sentences, 10 yes/no questions and 10 wh-questions. Each sentence was designed with two primary target items from the wordlist; occasionally, further wordlist forms occur.",
                    },
                    "items": [
                        {"label": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
                        {"label": "D2", "text": "La viuda vive en una casa tranquila cerca del centro."},
                        {"label": "D3", "text": "Los tabúes influyen mucho en la gente joven."},
                        {"label": "D4", "text": "Nadie se quedó en la ciudad después."},
                        {"label": "D5", "text": "Cuidar un perro exige tiempo y atención diaria."},
                        {"label": "D6", "text": "El médico pudo salvar la vida al enfermo."},
                        {"label": "D7", "text": "Es difícil juzgar solo por lo que se oye."},
                        {"label": "D8", "text": "El champán acompañó el baile elegante del evento."},
                        {"label": "D9", "text": "Algo tan caro no siempre vale la pena."},
                        {"label": "D10", "text": "El avión bajó hacia tierra sin problemas graves."},
                        {"label": "D11", "text": "El jamón quedó sobre la mesa después de cenar."},
                        {"label": "D12", "text": "La vainilla dejó un aroma suave en la cocina."},
                        {"label": "D13", "text": "Él quería llevar a su hijo a ver los toros."},
                        {"label": "D14", "text": "Por la mañana siento dolor en el labio y el oído."},
                        {"label": "D15", "text": "Mi tío se compró un carro y su deuda aumentó."},
                        {"label": "D16", "text": "La queja llegó finalmente al jefe responsable."},
                        {"label": "D17", "text": "La euforia le hizo traer más bebidas de lo necesario."},
                        {"label": "D18", "text": "Puedo oír bien cuando ella se ríe bajito."},
                        {"label": "D19", "text": "El ladrón buscó la llave correcta sin éxito."},
                        {"label": "D20", "text": "Un giro rápido lo llevó a una caída muy dolorosa."},
                        {"label": "D21", "text": "Con mucho cuidado se puso a lavar la ropa."},
                        {"label": "D22", "text": "Su logro es un motivo para admirar su esfuerzo."},
                        {"label": "D23", "text": "Al despertar, tenía sueño y un vacío extraño."},
                        {"label": "D24", "text": "Con su familia es un ángel y con sus amigos un diablo."},
                        {"label": "D25", "text": "La flor del jardín tiene un color neutro y bonito."},
                        {"label": "D26", "text": "El muchacho habla sobre la caza con su abuelo."},
                        {"label": "D27", "text": "Cuando el chico tiene hambre, pierde el control."},
                        {"label": "D28", "text": "El álbum familiar les hizo reír toda la tarde."},
                        {"label": "D29", "text": "Ahí termina la calle y allí comienza otra."},
                        {"label": "D30", "text": "El profesor explicó la regla y numeró ejemplos."},
                        {"label": "QY1", "text": "¿El vaso está lleno de vino ahora?"},
                        {"label": "QY2", "text": "¿Vienes mañana a ver la casa?"},
                        {"label": "QY3", "text": "¿La salud importa más que la paz?"},
                        {"label": "QY4", "text": "¿Ustedes dicen “hola” al entrar al aula?"},
                        {"label": "QY5", "text": "¿Tampoco los otros quieren venir?"},
                        {"label": "QY6", "text": "¿Querría otra ración de tortilla?"},
                        {"label": "QY7", "text": "¿El drama continúa dentro del club?"},
                        {"label": "QY8", "text": "¿En Europa la verdad importa?"},
                        {"label": "QY9", "text": "¿Usted espera respuesta ahí?"},
                        {"label": "QY10", "text": "¿Viajó solo con el mismo plan de siempre?"},
                        {"label": "QW1", "text": "¿Por qué dices gracias pero no respondes?"},
                        {"label": "QW2", "text": "¿Cuándo vienen los otros hoy?"},
                        {"label": "QW3", "text": "¿Dónde sirve el vino el jefe?"},
                        {"label": "QW4", "text": "¿Por qué esa causa genera tanto drama?"},
                        {"label": "QW5", "text": "¿Cómo se obtiene la llave correcta?"},
                        {"label": "QW6", "text": "¿Cómo de lleno está el barrio?"},
                        {"label": "QW7", "text": "¿Por qué cuidas los bienes y no la salud?"},
                        {"label": "QW8", "text": "¿Cómo numero los puntos que obtiene cada equipo?"},
                        {"label": "QW9", "text": "¿Cuál es el signo de la paz?"},
                        {"label": "QW10", "text": "¿Por qué quieres tirar ese número de teléfono?"},
                    ],
                },
            ],
        },
        {
            "heading": {
                "de": "Interview",
                "en": "Interview",
            },
            "paragraphs_html": {
                "de": [
                    "Das projektweit eingesetzte Interview ergänzt die kontrollierten Leseaufgaben um die Perspektive der Lernenden auf ihre eigene Aussprache. Es wird nicht in der Zielsprache geführt, sondern dient der metasprachlichen Reflexion: Neben allgemeinen Einschätzungen zur eigenen Aussprache und wahrgenommenen Schwierigkeiten können auch konkrete Auffälligkeiten aus den vorangegangenen Leseaufgaben aufgegriffen und gemeinsam besprochen werden. Anders als bei den fest vorgegebenen Wort- und Satzlisten richtet sich der Gesprächsverlauf somit teilweise nach den Beobachtungen während der jeweiligen Erhebung.",
                    "Auf diese Weise werden die dokumentierten Ausspracheproduktionen um subjektive Wahrnehmungen und Einschätzungen ergänzt, die zusätzliche Einblicke in das Aussprachebewusstsein der Lernenden ermöglichen. Die Interviewkomponente knüpft damit an Arbeiten an, die phonologische Bewusstheit und metakognitive Reflexion als wichtige Bestandteile der Aussprachearbeit verstehen (vgl. Blanco Canales 2024).",
                ],
                "en": [
                    "The project-wide interview supplements the controlled reading tasks with the learners’ perspective on their own pronunciation. It is not conducted in the target language but serves metalinguistic reflection: besides general assessments of their own pronunciation and perceived difficulties, specific conspicuous features from the preceding reading tasks can also be taken up and discussed together. Unlike the fixed wordlists and sentence lists, the course of the conversation thus partly depends on observations made during the respective elicitation.",
                    "In this way, the documented pronunciation productions are supplemented by subjective perceptions and assessments that provide additional insights into learners’ pronunciation awareness. The interview component thus connects with work that regards phonological awareness and metacognitive reflection as important components of pronunciation work (cf. Blanco Canales 2024).",
                ],
            },
        },
        {
            "heading": {
                "de": "Fazit: Potenziale und Grenzen des Erhebungsdesigns",
                "en": "Conclusion: Potential and limitations of the data collection design",
            },
            "paragraphs_html": {
                "de": [
                    "Das vorgestellte Erhebungsdesign verbindet die systematische Erfassung ausgewählter Aussprachephänomene mit einer an den Voraussetzungen von Spanischlernenden orientierten Materialkonzeption. Im Mittelpunkt stehen die Vergleichbarkeit der erhobenen Produktionen und die Abdeckung zentraler phonetisch-phonologischer Erscheinungen, insbesondere im Bereich des Konsonantismus. Das spanische Korpus von <em>Pronunciation Matters</em> bietet damit eine empirische Grundlage für unterschiedliche Fragestellungen der Lernendenphonetik und Aussprachedidaktik.",
                    "Als allgemeiner angelegtes Erhebungsprotokoll kann und soll es allerdings keine auf einzelne Phänomene zugeschnittenen Untersuchungen ersetzen. Für vertiefende Analysen werden je nach Erkenntnisinteresse spezifischere Aufgaben und zusätzliche Daten erforderlich bleiben. Das für die Forschung bereitgestellte Korpus ermöglicht es jedoch, zahlreiche Fragestellungen zunächst anhand authentischer Lernendendaten zu untersuchen, erste Hypothesen zu prüfen und weiterführende Studien vorzubereiten.",
                    "Die Konzeption ist somit das Ergebnis einer bewussten Abwägung zwischen phonologischer Abdeckung, Vergleichbarkeit, Lernendenorientierung und praktischer Durchführbarkeit. Gerade diese Verbindung soll eine möglichst vielseitige wissenschaftliche Nutzung der erhobenen Sprachdaten ermöglichen.",
                ],
                "en": [
                    "The data collection design presented here combines the systematic elicitation of selected pronunciation phenomena with a material design oriented towards the prerequisites of Spanish learners. The focus is on the comparability of the elicited productions and on the coverage of central phonetic-phonological phenomena, in particular in the area of consonantism. The Spanish corpus of <em>Pronunciation Matters</em> thus offers an empirical basis for different questions in learner phonetics and pronunciation didactics.",
                    "As a more generally conceived elicitation protocol, however, it cannot and is not meant to replace investigations tailored to individual phenomena. For in-depth analyses, more specific tasks and additional data will remain necessary depending on the research interest. The corpus made available for research nevertheless makes it possible to investigate numerous questions first on the basis of authentic learner data, to test initial hypotheses and to prepare further studies.",
                    "The design is thus the result of a deliberate weighing of phonological coverage, comparability, learner orientation and practical feasibility. This very combination is meant to enable the broadest possible scholarly use of the elicited speech data.",
                ],
            },
        },
        {
            "heading": {
                "de": "Literatur",
                "en": "References",
            },
            "list_class": "pm-literature",
            "bullets_html": {
                "de": [
                    'Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.) (2024): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins. DOI: <a href="https://doi.org/10.1075/ivitra.42">https://doi.org/10.1075/ivitra.42</a>',
                    "Benet, Ariadna / Pešková, Andrea (2017): „Cómo reducir el ‚acento extranjero‘ en el ELE“. <em>Der fremdsprachliche Unterricht Spanisch</em> 58, 16–20.",
                    "Blanco Canales, Ana (2024): „La enseñanza de la pronunciación basada en el desarrollo de la conciencia fonológica y la metacognición“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 175–189.",
                    "Coloma, Germán (2015): „Una versión alternativa de ‚El viento norte y el sol‘ en español“. <em>Revista de Investigación Lingüística</em> 18, 191–212.",
                    "Deterding, David (2006): „The North Wind versus a Wolf: Short Texts for the Description and Measurement of English Pronunciation“. <em>Journal of the International Phonetic Association</em> 36(2), 187–196.",
                    "Detey, Sylvain / Durand, Jacques / Laks, Bernard / Lyche, Chantal (2016): „The PFC programme and its methodological framework“. In: Detey, Sylvain / Durand, Jacques / Laks, Bernard / Lyche, Chantal (Hg.): <em>Varieties of Spoken French</em>. Oxford: Oxford University Press, 13–23.",
                    "Díez Plaza, César L. (2024): „La ortografía en la enseñanza de ELE: De la grafía a la pronunciación“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 40–54.",
                    "Fullana, Natalia / Pujolà, Joan-Tomàs (2024): „L2 pronunciation in the spotlight: From phonological awareness to oral production in communicative tasks“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 88–101.",
                    'Gabriel, Christoph / Meisenburg, Trudel / Selig, Maria (2025): <em>Spanisch: Phonetik und Phonologie. Eine Einführung</em>. 2., überarb. Aufl. Tübingen: Narr Francke Attempto. DOI: <a href="https://doi.org/10.24053/9783381100125">https://doi.org/10.24053/9783381100125</a>',
                    "Gil Fernández, Juana (2007): <em>Fonética para profesores de español: de la teoría a la práctica</em>. Madrid: Arco Libros.",
                    "Hidalgo Gallardo, Matías / Pérez Serrano, Mercedes (2024): „Léxico y pronunciación: Un camino de ida y vuelta“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 12–24.",
                    "International Phonetic Association (1999): <em>Handbook of the International Phonetic Association</em>. Cambridge: Cambridge University Press.",
                    "Labov, William (1972): <em>Sociolinguistic Patterns</em>. Philadelphia: University of Pennsylvania Press.",
                    "Marrero, Victoria (2024): „De la comprensión auditiva a la pronunciación“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 72–87.",
                    'Pešková, Andrea (o. J.): <em>Archivo de los acentos en el ELE</em>. Online: <a href="https://andrea-peskova.com/archivo-de-los-acentos-l2/">https://andrea-peskova.com/archivo-de-los-acentos-l2/</a>',
                    "Pustka, Elissa (2021): <em>Phonetik und Phonologie des Spanischen. Eine korpuslinguistische Einführung</em>. Berlin: Erich Schmidt.",
                    "Pustka, Elissa / Gabriel, Christoph / Meisenburg, Trudel / Burkard, Monja / Dziallas, Kristina (2018): „(Inter-)Fonología del Español Contemporáneo (I)FEC: Metodología de un programa de investigación para la fonología de corpus“. <em>Loquens</em> 5(1), e046.",
                    "Racine, Isabelle / Zay, Françoise / Detey, Sylvain / Kawaguchi, Yuji (2012): „Des atouts d’un corpus multitâches pour l’étude de la phonologie en L2: l’exemple du projet ‚Interphonologie du français contemporain‘ (IPFC)“. In: Kamiyama, Takeki / Kawaguchi, Yuji / Minegishi, Makoto (Hg.): <em>Corpus-based Analysis and Diachronic Linguistics</em>. Amsterdam: John Benjamins, 1–19.",
                    "Santamaría Busto, Enrique (2024): „Hacia una evaluación comunicativa y eficaz de la pronunciación del español“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 190–206.",
                    'Tacke, Felix (2023–2024): <em>MAR.ELE – Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg</em>. Marburg: Philipps-Universität Marburg. Online: <a href="https://hispanistica.com/projects/marele/">https://hispanistica.com/projects/marele/</a>',
                ],
                "en": [
                    'Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.) (2024): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins. DOI: <a href="https://doi.org/10.1075/ivitra.42">https://doi.org/10.1075/ivitra.42</a>',
                    "Benet, Ariadna / Pešková, Andrea (2017): „Cómo reducir el ‚acento extranjero‘ en el ELE“. <em>Der fremdsprachliche Unterricht Spanisch</em> 58, 16–20.",
                    "Blanco Canales, Ana (2024): „La enseñanza de la pronunciación basada en el desarrollo de la conciencia fonológica y la metacognición“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 175–189.",
                    "Coloma, Germán (2015): „Una versión alternativa de ‚El viento norte y el sol‘ en español“. <em>Revista de Investigación Lingüística</em> 18, 191–212.",
                    "Deterding, David (2006): „The North Wind versus a Wolf: Short Texts for the Description and Measurement of English Pronunciation“. <em>Journal of the International Phonetic Association</em> 36(2), 187–196.",
                    "Detey, Sylvain / Durand, Jacques / Laks, Bernard / Lyche, Chantal (2016): „The PFC programme and its methodological framework“. In: Detey, Sylvain / Durand, Jacques / Laks, Bernard / Lyche, Chantal (Hg.): <em>Varieties of Spoken French</em>. Oxford: Oxford University Press, 13–23.",
                    "Díez Plaza, César L. (2024): „La ortografía en la enseñanza de ELE: De la grafía a la pronunciación“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 40–54.",
                    "Fullana, Natalia / Pujolà, Joan-Tomàs (2024): „L2 pronunciation in the spotlight: From phonological awareness to oral production in communicative tasks“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 88–101.",
                    'Gabriel, Christoph / Meisenburg, Trudel / Selig, Maria (2025): <em>Spanisch: Phonetik und Phonologie. Eine Einführung</em>. 2., überarb. Aufl. Tübingen: Narr Francke Attempto. DOI: <a href="https://doi.org/10.24053/9783381100125">https://doi.org/10.24053/9783381100125</a>',
                    "Gil Fernández, Juana (2007): <em>Fonética para profesores de español: de la teoría a la práctica</em>. Madrid: Arco Libros.",
                    "Hidalgo Gallardo, Matías / Pérez Serrano, Mercedes (2024): „Léxico y pronunciación: Un camino de ida y vuelta“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 12–24.",
                    "International Phonetic Association (1999): <em>Handbook of the International Phonetic Association</em>. Cambridge: Cambridge University Press.",
                    "Labov, William (1972): <em>Sociolinguistic Patterns</em>. Philadelphia: University of Pennsylvania Press.",
                    "Marrero, Victoria (2024): „De la comprensión auditiva a la pronunciación“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 72–87.",
                    'Pešková, Andrea (o. J.): <em>Archivo de los acentos en el ELE</em>. Online: <a href="https://andrea-peskova.com/archivo-de-los-acentos-l2/">https://andrea-peskova.com/archivo-de-los-acentos-l2/</a>',
                    "Pustka, Elissa (2021): <em>Phonetik und Phonologie des Spanischen. Eine korpuslinguistische Einführung</em>. Berlin: Erich Schmidt.",
                    "Pustka, Elissa / Gabriel, Christoph / Meisenburg, Trudel / Burkard, Monja / Dziallas, Kristina (2018): „(Inter-)Fonología del Español Contemporáneo (I)FEC: Metodología de un programa de investigación para la fonología de corpus“. <em>Loquens</em> 5(1), e046.",
                    "Racine, Isabelle / Zay, Françoise / Detey, Sylvain / Kawaguchi, Yuji (2012): „Des atouts d’un corpus multitâches pour l’étude de la phonologie en L2: l’exemple du projet ‚Interphonologie du français contemporain‘ (IPFC)“. In: Kamiyama, Takeki / Kawaguchi, Yuji / Minegishi, Makoto (Hg.): <em>Corpus-based Analysis and Diachronic Linguistics</em>. Amsterdam: John Benjamins, 1–19.",
                    "Santamaría Busto, Enrique (2024): „Hacia una evaluación comunicativa y eficaz de la pronunciación del español“. In: Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.): <em>La integración de la pronunciación en el aula de ELE</em>. Amsterdam/Philadelphia: John Benjamins, 190–206.",
                    'Tacke, Felix (2023–2024): <em>MAR.ELE – Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg</em>. Marburg: Philipps-Universität Marburg. Online: <a href="https://hispanistica.com/projects/marele/">https://hispanistica.com/projects/marele/</a>',
                ],
            },
        },
    ],
    "footnotes_html": {
        "de": [
            {
                "id": "fn-spanish-design-1-de",
                "label": "1",
                "html": 'Zum Gesamtprojekt, seiner Entstehung, Plattformlogik, methodischen Infrastruktur und beteiligten Zusammenarbeit siehe die Projektseiten <a href="/de/project/about">Worum es geht</a>, <a href="/de/project/structure">Projektaufbau</a>, <a href="/de/project/data-methods">Daten &amp; Methodik</a> und <a href="/de/project/team">Team &amp; Mitwirkende</a>.',
            },
            {
                "id": "fn-spanish-design-2-de",
                "label": "2",
                "html": "Beispiele für nicht übernommene oder problematische (I)FEC-Items: <em>estudiéis</em>, <em>cambiáis</em>, <em>bou</em>, <em>miau</em>, <em>guau</em>, <em>kétchup</em>, <em>iceberg</em>, <em>ñandú</em>, <em>yunque</em>, <em>ciempiés</em>, <em>rosbif</em>, <em>coñac</em>, <em>chalet</em>, <em>suntuoso</em>, <em>diurético</em>.",
            },
            {
                "id": "fn-spanish-design-3-de",
                "label": "3",
                "html": "Übernommene Wortformen aus (I)FEC: <em>reloj</em>, <em>viuda</em>, <em>tabúes</em>, <em>querría</em>, <em>caída</em>, <em>numeró</em>, <em>toros</em>, <em>flor</em>, <em>ríe</em>, <em>hoy</em>, <em>juzgar</em>, <em>signo</em>, <em>labio</em>, <em>deuda</em>, <em>queja</em>, <em>ladrón</em>, <em>club</em>, <em>vainilla</em>, <em>número</em>, <em>ángel</em>, <em>caza</em>, <em>logro</em>, <em>mismo</em>, <em>vino</em>, <em>admirar</em>, <em>sueño</em>, <em>álbum</em>, <em>chico</em>, <em>algo</em>, <em>ahí</em>, <em>enfermo</em>, <em>diablo</em>, <em>nadie</em>, <em>causa</em>, <em>llave</em>, <em>perro</em>, <em>cuidar</em>, <em>baile</em>, <em>drama</em>, <em>vienes</em>, <em>gracias</em>, <em>oído</em>, <em>casa</em>, <em>ración</em>, <em>muchacho</em>, <em>salud</em>, <em>quería</em>, <em>paz</em>, <em>champán</em>, <em>obtiene</em>, <em>oye</em>, <em>reír</em>, <em>lleno</em>, <em>Europa</em>, <em>allí</em>, <em>numero</em>, <em>otros</em>, <em>pero</em>.",
            },
            {
                "id": "fn-spanish-design-4-de",
                "label": "4",
                "html": "Neu ergänzte Wortformen (31): <em>mesa</em>, <em>neutro</em>, <em>ciudad</em>, <em>lavar</em>, <em>avión</em>, <em>jamón</em>, <em>gente</em>, <em>regla</em>, <em>euforia</em>, <em>oír</em>, <em>usted</em>, <em>giro</em>, <em>cuidado</em>, <em>solo</em>, <em>vacío</em>, <em>traer</em>, <em>jefe</em>, <em>vida</em>, <em>ustedes</em>, <em>tirar</em>, <em>carro</em>, <em>tierra</em>, <em>tampoco</em>, <em>hambre</em>, <em>suave</em>, <em>barrio</em>, <em>verdad</em>, <em>caro</em>, <em>ola</em>, <em>hola</em>, <em>bienes</em>.",
            },
            {
                "id": "fn-spanish-design-5-de",
                "label": "5",
                "html": "Für entsprechende Analysen stehen im Forschungsbereich von <em>Pronunciation Matters</em> kuratierte Phänomensets zur Verfügung, die ausgewählte Wort- und Satzitems zusammenführen. Darüber hinaus können Forschende die Items für spezifische Fragestellungen individuell kombinieren.",
            },
        ],
        "en": [
            {
                "id": "fn-spanish-design-1-en",
                "label": "1",
                "html": 'For the project as a whole, its genesis, platform logic, methodological infrastructure and the collaboration involved, see the project pages <a href="/en/project/about">What this project is about</a>, <a href="/en/project/structure">Project structure</a>, <a href="/en/project/data-methods">Data &amp; methods</a> and <a href="/en/project/team">Team &amp; contributors</a>.',
            },
            {
                "id": "fn-spanish-design-2-en",
                "label": "2",
                "html": "Examples of (I)FEC items that were not retained or proved problematic: <em>estudiéis</em>, <em>cambiáis</em>, <em>bou</em>, <em>miau</em>, <em>guau</em>, <em>kétchup</em>, <em>iceberg</em>, <em>ñandú</em>, <em>yunque</em>, <em>ciempiés</em>, <em>rosbif</em>, <em>coñac</em>, <em>chalet</em>, <em>suntuoso</em>, <em>diurético</em>.",
            },
            {
                "id": "fn-spanish-design-3-en",
                "label": "3",
                "html": "Word forms retained from (I)FEC: <em>reloj</em>, <em>viuda</em>, <em>tabúes</em>, <em>querría</em>, <em>caída</em>, <em>numeró</em>, <em>toros</em>, <em>flor</em>, <em>ríe</em>, <em>hoy</em>, <em>juzgar</em>, <em>signo</em>, <em>labio</em>, <em>deuda</em>, <em>queja</em>, <em>ladrón</em>, <em>club</em>, <em>vainilla</em>, <em>número</em>, <em>ángel</em>, <em>caza</em>, <em>logro</em>, <em>mismo</em>, <em>vino</em>, <em>admirar</em>, <em>sueño</em>, <em>álbum</em>, <em>chico</em>, <em>algo</em>, <em>ahí</em>, <em>enfermo</em>, <em>diablo</em>, <em>nadie</em>, <em>causa</em>, <em>llave</em>, <em>perro</em>, <em>cuidar</em>, <em>baile</em>, <em>drama</em>, <em>vienes</em>, <em>gracias</em>, <em>oído</em>, <em>casa</em>, <em>ración</em>, <em>muchacho</em>, <em>salud</em>, <em>quería</em>, <em>paz</em>, <em>champán</em>, <em>obtiene</em>, <em>oye</em>, <em>reír</em>, <em>lleno</em>, <em>Europa</em>, <em>allí</em>, <em>numero</em>, <em>otros</em>, <em>pero</em>.",
            },
            {
                "id": "fn-spanish-design-4-en",
                "label": "4",
                "html": "Newly added word forms (31): <em>mesa</em>, <em>neutro</em>, <em>ciudad</em>, <em>lavar</em>, <em>avión</em>, <em>jamón</em>, <em>gente</em>, <em>regla</em>, <em>euforia</em>, <em>oír</em>, <em>usted</em>, <em>giro</em>, <em>cuidado</em>, <em>solo</em>, <em>vacío</em>, <em>traer</em>, <em>jefe</em>, <em>vida</em>, <em>ustedes</em>, <em>tirar</em>, <em>carro</em>, <em>tierra</em>, <em>tampoco</em>, <em>hambre</em>, <em>suave</em>, <em>barrio</em>, <em>verdad</em>, <em>caro</em>, <em>ola</em>, <em>hola</em>, <em>bienes</em>.",
            },
            {
                "id": "fn-spanish-design-5-en",
                "label": "5",
                "html": "For corresponding analyses, curated phenomenon sets that bring together selected word and sentence items are available in the research area of <em>Pronunciation Matters</em>. In addition, researchers can combine the items individually for specific research questions.",
            },
        ],
    },
}
