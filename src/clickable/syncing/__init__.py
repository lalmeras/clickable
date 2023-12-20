import subprocess
import urllib.parse


def lftp_sync(src, url, excludes=[], delete=True, dry_run=False,
              pre_commands=[]):
    parsed_url = urllib.parse.urlparse(url)
    # url without path
    base_url = urllib.parse.urlunparse([parsed_url.scheme, parsed_url.netloc, '',
                                   None, None, None])
    excludes_args = ['--exclude {}'.format(i) for i in excludes]
    args = []
    args.append('lftp')
    args.append(base_url)
    args.append('-e')
    args.append("""
{pre}
mirror {src} {dest} -R {dry_run} -n {excludes} {delete};
quit
""".format(src=src, dest=parsed_url.path,
           dry_run='--dry-run' if dry_run else '',
           excludes=' '.join(excludes_args),
           delete='--delete' if delete else '',
           pre=';\n'.join(pre_commands)))
    subprocess.check_call(args)


def rsync(src, dest, options=['-az'], excludes=[], delete=True, dry_run=False):
    excludes_args = ['--exclude={}'.format(i) for i in excludes]

    args = []
    # rsync {options} [--dry_run] [--delete] {excludes} {src} {dest}
    args.append('rsync')
    if options:
        args.extend(options)
    if dry_run:
        args.append('--dry-run')
    if delete:
        args.append('--delete')
    if excludes_args:
        args.extend(excludes_args)
    args.append(src)
    args.append(dest)
    subprocess.check_call(args)
