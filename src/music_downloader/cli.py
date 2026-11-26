import argparse
from music_downloader import downloader, config, parser
from pathlib import Path

import rich 
import InquirerPy

""" This function will evaluate for 2 case cenarios
   1. Argument passing on run, this means the user will run like these two opts:

       # link flag
       - soundpp-dl -l audio-link 
       - soundpp-dl -link audio-link 

       # file flag
       - soundpp-dl -f links.txt 
       - soundpp-dl -file links.txt 

       The given file should be a readable file like txt in the following format:
            link 1
            link 2
            link 3 
            # comment (ignored by the link parser) 
            link 4 
        
       So, any text line that starts with # (whitespace doesn't count) will be counted as comment.

   2. Actual CLI app.

       [TODO]

"""

def download_file(filepath: str, split_chapters:bool, custom_config: dict, filetype: str):

    path = Path(filepath).expanduser().resolve()
    if not path.is_file():
        rich.print("[red]ERROR:[/red] Invalid file or file does not exist!")
        return

    with open(path, "r", encoding="utf-8") as f:
        links = parser.parse_links(f.read().splitlines())
        
        if not links:
            rich.print("[yellow]Warning:[/yellow] File exists but has not links")
            return

        for link in links:
            download_link(link, split_chapters=split_chapters, custom_config=custom_config, filetype=filetype)

def download_link(url: str, split_chapters: bool, custom_config: dict, filetype: str):
    return downloader.process_link(url,custom_config["output_dir"],filetype, split_chapters)

def cli():
    rich.print("[italic blue]Opening cli[/italic blue]")

def main():
    parser = argparse.ArgumentParser(description='Download your music')
    
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("-f", "--file", dest="file", help="Path to a file containing links")
    source_group.add_argument("-l", "--link", dest="link", help="Link to download")

    parser.add_argument("--split-chapters", action=argparse.BooleanOptionalAction, default=False, help="Split by video chapters")
    parser.add_argument("-ft", "--filetype", dest="filetype", default="mp3", choices=["mp3", "flac", "wav", "m4a", "ogg", "opus"], help="Filetype may be one of the following: .mp3, .flac, .wav, .m4a, .ogg, .opus")
    parser.add_argument("-o", "--out", dest="out", help="Custom output folder")

    args = parser.parse_args()
    custom_config = config.load_config()

    if args.out:
        custom_config["output_dir"] = str(Path(args.out).expanduser().resolve())

    if args.file:
        download_file(args.file, split_chapters=args.split_chapters, custom_config=custom_config, filetype=args.filetype)
    elif args.link:
        download_link(args.link, split_chapters=args.split_chapters, custom_config=custom_config, filetype=args.filetype)
    else:
        cli()

    if not args.out:
        config.save_config(custom_config)

if __name__ == "__main__":
    main() 
