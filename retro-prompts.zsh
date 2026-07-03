# retro-prompts.zsh — flip the CURRENT zsh into a period-correct prompt.
#
#   retro c64      -> READY.        retro amiga   -> 1>
#   retro dos      -> C:\>          retro irix    -> indy 1%
#   retro sun      -> sun%          retro next    -> next%
#   retro plan9    -> term%         retro apple2  -> ]
#   retro bbc      -> >             retro green   -> $
#   retro amber    -> >             retro linux   -> futhark:~$
#   retro          -> list machines
#   retro off      -> restore your normal (starship) prompt
#
# Why a command and not per-profile magic: with tmux + starship, a prompt set at
# profile-open is immediately overwritten by starship's precmd hook, and
# ITERM_PROFILE is stale inside tmux. `retro` removes the starship hook while
# active and restores it on `retro off`, so it works in any shell, any profile.
#
# Install (optional): echo 'source ~/Desktop/notebook/code/retro-terminals/retro-prompts.zsh' >> ~/.zshrc
# Or just `source` it in a shell to try it out.

typeset -gA _RETRO_PROMPTS=(
  green    '%F{46}$ %f'
  amber    '%F{214}> %f'
  linux    '%F{250}futhark:%~$ %f'
  sun      '%F{240}sun%% %f'
  irix     '%F{80}indy 1%% %f'
  c64      $'%F{147}READY.\n%f'
  dos      '%F{252}C:\> %f'
  amiga    '%F{255}1> %f'
  next     '%F{245}next%% %f'
  apple2   '%F{46}] %f'
  spectrum '%F{255}> %f'
  atari    '%F{111}READY%f'$'\n'
  bbc      '%F{255}> %f'
  plan9    '%F{240}term%% %f'

  # --- fictional computers ---
  matrix      '%F{46}neo@zion:~$ %f'
  tron        '%F{45}flynn> %f'
  neuromancer '%F{43}case@sprawl:~$ %f'
  hal         '%F{196}HAL> %f'
  pipboy      '%F{40}RobCo> %f'
  severance   '%F{80}MDR> %f'
  cyberpunk   '%F{220}V@nightcity:~$ %f'
  bladerunner '%F{215}esper> %f'
  wopr        '%F{45}WOPR> %f'
  outrun      '%F{205}outrun> %f'
  lcars       '%F{208}LCARS> %f'

  # --- aesthetic movements ---
  steampunk   '%F{179}aether> %f'
  solarpunk   '%F{29}garden> %f'
  dieselpunk  '%F{137}works> %f'
  vaporwave   '%F{159}vapor> %f'
  atompunk    '%F{30}atom> %f'

  # --- Alien / Blade Runner megacorps ---
  openstep    '%F{246}openstep%% %f'
  weyland     '%F{179}wy> %f'
  mother      '%F{43}MU/TH/UR> %f'
  muthur      '%F{46}MU/TH/UR> %f'
  apollo      '%F{75}APOLLO> %f'
  tyrell      '%F{179}tyrell> %f'
  wallace     '%F{80}wallace> %f'
  vk          '%F{208}V-K> %f'
)

typeset -ga _retro_saved_precmd
typeset -g  _retro_active=0

retro() {
  emulate -L zsh
  local name="$1"

  if [[ -z "$name" ]]; then
    print -r -- "retro <machine> — one of:"
    print -r -- "  ${(k)_RETRO_PROMPTS}"
    print -r -- "  retro off   (restore your normal prompt)"
    return 0
  fi

  if [[ "$name" == off ]]; then
    if (( _retro_active )); then
      precmd_functions=("${_retro_saved_precmd[@]}")   # re-arm starship etc.
      unset PROMPT RPROMPT
      _retro_active=0
      print -r -- "retro: off"
    fi
    return 0
  fi

  local p="${_RETRO_PROMPTS[$name]}"
  if [[ -z "$p" ]]; then
    print -r -- "retro: unknown machine '$name'. try: ${(k)_RETRO_PROMPTS}"
    return 1
  fi

  if (( ! _retro_active )); then
    _retro_saved_precmd=("${precmd_functions[@]}")     # remember the real hooks once
  fi
  precmd_functions=(${precmd_functions:#starship_precmd})  # silence starship redraws
  RPROMPT=''
  PROMPT="$p"
  _retro_active=1
}

# tab-completion: `retro <TAB>` lists the machines
_retro() { compadd off ${(k)_RETRO_PROMPTS}; }
compdef _retro retro 2>/dev/null

# tiny quality-of-life: `retro?` -> help
alias 'retro?'='retro'
