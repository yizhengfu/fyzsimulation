# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/data/app/deepmd-gpu/3.0.3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/data/app/deepmd-gpu/3.0.3/etc/profile.d/conda.sh" ]; then
        . "/data/app/deepmd-gpu/3.0.3/etc/profile.d/conda.sh"
    else
        export PATH="/data/app/deepmd-gpu/3.0.3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
dp test -m graph-compress.pb -s ./validation_data -n 40 -d results