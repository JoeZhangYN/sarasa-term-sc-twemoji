@echo off
setlocal

cd /d "%~dp0"

echo ===== Font Patcher: Sarasa Term SC + Color Emoji (Twemoji default, publishable) =====
echo.

:: 1. venv
if not exist .venv (
    echo [build] creating venv...
    python -m venv .venv || goto :fail
)
call .venv\Scripts\activate.bat || goto :fail

:: 2. deps
echo [build] installing fonttools...
pip install -q -r requirements.txt || goto :fail

:: 3. find Sarasa Term SC Regular
set "SARASA=%LOCALAPPDATA%\Microsoft\Windows\Fonts\SarasaTermSC-Regular.ttf"
if not exist "%SARASA%" (
    echo [build] ERROR: Sarasa Term SC Regular not found at:
    echo         %SARASA%
    echo Install from https://github.com/be5invis/Sarasa-Gothic/releases
    goto :fail
)

:: 3b. find Sarasa Mono SC Regular (圈数字全角字形来源 ①②… )
set "SARASAMONO=%LOCALAPPDATA%\Microsoft\Windows\Fonts\SarasaMonoSC-Regular.ttf"
if not exist "%SARASAMONO%" (
    echo [build] ERROR: Sarasa Mono SC Regular not found at:
    echo         %SARASAMONO%
    echo It ships in the same Sarasa-Gothic release; install it (circled-number
    echo full-width glyphs are grafted from it). https://github.com/be5invis/Sarasa-Gothic/releases
    goto :fail
)

:: 3c. graft full-width circled numbers (①②… ❶ ⑴ ㉑ …) Mono -> Term
echo [build] widening circled numbers (Mono -^> Term)...
python patch_circled_width.py "%SARASA%" output\SarasaTermSC-Circled-Regular.ttf --source "%SARASAMONO%" || goto :fail
set "SARASA_PATCHED=output\SarasaTermSC-Circled-Regular.ttf"

:: 4. download Twemoji (primary, CC-BY 4.0, publishable)
echo [build] downloading Twemoji...
python download.py || goto :fail

:: 5. patch Twemoji -> aligned advance + UPM 1000 + Sarasa-matched vertical metrics
echo [build] patching Twemoji to aligned advance + metrics...
python patch_emoji_only.py downloads\TwemojiMozilla.ttf output\TwemojiAligned-Regular.ttf "Twemoji Aligned" --metrics-from "%SARASA%" || goto :fail

:: 6. bundle into TTC (use circled-widened Sarasa Term)
echo [build] bundling TTC...
python build_ttc.py output\SarasaTermSCEmoji.ttc "%SARASA_PATCHED%" output\TwemojiAligned-Regular.ttf || goto :fail

echo.
echo ===== DONE =====
echo Output:
echo   - output\TwemojiAligned-Regular.ttf       (~20KB, 49 emoji subset, publishable CC-BY 4.0)
echo   - output\SarasaTermSC-Circled-Regular.ttf (~24MB, Sarasa Term SC + full-width ①②… )
echo   - output\SarasaTermSCEmoji.ttc            (~24MB, circled-widened Sarasa + Twemoji bundle)
echo.
echo Install ANY of these:
echo.
echo  A. Standalone (recommended):
echo     1. Uninstall the original Sarasa Term SC (same family name, must replace)
echo     2. Double-click output\SarasaTermSC-Circled-Regular.ttf -^> Install for All Users
echo     3. Double-click output\TwemojiAligned-Regular.ttf       -^> Install for All Users
echo     4. settings.json:
echo        "editor.fontFamily": "'Twemoji Aligned', 'Sarasa Term SC', monospace"
echo.
echo  B. TTC single-file bundle:
echo     1. Uninstall existing Sarasa Term SC + standalone emoji font (if any)
echo     2. Double-click output\SarasaTermSCEmoji.ttc -^> Install for All Users
echo     3. Same fontFamily as A
echo.
echo  Circled numbers ①②… now full-width. VS Code editor: works as-is.
echo  Terminals: set ambiguous-width = wide/double, else they overlap (see README).
echo.
echo  Reload VS Code: fully Exit and reopen (Reload Window doesn't refresh font cache)
echo.
echo Alternative (Noto-COLRv1 style, also OFL): re-run with `python download.py --noto`
echo  then patch with patch_emoji_only.py downloads\Noto-COLRv1.ttf ...
echo.
pause
exit /b 0

:fail
echo.
echo ===== BUILD FAILED =====
pause
exit /b 1
