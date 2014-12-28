#! /bin/bash
pid=$(ps -opid -C 'python pepsite/scripts/trial_imports.pt' );
echo $pid$1;
while [ -d /proc/2883 ]
do
    sleep 1
done && pg_dump hdometwo > 140802_progressing.sql && cp 140802_progressing.sql /home/rimmer/Dropbox/ && source /home/rimmer/hdenv/bin/activate && python /home/rimmer/hdome/pepsite/scripts/trial_imports_all.py > allimportsfinish_01.log && echo 'COMPLETED!!!\n\n';
