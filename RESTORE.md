# Restauração do checkpoint

## 1. Verificar integridade

Linux/macOS:

```bash
sha256sum -c sitepulse-checkpoint-v1.1.0.zip.sha256
```

PowerShell:

```powershell
Get-FileHash .\sitepulse-checkpoint-v1.1.0.zip -Algorithm SHA256
Get-Content .\sitepulse-checkpoint-v1.1.0.zip.sha256
```

## 2. Extrair

Extraia o ZIP em uma pasta sem acentos ou sincronização ativa, por exemplo:

```text
C:\Projetos\sitepulse
```

## 3. Iniciar

```powershell
Copy-Item .env.example .env
.\scripts\start.ps1
```

## 4. Confirmar

- Dashboard: `http://localhost:3000`
- Saúde da API: `http://localhost:8000/api/v1/health`
- Demo Target: `http://localhost:8080/health`
- Mailpit: `http://localhost:8025`
- Flower: `http://localhost:5555`

## 5. Reset completo

```powershell
.\scripts\reset.ps1
```
