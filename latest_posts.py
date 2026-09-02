# ABOUTME: Refreshes the "Latest Writing" list in README.md from the estebantorr.es RSS feed.
# ABOUTME: Source: https://github.com/eugeneyan/eugeneyan/

import feedparser
import pathlib
import re
import sys
import time

FEED_URL = 'https://estebantorr.es/rss.xml'
POST_COUNT = 5

root = pathlib.Path(__file__).parent.resolve()

# Find the search trigger in readme
# This is done by searching for comment blocks for "Blogpost"
# e.g. "Blogpost starts" "Blogpost ends" in readme
def replace_writing(content, marker, chunk, inline=False):
    r = re.compile(
        r'<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->'.format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = '\n{}\n'.format(chunk)
    chunk = '<!-- {} starts -->{}<!-- {} ends -->'.format(marker, chunk, marker)
    return r.sub(chunk, content)

# Fetch the latest posts by feedparser
def fetch_writing():
    entries = feedparser.parse(FEED_URL)['items']
    return [
               {
                   'title': entry['title'],
                   'url': entry['link'].split('#')[0],
                   'published': time.strftime('%d %b %Y', entry['published_parsed']),
               }
               for entry in entries[:POST_COUNT]
           ], len(entries)

# Execution the code
if __name__ == '__main__':
    readme_path = root / 'README.md'
    readme = readme_path.open().read()
    entries, entry_count = fetch_writing()

    # An empty feed means a broken/moved endpoint. Bail out instead of wiping
    # the list from the README.
    if not entries:
        sys.exit('No entries found in {} — leaving README.md untouched.'.format(FEED_URL))

    print(f'Recent {POST_COUNT}: {entries}, Total count: {entry_count}')
    entries_md = '\n'.join(
        ['* [{title}]({url}) - {published}'.format(**entry) for entry in entries]
    )

    # Update entries
    rewritten_entries = replace_writing(readme, 'Blogpost', entries_md)
    readme_path.open('w').write(rewritten_entries)
