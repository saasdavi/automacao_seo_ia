# 🚀 Guia de Deploy no Vercel — Blog Mente Leve

## ✅ Pré-requisitos

Você já tem:
- ✅ Repositório GitHub (`saasdavi/automacao_seo_ia`)
- ✅ Automação com Gemini gerando artigos
- ✅ CSV do calendário (`dados/calendario_blog_1_ano.csv`)
- ✅ Script Python para gerar homepage (`scripts/gerar_home.py`)
- ✅ `vercel.json` configurado

## 📋 Fluxo Completo de Deploy

### 1️⃣ **Preparar os Artigos Localmente** (seu computador)

```bash
# Clonar o repositório
git clone https://github.com/saasdavi/automacao_seo_ia
cd automacao_seo_ia

# Instalar dependências
pip install -r requirements.txt

# Gerar stubs HTML para todos os artigos do calendário
python scripts/processar_artigos.py --gerar-faltantes

# Validar que tudo está OK
python scripts/processar_artigos.py --validar

# Gerar a homepage (index.html)
python scripts/gerar_home.py

# Verificar que a pasta saida/html/ tem os arquivos
ls -la dados/saida/html/
```

Você verá algo como:
```
index.html
art-001-09h-estresse.html
art-002-12h-meditacao.html
sobre.html
privacidade.html
...
```

### 2️⃣ **Fazer Commit e Push para GitHub**

```bash
# Confirmar mudanças
git add .
git commit -m "Build: gerar arquivos HTML para deploy"
git push origin main
```

### 3️⃣ **Conectar no Vercel**

#### **Opção A: Usando o Dashboard (mais fácil)**

1. Acesse https://vercel.com
2. Clique em **"New Project"**
3. Selecione **"Import Git Repository"**
4. Procure por `saasdavi/automacao_seo_ia` e clique em **"Import"**
5. Na tela de configuração:
   - **Project Name**: `blog-mente-leve` (ou seu nome preferido)
   - **Framework Preset**: `Other`
   - **Root Directory**: `.` (deixe em branco = raiz do repositório)
   - **Build Command**: Será detectado do `vercel.json` ✅
   - **Output Directory**: `dados/saida/html` ✅
6. Clique em **"Deploy"**

#### **Opção B: Usando CLI (avançado)**

```bash
# Instalar Vercel CLI
npm install -g vercel

# Fazer login
vercel login

# Deploy automático
vercel
```

### 4️⃣ **Configurar Domínio** (opcional)

Após o deploy, você terá um link tipo: `https://blog-mente-leve.vercel.app`

Para usar um domínio customizado:

1. No dashboard do Vercel, vá para **Settings → Domains**
2. Clique em **"Add Domain"**
3. Digite seu domínio (ex: `blog.seudominio.com`)
4. Siga as instruções para apontar o DNS

## 🔄 Automatizar Tudo com GitHub Actions

Para publicar automaticamente quando artigos forem gerados:

1. Crie `.github/workflows/deploy-vercel.yml`:

```yaml
name: Deploy para Vercel

on:
  push:
    branches: [main]
    paths:
      - 'dados/saida/html/**'
      - 'dados/calendario_blog_1_ano.csv'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Instalar dependências
        run: pip install -r requirements.txt
      
      - name: Gerar homepage
        run: python scripts/gerar_home.py
      
      - name: Deploy no Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./dados/saida/html
```

2. Adicionar secrets no GitHub:
   - Vá em: **Settings → Secrets and variables → Actions**
   - Clique em **"New repository secret"**
   - Adicione:
     - `VERCEL_TOKEN`: Token do Vercel (gera em https://vercel.com/account/tokens)
     - `VERCEL_ORG_ID`: ID da organização Vercel
     - `VERCEL_PROJECT_ID`: ID do projeto Vercel

## 📊 Fluxo de Publicação do Blog

```
1. Gemini gera artigo HTML
2. ↓
3. Você salva em dados/saida/html/art-XXX.html
4. ↓
5. Executa: python scripts/gerar_home.py
6. ↓
7. Commit + push para GitHub
8. ↓
9. GitHub Action roda: gera homepage + deploy no Vercel
10. ↓
11. Blog atualizado em tempo real! 🎉
```

## 🛠️ Ferramentas Úteis

### Validar HTML dos artigos
```bash
python scripts/processar_artigos.py --validar
```

### Regenerar apenas a homepage
```bash
python scripts/gerar_home.py
```

### Testar localmente (opcional)
```bash
# Instalar http-server (se tiver Node)
npm install -g http-server

# Servir local
cd dados/saida/html
http-server
# Abrir http://localhost:8080
```

## ❓ Troubleshooting

### "Build failed" no Vercel
- Verifique se `dados/saida/html/` existe e tem arquivos
- Confirme que `vercel.json` está no repositório
- Veja os logs no dashboard do Vercel

### Homepage não mostra artigos
- Rode: `python scripts/gerar_home.py` localmente
- Verifique se `calendario_blog_1_ano.csv` tem dados
- Confira se a coluna `Artigo_Arquivo_HTML` está preenchida

### Artigo está com stub (texto "em breve")
- Copie o HTML real do Gemini
- Salve em `dados/saida/html/art-XXX.html`
- Rode `python scripts/gerar_home.py`
- Push para GitHub

## 📞 Dúvidas?

- **Vercel**: https://vercel.com/docs
- **GitHub Actions**: https://docs.github.com/actions
- **Python**: https://docs.python.org

---

**Seu blog está pronto para ir ao ar!** 🌿 Mente Leve
