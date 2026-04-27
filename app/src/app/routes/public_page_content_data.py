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
                        "Der Forschungsbereich führt zu den einzelnen Sprachkorpora. Dort werden die jeweiligen Korpusdesigns erläutert. Die geschützten Bereiche enthalten die eigentlichen Sprachdaten und Forschungstools: Über die Seite Sprecher:innen lassen sich die teilnehmenden Informant:innen erschließen, über Aufnahmen einzelne Sessions und Aufgabenformate, über Vergleichsansichten kontrastive Analysen und über phänomenbezogene Item-Sets gezielte Ausschnitte des Materials. Diese Bereiche sind nicht frei zugänglich, weil sie mit pseudonymisierten Sprachdaten und aufnahmebezogenen Metadaten arbeiten.",
                        "Der Unterrichtsbereich bereitet ausgewählte Inhalte für die Aussprachevermittlung auf. Er ist schlanker angelegt als der Forschungsbereich, weil hier nicht die vollständige Forschungsumgebung im Vordergrund steht, sondern thematisch fokussierte Zugänge zu besonders relevanten Aspekten der Aussprache. Solche Themenseiten können kontrastive Vergleiche nutzen, typische Schwierigkeiten sichtbar machen und Material bereitstellen, das Lehrkräfte pragmatisch in bestehende Unterrichtsstunden integrieren können. Dabei geht das Projekt nicht von der Illusion aus, dass Aussprache im schulischen Fremdsprachenunterricht regelmäßig eigene Unterrichtsreihen erhält. Ziel sind vielmehr anschauliche, fachlich fundierte Erweiterungen dort, wo Lehrpläne, Unterrichtssituationen oder konkrete Lernprobleme Raum dafür eröffnen.",
                    ],
                    "en": [
                        "The public web app is divided into three main content areas: Project, Research, and Teaching.",
                        "The Project area explains the basic idea, the development of the project, the platform structure, the methodology, and the collaboration behind it. It is intended for all users who want to understand what <em>Pronunciation Matters</em> is and how the project works.",
                        "The Research area leads to the individual language corpora. The respective corpus designs are explained there. The protected areas contain the actual speech data and research tools: the Speakers page provides access to the participating informants, Recordings gives access to individual sessions and task formats, comparison views support contrastive analyses, and phenomenon-based item sets allow users to work with targeted excerpts of the material. These areas are not openly accessible because they work with pseudonymised speech data and recording-related metadata.",
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
                        "Im Forschungsbereich können Nutzer:innen mit detaillierten Daten arbeiten. Sie können Aufnahmen gezielt vergleichen, einzelne Aufgabenformate aufrufen, Materialausschnitte auswählen und phänomenbezogene Sets erstellen oder modifizieren. Der Forschungsbereich ist damit ein Arbeitsraum für Analyse und Hochschullehre.",
                        "Im Unterrichtsbereich werden ausgewählte Inhalte didaktisch gefasst. Dort geht es um verständliche Erklärungen, Aufgaben, Hörbeispiele und Materialien, die für schulische oder hochschuldidaktische Kontexte geeignet sind. Diese Materialien können aus der Arbeit mit den Forschungsdaten hervorgehen, werden aber nicht einfach direkt aus dem geschützten Datenraum ausgespielt.",
                    ],
                    "en": [
                        "The platform deliberately separates research and teaching. This prevents teaching materials from appearing as a reduced research database and prevents research surfaces from having to take on didactic functions for which they were not designed.",
                        "In the Research area, users can work with detailed data. They can compare recordings, access individual task formats, select excerpts of material, and create or modify phenomenon-based sets. The Research area is therefore a workspace for analysis and university teaching.",
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
                        "Die Plattform soll Forschung und Hochschullehre komfortabel unterstützen. Wer mit den Daten arbeitet, soll nicht zuerst Ordnerstrukturen, Dateinamen oder Rohformate verstehen müssen. Die WebApp bietet stattdessen geordnete Zugänge über Sprachen, Personen, Aufnahmen, Aufgabenformate, Vergleichsansichten und Aussprachephänomene. Dadurch wird die technische Komplexität nicht unsichtbar gemacht, aber so organisiert, dass sie wissenschaftliches Arbeiten erleichtert.",
                        "Eine ergänzende technische Projektseite zu <em>Pronunciation Matters</em> wird im Kontext von Hispanistica @ Marburg geführt: https://hispanistica.com/projects/promat/. Die öffentliche WebApp selbst stellt dagegen primär die Projektidee, die Forschungs- und Unterrichtslogik sowie die nutzbaren Inhalte in den Vordergrund.",
                    ],
                    "en": [
                        "<em>Pronunciation Matters</em> is also a digital humanities project. The technical infrastructure is not a layer added after the fact; it is part of the scholarly and didactic method. Data modelling, structured metadata, annotations, audio processing, web app design, and protected access spaces are what make the collected speech data practically usable in the first place.",
                        "The platform is intended to support research and university teaching comfortably. Users working with the data should not first have to understand folder structures, filenames, or raw formats. Instead, the web app offers structured access through languages, persons, recordings, task formats, comparison views, and pronunciation phenomena. Technical complexity is not made invisible, but organised in a way that facilitates scholarly work.",
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
                "meta_cards": [
                    {
                        "title": {
                            "de": "Spanisch-Korpus",
                            "en": "Spanish corpus",
                        },
                        "metadata_rows": {
                            "de": [
                                {
                                    "label": "Korpusverantwortung",
                                    "value": "Prof. Dr. Felix Tacke",
                                },
                                {
                                    "label": "Materialkonzeption",
                                    "value": "Prof. Dr. Felix Tacke, Ana Goás Pérez",
                                },
                                {
                                    "label": "Durchführung",
                                    "value": "Marlon Merte",
                                },
                            ],
                            "en": [
                                {
                                    "label": "Corpus responsibility",
                                    "value": "Prof. Dr. Felix Tacke",
                                },
                                {
                                    "label": "Material design",
                                    "value": "Prof. Dr. Felix Tacke, Ana Goás Pérez",
                                },
                                {
                                    "label": "Implementation",
                                    "value": "Marlon Merte",
                                },
                            ],
                        },
                    },
                    {
                        "title": {
                            "de": "Französisch-Korpus",
                            "en": "French corpus",
                        },
                        "metadata_rows": {
                            "de": [
                                {
                                    "label": "Korpusverantwortung",
                                    "value": "Prof. Dr. Janina Reinhardt",
                                },
                                {
                                    "label": "Materialkonzeption",
                                    "value": "Prof. Dr. Janina Reinhardt",
                                },
                                {
                                    "label": "Durchführung",
                                    "value": "Amelie Spieß",
                                },
                            ],
                            "en": [
                                {
                                    "label": "Corpus responsibility",
                                    "value": "Prof. Dr. Janina Reinhardt",
                                },
                                {
                                    "label": "Material design",
                                    "value": "Prof. Dr. Janina Reinhardt",
                                },
                                {
                                    "label": "Implementation",
                                    "value": "Amelie Spieß",
                                },
                            ],
                        },
                    },
                    {
                        "title": {
                            "de": "Deutsch-Korpus",
                            "en": "German corpus",
                        },
                        "metadata_rows": {
                            "de": [
                                {
                                    "label": "Korpusverantwortung",
                                    "value": "Prof. Dr. Kathrin Siebold",
                                },
                                {
                                    "label": "Materialkonzeption",
                                    "value": "Prof. Dr. Kathrin Siebold",
                                },
                                {
                                    "label": "Durchführung",
                                    "value": "Theresa Fischer, M.A.",
                                },
                            ],
                            "en": [
                                {
                                    "label": "Corpus responsibility",
                                    "value": "Prof. Dr. Kathrin Siebold",
                                },
                                {
                                    "label": "Material design",
                                    "value": "Prof. Dr. Kathrin Siebold",
                                },
                                {
                                    "label": "Implementation",
                                    "value": "Theresa Fischer, M.A.",
                                },
                            ],
                        },
                    },
                    {
                        "title": {
                            "de": "Englisch-Korpus",
                            "en": "English corpus",
                        },
                        "metadata_rows": {
                            "de": [
                                {
                                    "label": "Korpusverantwortung",
                                    "value": "Prof. Dr. Rolf Kreyer",
                                },
                                {
                                    "label": "Materialkonzeption",
                                    "value": "Prof. Dr. Rolf Kreyer",
                                },
                                {
                                    "label": "Durchführung",
                                    "value": "Marlon Merte",
                                },
                            ],
                            "en": [
                                {
                                    "label": "Corpus responsibility",
                                    "value": "Prof. Dr. Rolf Kreyer",
                                },
                                {
                                    "label": "Material design",
                                    "value": "Prof. Dr. Rolf Kreyer",
                                },
                                {
                                    "label": "Implementation",
                                    "value": "Marlon Merte",
                                },
                            ],
                        },
                    },
                ],
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
                        "Marcela Gualotuña",
                        "Aoife Holmes-Rein, M.A.",
                    ],
                    "en": [
                        "Dr. Pedro Alonso",
                        "Ana Goás Pérez",
                        "Marcela Gualotuña",
                        "Aoife Holmes-Rein, M.A.",
                    ],
                },
            },
        ],
    },
}


