import subprocess
import json
import sys
import re
import unicodedata
import threading
from concurrent.futures import ThreadPoolExecutor

# -------- CONFIG --------
MAX_WORKERS = 3
FORMAT = "best[height<=720][ext=mp4]/best[ext=mp4]"
BASE_OUTPUT_DIR = "./top_video"
# ------------------------

print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


def sanitize(name):
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[\\/*?:"<>|]', '-', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def get_channel_name(channel_url):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--playlist-items", "1",
        channel_url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        name = data.get("uploader") or data.get("channel") or data.get("title") or "unknown_channel"
        return "".join(c for c in name if c.isalnum() or c in " _-").strip()
    except Exception:
        return "unknown_channel"


def get_all_videos(channel_url):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        channel_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'analyse de la chaîne :\n{e.stderr}")
        sys.exit(1)

    videos = []
    for line in result.stdout.splitlines():
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        if data.get("view_count") is not None:
            videos.append({
                "id": data["id"],
                "title": data["title"],
                "view_count": data["view_count"]
            })
        else:
            safe_print(f"⚠️  view_count manquant pour : {data.get('title', data.get('id', '?'))}")

    return videos


def download_one(video, rank, output_dir):
    vid = video["id"]
    filename = f"{rank:02d} - {sanitize(video['title'])}"

    safe_print(f"⬇️  Téléchargement : {filename}")

    try:
        subprocess.run(
            [
                "yt-dlp",
                "-f", FORMAT,
                "--merge-output-format", "mp4",
                "--no-playlist",
                "-o", f"{output_dir}/{filename}.%(ext)s",
                f"https://www.youtube.com/watch?v={vid}"
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        safe_print(f"✅ Terminé : {filename}")
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ Échec pour '{filename}' :\n{e.stderr.decode()}")


def download_videos(videos, output_dir):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(download_one, v, i + 1, output_dir) for i, v in enumerate(videos)]
        for f in futures:
            f.result()


def main():
    if len(sys.argv) != 3:
        print("Usage: python top_videos.py <channel_url> <X>")
        sys.exit(1)

    channel_url = sys.argv[1]

    try:
        top_x = int(sys.argv[2])
        if top_x <= 0:
            raise ValueError
    except ValueError:
        print("❌ <X> doit être un entier positif.")
        sys.exit(1)

    print("📥 Analyse de la chaîne…")
    channel_name = get_channel_name(channel_url)
    output_dir = f"{BASE_OUTPUT_DIR}/{channel_name}"
    videos = get_all_videos(channel_url)

    if not videos:
        print("❌ Aucune vidéo trouvée (view_count disponible).")
        sys.exit(1)

    print(f"📊 {len(videos)} vidéos trouvées")

    videos.sort(key=lambda v: v["view_count"], reverse=True)
    top_videos = videos[:top_x]

    print("\n🔥 Top vidéos sélectionnées :")
    for i, v in enumerate(top_videos, 1):
        print(f"{i}. {v['title']} ({v['view_count']:,} vues)")

    print(f"\n🚀 Téléchargement en parallèle ({MAX_WORKERS} jobs, 720p max)…")
    print(f"📁 Dossier de sortie : {output_dir}\n")
    download_videos(top_videos, output_dir)

    print("\n🎉 Tous les téléchargements sont terminés !")


if __name__ == "__main__":
    main()