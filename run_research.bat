@echo off
REM Automated Driving Research Agent Runner
REM ======================================

echo Automated Driving Research Agent
echo =================================
echo.

REM Check if API key is provided as argument
if "%1"=="" (
    echo ERROR: Please provide your API key as an argument
    echo.
    echo Usage: run_research.bat YOUR_API_KEY
    echo.
    echo Get your API key from:
    echo  - Google AI Studio: https://aistudio.google.com/
    echo  - Kimi AI: https://platform.moonshot.cn/
    echo.
    pause
    exit /b 1
)

REM Run the research agent
echo Starting research with Gemini Pro...
echo.
python enhanced_ad_research_agent.py --api-key %1 --model gemini

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Research completed successfully!
) else (
    echo.
    echo Research failed with error code %ERRORLEVEL%
)

echo.
pause