SPANISH_DESIGN_PAGE_CONTENT: dict[str, object] = {
    "title": {
        "de": "Design",
        "en": "Design",
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
                "de": "Ausgangspunkt",
                "en": "Starting point",
            },
            "paragraphs_html": {
                "de": [
                    "Die spanischen Aufgaben dieses Korpus wurden entwickelt, um ein Forschungsdesign für Lernendenaussprache bereitzustellen, das systematisch, vergleichbar und zugleich für Lernende gut bearbeitbar ist. Für den größeren Projektrahmen und die Entstehung des Gesamtvorhabens bietet die allgemeine Projektseite <a href=\"/de/project/about\">Worum es geht</a> den passenden Kontext.",
                    "Ergänzend verorten die Projektseiten <a href=\"/de/project/structure\">Projektaufbau</a>, <a href=\"/de/project/data-methods\">Daten &amp; Methodik</a> und <a href=\"/de/project/team\">Team &amp; Mitwirkende</a> das spanische Design innerhalb der gemeinsamen Plattformlogik, der methodischen Infrastruktur und der beteiligten Zusammenarbeit.",
                    "Ausgangspunkt war die Beobachtung, dass bestehende Modelle zwar wichtige Vorarbeiten bieten, für die gezielte Untersuchung der spanischen Aussprache von Lernenden aber nur teilweise direkt übernommen werden können. Das betrifft vor allem Wortschatzschwierigkeit, inhaltliche Ablenkungen durch Lesetexte und die Frage, welche lautlichen Phänomene für Lernendenaussprache tatsächlich mehrfach und kontrolliert erhoben werden müssen. Leitend sind daher nicht Nativitätsnähe oder bloße Tradition, sondern Intelligibilität, kontrollierte Elizitation und eine für Lernende sinnvolle Materialgestaltung.",
                ],
                "en": [
                    "The Spanish tasks in this corpus were developed to provide a research design for learner pronunciation that is systematic, comparable, and still manageable for learners. For the broader project frame and the history of the overall initiative, the general project page <a href=\"/en/project/about\">What this project is about</a> provides the right context.",
                    "In addition, the project pages <a href=\"/en/project/structure\">Project structure</a>, <a href=\"/en/project/data-methods\">Data &amp; methods</a>, and <a href=\"/en/project/team\">Team &amp; contributors</a> place the Spanish design within the shared platform logic, methodological infrastructure, and collaborative setup.",
                    "The starting point was the observation that existing models offer valuable groundwork, but can only partly be transferred directly to the targeted study of Spanish learner pronunciation. This concerns lexical difficulty, content-related distraction in reading passages, and the question of which pronunciation phenomena actually need to be elicited repeatedly and under controlled conditions in learner data. The guiding principles are therefore not proximity to native-speaker norms or mere tradition, but intelligibility, controlled elicitation, and materials that make sense for learners.",
                ],
            },
        },
        {
            "heading": {
                "de": "Vorarbeiten und empirische Ausgangslage",
                "en": "Previous work and empirical starting position",
            },
            "paragraphs_html": {
                "de": [
                    _link_marele("Ein wichtiger Zwischenschritt war das frühere Projekt MAR.ELE – Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg. In diesem kleineren Vorprojekt wurden 22 Aufnahmen mit Studierenden der Universität Marburg erstellt. MAR.ELE diente dazu, spanische Lernendenaussprache als Korpusmaterial zugänglich und empirisch auswertbar zu machen. In der praktischen Arbeit mit diesem Korpus wurden jedoch auch die Grenzen eines stark übernommenen Designs sichtbar. Gerade diese Erfahrungen waren entscheidend für die weitergehende Überarbeitung im vorliegenden Projekt und stehen zugleich in engem Zusammenhang mit der allgemeinen Projektentwicklung, die auf <a href=\"/de/project/about\">Worum es geht</a> skizziert wird."),
                    _link_marele("Für MAR.ELE wurde die Wortliste des Projekts (I)FEC vollständig übernommen, um die Anschlussfähigkeit an ein etabliertes korpusphonologisches Design des Spanischen zu sichern. Das war methodisch sinnvoll, zeigte in der Arbeit mit Lernenden aber auch deutliche Probleme: Einige Items erwiesen sich als unnötige lexikalische Stolperstellen, andere Phänomene, die für Lernendenaussprache besonders aufschlussreich sind, waren nicht optimal verteilt oder nicht stark genug vertreten. Die jetzige Konzeption reagiert daher nicht aus bloßer Präferenz auf frühere Modelle, sondern auf konkrete Erfahrungen aus ihrer Anwendung."),
                ],
                "en": [
                    _link_marele("An important intermediate step was the earlier project MAR.ELE – Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg. In that smaller pilot project, 22 recordings with students from Marburg University were produced. MAR.ELE made Spanish learner pronunciation accessible as corpus material and open to empirical analysis. At the same time, practical work with this corpus also revealed the limits of a design that had been adopted too directly. Those experiences were decisive for the more extensive revision in the present project and are closely tied to the broader project development outlined on <a href=\"/en/project/about\">What this project is about</a>."),
                    _link_marele("For MAR.ELE, the wordlist from the (I)FEC project was adopted in full in order to remain compatible with an established corpus-phonological design for Spanish. Methodologically, that made sense, but it also exposed clear problems in work with learners: some items turned out to be unnecessary lexical stumbling blocks, while other phenomena that are particularly revealing for learner pronunciation were not distributed optimally or were not represented strongly enough. The current design therefore responds not out of mere preference for a different model, but to concrete experience gained in practice."),
                ],
            },
        },
        {
            "heading": {
                "de": "Interview",
                "en": "Interview",
            },
            "paragraphs_html": {
                "de": [
                    "Das Interview ist schließlich eine projektweite Erweiterung des Designs. Es ergänzt die kontrollierten Leseaufgaben um eine reflexive Komponente: Lernende werden nicht nur aufgenommen, sondern auch zu ihrer eigenen Aussprache, zu wahrgenommenen Schwierigkeiten und zu auffälligen Phänomenen befragt, die im Verlauf der Erhebung beobachtet wurden. Damit fließt neben der Außenbeobachtung auch die Perspektive der Lernenden selbst in das Korpus ein. Für die Untersuchung von Lernendenaussprache ist das besonders wichtig, weil so nicht nur Realisierungen dokumentiert, sondern auch metasprachliche Einschätzungen und subjektive Problemwahrnehmungen sichtbar werden.",
                    "Die Interviewkomponente zeigt zugleich, dass das spanische Korpus Teil einer größeren Arbeitsstruktur ist, in der Forschung, Datenerhebung und Materialentwicklung zusammengedacht werden. Informationen zu Mitwirkenden im Gesamtprojekt bündelt die Seite <a href=\"/de/project/team\">Team &amp; Mitwirkende</a>.",
                ],
                "en": [
                    "The interview is, finally, a project-wide extension of the design. It adds a reflective component to the controlled reading tasks: learners are not only recorded, but also asked about their own pronunciation, perceived difficulties, and striking phenomena observed during the recording process. This means that the corpus includes not only external observation, but also the learners' own perspective. For the study of learner pronunciation, this is especially important because it documents not only realisations, but also metalinguistic judgments and subjective perceptions of difficulty.",
                    "At the same time, the interview component shows that the Spanish corpus is part of a broader working structure in which research, data collection, and material development are thought together from the outset. Information on the contributors to the overall project is gathered on <a href=\"/en/project/team\">Team &amp; contributors</a>.",
                ],
            },
        },
        {
            "heading": {
                "de": "Literatur",
                "en": "References",
            },
            "bullets_html": {
                "de": [
                    "(I)FEC: (Inter-)Fonología del Español Contemporáneo.",
                    f'<a href="{MARELE_PROJECT_URL}">MAR.ELE</a>: Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg.',
                ],
                "en": [
                    "(I)FEC: (Inter-)Fonología del Español Contemporáneo.",
                    f'<a href="{MARELE_PROJECT_URL}">MAR.ELE</a>: Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg.',
                ],
            },
        },
    ],
}
