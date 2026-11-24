import argparse
from music_downloader import downloader, config
#import parser

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

def download_file(filepath: str, custom_config: dict):
    return 

def download_link(url: str, split_chapters: bool, custom_config: dict):
    source = downloader.detect_source(url)

    if source == "spotify": 
        print("spotify")
    elif source == "direct_file":
        print("direct")
    elif source == "ytdlp":
        ytdlp_opts = downloader.build_ydl_options(custom_config["output_dir"], split_chapters=split_chapters) 
        downloader.download_with_ytdlp(url, ytdlp_opts)
    else:
        print("Invalid source")
        return

def cli():
    rich.print("[italic blue]Opening cli[/italic blue]")

def main():
    parser = argparse.ArgumentParser(description='Download your music')
    
    parser.add_argument("-f", "-file", dest="file", help="Path to a file containing links")
    parser.add_argument("-l", "-link", dest="link", help="Link to download")
    parser.add_argument("--split-chapters", action=argparse.BooleanOptionalAction, default=True, help="Flag to split chapters")

    args = parser.parse_args()

    custom_config = config.load_config()
    if args.file:
        download_file(args.file, custom_config)
    elif args.link:
        download_link(args.link, split_chapters=args.split_chapters, custom_config=custom_config)
    else:
        cli()

    config.save_config(custom_config)

if __name__ == "__main__":
    main() 
