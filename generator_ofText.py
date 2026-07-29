# lien uniquement joplin://x-callback-url/openNote?id=54a91eea517544de91d831c794eb0e47
# to run: python3 generator_ofText.py
# chaînes sorties: ,'https://www.youtube.com/@IdrissJAberkane','https://www.youtube.com/@QuestionsdHistoire','https://www.youtube.com/@bettercallouss/videos'
import os
import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# YYYYmmDD  — aujourd'hui: 1 avril
telechargeDepuis = '2026' + '0623'

# MAX téléchargements simultanés (augmenter si bonne connexion, baisser si lente)
MAX_WORKERS = 4

audio_channel = [
    'https://www.youtube.com/@_jared', 'https://www.youtube.com/@RadioBanya',
    'https://www.youtube.com/@LePhi', 'https://www.youtube.com/@TechLead', 'https://www.youtube.com/@TechLeadShow',
    'https://www.youtube.com/@ElJj', 'https://www.youtube.com/@YannPiette', 'https://www.youtube.com/@LeRaptor',
    'https://www.youtube.com/@aliabdaal', 'https://www.youtube.com/@Mohamed1percent', 'https://www.youtube.com/@JamesJani',
    'https://www.youtube.com/@MikeHornexplorer', 'https://www.youtube.com/@MarketingMania',
    'https://www.youtube.com/@MarketingManiaDaily', 'https://www.youtube.com/@otto_music',
    'https://www.youtube.com/@DaliDutilleul', 'https://www.youtube.com/@seb_raconte', 'https://www.youtube.com/@RacemFlazi',
]

video_channel = [
    'https://www.youtube.com/@Fireship', 'https://www.youtube.com/@Paulygones',
    'https://www.youtube.com/@Micmaths', 'https://www.youtube.com/@Altis_play',
]

today = datetime.date.today()
formatted_date = today.strftime('%Y%m%d')
new_folder   = f"/Users/ivantorbey/Desktop/a_faire/{formatted_date}"
audio_folder = f"{new_folder}/audio"
video_folder = f"{new_folder}/video"

for folder in [new_folder, audio_folder, video_folder]:
    os.makedirs(folder, exist_ok=True)

# Mise à jour des outils avant téléchargement
print("Mise à jour des outils...")
os.system('brew update && brew upgrade && pipx upgrade yt-dlp')

# Construction des commandes (a et v sont des alias zsh)
FLAGS = f"--playlist-end 15 --dateafter {telechargeDepuis} --concurrent-fragments 4 --retries 5 --restrict-filenames"
tasks = (
    [('audio', f"a {FLAGS} -P '{audio_folder}' '{url}'", url) for url in audio_channel] +
    [('video', f"v {FLAGS} -P '{video_folder}' '{url}'", url) for url in video_channel]
)

# Sauvegarde du script pour référence
script_path = f"{new_folder}/class.sh"
with open(script_path, 'w') as f:
    f.write('brew update && brew upgrade && pipx upgrade yt-dlp\n\n')
    for _, cmd, _ in tasks:
        f.write(cmd + '\n')

def download(task):
    kind, cmd, url = task
    channel = url.rstrip('/').split('/')[-1]
    print(f"  ▶ [{kind}] {channel}")
    # zsh -i pour charger les alias a/v définis dans ~/.zshrc
    result = subprocess.run(['zsh', '-i', '-c', cmd], capture_output=False)
    status = '✓' if result.returncode == 0 else '✗'
    print(f"  {status} [{kind}] {channel}")
    return channel, result.returncode

total = len(tasks)
print(f"\n{total} chaînes à télécharger — {MAX_WORKERS} en parallèle\n")

results = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
    futures = {pool.submit(download, t): t for t in tasks}
    for future in as_completed(futures):
        channel, code = future.result()
        results.append(code)

success = sum(1 for r in results if r == 0)
print(f"\nTerminé : {success}/{total} chaînes téléchargées avec succès.")
print(f"Audio → {audio_folder}")
print(f"Vidéo → {video_folder}")
