transfer_github_releases
========================

Transfer release metadata from your GitHub.com repositories to GitHub Enterprise (or another GitHub.com repo).

# Installation

We expect a sane Python 2.7 environment (i.e. have pip installed).

1. Transfer your git repository using [the official documentation](https://enterprise.github.com/help/articles/moving-a-repository-from-github-com-to-github-enterprise).
1. `pip install -r requirements.txt`
1. Edit `transfer.py`: Add personal access tokens and set the target and destination repository.
1. `python transfer.py`

## Example output

```
$ python transfer.py
Release #533208: [1.1.1-rc1] Google Play 1.1.1 RC1
`-----> #39
        Downloading asset Project-beta-62-debug.apk.
        `- Downloaded 20649 kB. Starting upload.
        `- Successfully uploaded asset.
Release #527221: [GooglePlay-1.1] Google Play Feature Branch release (version 1.1)
`-----> #40
        Downloading asset Project-play-release.apk.
        `- Downloaded 20618 kB. Starting upload.
        `- Successfully uploaded asset.
```
