$raizes = @(
  "HKLM:\SOFTWARE\WOW6432Node\KasperskyLab",
  "HKLM:\SOFTWARE\KasperskyLab"
)
$alvos = @("opencode")
$achou = @()
$testados = 0

function TestaValor($nome, $valor) {
  $script:testados++
  $texto = ""
  if ($valor -is [byte[]]) {
    $texto = [System.Text.Encoding]::ASCII.GetString($valor) + "|" + [System.Text.Encoding]::Unicode.GetString($valor)
  } elseif ($valor -is [string]) {
    $texto = $valor
  } elseif ($valor -is [array]) {
    $texto = ($valor -join "|")
  }
  if (-not $texto) { return }
  foreach ($a in $script:alvos) {
    if ($texto -match $a) {
      $script:achou += ("[" + $script:caminhoAtual + "] " + $nome + " => " + ($texto.Substring(0, [Math]::Min(300, $texto.Length))))
    }
  }
}

foreach ($raiz in $raizes) {
  if (-not (Test-Path $raiz)) { continue }
  Get-ChildItem $raiz -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $script:caminhoAtual = $_.PSPath -replace "Microsoft.PowerShell.Core\\Registry::", ""
    $chave = Get-Item $_.PSPath -ErrorAction SilentlyContinue
    if ($chave) {
      foreach ($vn in $chave.GetValueNames()) {
        try { TestaValor $vn $chave.GetValue($vn) } catch {}
      }
    }
  }
}

Write-Host ("valores verificados: " + $testados)
Write-Host ("ocorrencias com 'opencode': " + $achou.Count)
if ($achou.Count -gt 0) {
  $achou | Select-Object -First 10 | ForEach-Object { Write-Host ("  " + $_) }
} else {
  Write-Host "  Nenhuma exclusao com 'opencode' no registro do Kaspersky"
}
