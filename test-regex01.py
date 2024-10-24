import re 

def parse_filename(input):
    results = []
    for idx, filename in enumerate(input):
        print(f"Processing file {idx+1}/{len(input)}: {filename}")

        pattern = re.compile(r'(?P<show_name>.*?)[\s.-]*S(?P<season>\d{2})E(?P<episode>\d{2})[\s.-]*(?P<episode_name>.*?)[.\[]', re.IGNORECASE)
        match = pattern.search(filename)

        if match:
            show_name = match.group('show_name').strip().replace('.', ' ').replace('_', ' ')
            season_episode = f"S{match.group('season')}E{match.group('episode')}"
            episode_name = match.group('episode_name').strip().replace('.', ' ').replace('_', ' ')
            extension = filename.split('.')[-1]

            results.append(f"{show_name} {season_episode} {episode_name}.{extension}")
    return results

input = [
    "Breaking Bad (2008) - S01E01 - Pilot (1080p BluRay x265 Silence).mkv",
    "Mr.Robot.S01E01.eps1.0.hellofriend.mov.1080p.10bit.BluRay.AAC5.1.HEVC-Vyndros.mkv",
    "Parks and Recreation (2009) - S01E01 - Make My Pit a Park (1080p AMZN WEBRip x265 Silence).mkv",
    "Family Guy - S03E02 - Brian Does Hollywood.mkv",
    "Game Of Thrones S01E06.mp4",
    "Chernobyl (2019) - S01E01 - 1.23.45 (1080p BluRay x265 Silence).mkv",
    "Behind Curtain - Director Johan Renck.mkv"
]

matched = parse_filename(input)

for match in matched:
    print(f"Extracted Filenames: {match}")