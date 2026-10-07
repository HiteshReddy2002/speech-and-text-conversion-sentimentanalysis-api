Add-Type -AssemblyName System.Speech

$csvPath = Join-Path $PSScriptRoot "dataset_v2.csv"
$audioDir = Join-Path $PSScriptRoot "audio"
if (-not (Test-Path $audioDir)) {
    New-Item -ItemType Directory -Path $audioDir | Out-Null
}

$csv = Import-Csv -Path $csvPath
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$count = 0

foreach ($row in $csv) {
    $qid = $row.question_id
    $qtext = $row.question_text
    $wavPath = Join-Path $audioDir "$qid.wav"

    if (-not (Test-Path $wavPath) -or (Get-Item $wavPath).Length -lt 1000) {
        $synth.SetOutputToWaveFile($wavPath)
        $synth.Speak($qtext)
        $count++
    }
}

$synth.Dispose()
Write-Output "Successfully synthesized $count audio files."
