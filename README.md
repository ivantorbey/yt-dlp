# yt-dlp scripts

Scripts Python pour télécharger des vidéos et audios YouTube via [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Prérequis

```bash
pipx install yt-dlp
```

## Scripts

### `generator_ofText.py`

Télécharge les dernières vidéos/audios d'une liste de chaînes YouTube en parallèle.

- Configure les chaînes directement dans le fichier (`audio_channel`, `video_channel`)
- Modifie `telechargeDepuis` pour changer la date de départ
- Nécessite les alias `a` (audio) et `v` (vidéo) dans ton shell

```bash
python3 generator_ofText.py
```

---

### `top_audio.py`

Télécharge les N audios les plus vus d'une chaîne YouTube.

```bash
python3 top_audio.py <url_chaîne> <nombre>
```

**Exemple :**
```bash
python3 top_audio.py https://www.youtube.com/@MrBeast 10
```

---

### `top_videos.py`

Télécharge les N vidéos les plus vues d'une chaîne YouTube (720p max, format mp4).

```bash
python3 top_videos.py <url_chaîne> <nombre>
```

**Exemple :**
```bash
python3 top_videos.py https://www.youtube.com/@Fireship 5
```
