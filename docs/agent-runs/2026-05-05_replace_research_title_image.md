# 2026-05-05 · Research Title Image Replacement

## Scope

- replace the research landing-card image with the exact user-provided `IMG_6026_Kopie.JPEG` photo
- crop the source to a web-friendly 16:9 title image and keep file size modest for the card slot
- update the landing-card content reference and alt text

## Changes

- created `app/static/img/cards/research_title_image.jpg` from `app/static/img/cards/IMG_6026_Kopie.JPEG`
- updated the research landing card in `app/src/app/routes/public_content.py` to point at the new asset
- updated the research card alt text to match the waveform-monitor recording-studio motif

## Validation

- `app/src/app/routes/public_content.py` passed `get_errors`
- browser checked the live landing page on `http://127.0.0.1:8000/de` and `http://127.0.0.1:8000/en`
- confirmed the new image renders correctly in both locales on the landing cards

## Correction

- an earlier pass briefly used the wrong source image
- the final asset now comes from the exact file `app/static/img/cards/IMG_6026_Kopie.JPEG` placed by the user
