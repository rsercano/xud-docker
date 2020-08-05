export PS1="{{prompt}}"

function print_help {
    echo "All-in-one help command"
}

function launcher_exec {
    echo "$@" | nc local:/root/launcher.sock
}

function status_command {
    launcher_exec status "$@"
}

function report_command {
    launcher_exec report "$@"
}

function logs_command {
    launcher_exec logs "$@"
}

function start_command {
    launcher_exec start "$@"
}

function stop_command {
    launcher_exec stop "$@"
}

function restart_command {
    launcher_exec restart "$@"
}

function down_command {
    launcher_exec down "$@"
}

function up_command {
    launcher_exec up "$@"
}

alias help="print_help"
alias status="status_command"
alias report="report_command"
alias logs="logs_command"
alias start="start_command"
alias stop="stop_command"
alias restart="restart_command"
alias up="up_command"
alias down="down_command"
alias btcctl="docker exec -it ${NETWORK}_btcd_1 btcctl"
alias ltcctl="docker exec -it ${NETWORK}_ltcd_1 ltcctl"
alias bitcoin-cli="docker exec -it ${NETWORK}_bitcoind_1 bitcoin-cli"
alias litecoin-cli="docker exec -it ${NETWORK}_litecoin_1 litecoin-cli"
alias lndbtc-lncli="docker exec -it ${NETWORK}_lndbtc_1 lncli"
alias lndltc-lncli="docker exec -it ${NETWORK}_lndltc_1 lncli"
alias geth="docker exec -it ${NETWORK}_geth_1 geth"
alias xucli="docker exec -it ${NETWORK}_xud_1 xucli"
alias boltzcli="docker exec -it ${NETWORK}_boltz_1 boltzcli"

# boltzcli shortcut commands

# xucli shortcut commands
