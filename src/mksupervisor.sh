VAR=$1
BINDIR=$2

cat <<EOF
[program:readingdb]
command = $BINDIR/reading-server -d $VAR/lib/readingdb -p 4242
priority = 2
autorestart = true
stdout_logfile = /var/log/readingdb.stdout.log
stdout_logfile_maxbytes = 50MB
stdout_logfile_backups = 5
stderr_logfile = /var/log/readingdb.stderr.log
stderr_logfile_maxbytes = 50MB
stderr_logfile_backups = 5
EOF
