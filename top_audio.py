#python3 top_audio.py https://www.youtube.com/@IAmMarkManson/videos 30

import subprocess
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def get_all_videos(channel_url):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",     # ← plus rapide que --dump-json + parsing ligne par ligne
        "--no-warnings",
        "--ignore-errors",
        channel_url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print("Erreur yt-dlp:", result.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
        entries = data.get("entries", [])
    except json.JSONDecodeError:
        print("Erreur de parsing JSON")
        sys.exit(1)

    videos = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("view_count") is not None:
            videos.append({
                "id": entry["id"],
                "title": entry.get("title", "Sans titre"),
                "view_count": entry["view_count"]
            })

    return videos


def download_one(video_id: str, output_dir: str = "."):
    """Fonction appelée en parallèle pour chaque vidéo"""
    cmd = [
        "yt-dlp",
        "-q",                        # vraiment silencieux
        "--no-warnings",
        "-f", "bestaudio[ext=m4a]/bestaudio",
        "--audio-quality", "5",      # 5 ≈ ~128-160kbps, bon compromis
        "--embed-thumbnail",
        "--add-metadata",
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    if len(sys.argv) != 3:
        print("Usage: python top_audio.py <channel_url> <nombre>")
        print("Exemple: python top_audio.py https://www.youtube.com/@MrBeast 15")
        sys.exit(1)

    channel_url = sys.argv[1]
    try:
        top_x = int(sys.argv[2])
    except ValueError:
        print("Le deuxième argument doit être un nombre")
        sys.exit(1)

    print("📥 Récupération de la liste des vidéos (flat playlist)...")
    videos = get_all_videos(channel_url)

    print(f"   → {len(videos):,} vidéos trouvées")

    if not videos:
        print("Aucune vidéo avec nombre de vues trouvé 😕")
        return

    print("🔢 Tri par vues décroissantes...")
    videos.sort(key=lambda v: v["view_count"], reverse=True)

    top_videos = videos[:top_x]

    print("\n🎯 Top sélectionnés :")
    for i, v in enumerate(top_videos, 1):
        print(f"{i:2d}. {v['view_count']:,} vues → {v['title'][:68]}{'...' if len(v['title'])>68 else ''}")

    print(f"\n🚀 Téléchargement parallèle de {len(top_videos)} meilleurs audios...")

    # Dossier de sortie (optionnel)
    output_dir = f"Top_{top_x}_audios_{Path(channel_url).name}"
    Path(output_dir).mkdir(exist_ok=True)

    # Nombre de téléchargements simultanés
    # 4-6 souvent le meilleur compromis (selon ta connexion)
    MAX_WORKERS = 5

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(download_one, video["id"], output_dir)
            for video in top_videos
        ]

        for i, future in enumerate(as_completed(futures), 1):
            try:
                future.result()  # lève l'exception s'il y en a eu une
                print(f"  {i:2d}/{len(top_videos)} terminé", end="\r")
            except Exception as e:
                print(f"\nErreur sur une vidéo : {e}")

    print(f"\n\n✓ Terminé ! {len(top_videos)} fichiers dans le dossier :")
    print(f"   ./{output_dir}\n")


if __name__ == "__main__":
    main()