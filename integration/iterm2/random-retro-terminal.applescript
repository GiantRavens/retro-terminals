-- Random Retro Terminal — open a NEW window wearing a randomly chosen machine.
--
-- Installed into iTerm2's scripts folder it appears under Scripts in the menu
-- bar; installed into that folder's AutoLaunch/ it also fires once at every
-- iTerm2 launch. install.sh does both.
--
-- Why a new window rather than repainting this one: `retro random` works
-- through OSC 4/10/11/12, which reach the text grid and nothing else. The
-- FONT and iTerm2's own chrome -- status bar, tabs, window frame -- are bound
-- to the profile and resolved when the session is created, so no escape
-- sequence can move them. Creating the window from the profile is the only
-- way the whole machine arrives.
--
-- AppleScript rather than Python on purpose: a .py script runs under iTerm2's
-- bundled, version-pinned Python runtime, which app updates have broken
-- before. This depends on nothing but iTerm2.
--
-- @RETRO_RANDOM@ is rewritten by install.sh with the absolute path.
delay 1
try
	do shell script quoted form of "@RETRO_RANDOM@" & " >/dev/null 2>&1"
on error errMsg
	display notification errMsg with title "Random Retro Terminal failed"
end try
