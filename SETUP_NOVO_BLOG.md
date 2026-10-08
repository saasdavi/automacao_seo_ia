# 🚀 Template: Criar Novo Blog com Automação Gemini + Vercel

Este documento guia a replicação do modelo de blog **Mente Leve** para novos projetos.

---

## 📋 O que é este modelo?

Um **blog totalmente automatizado** que:
- ✅ Gera artigos com **Google Gemini AI**
- ✅ Obtém dados com **SerpAPI** (pesquisa, trending topics)
- ✅ Organiza 1 ano de conteúdo em **CSV**
- ✅ Renderiza com **Astro** (SSG rápido)
- ✅ Deploya no **Vercel** (automático)

---

## 🎯 Passo a Passo: Criar Novo Blog

### 1️⃣ **Preparar Repositório**

```bash
# Clonar este repositório como template
git clone https://github.com/saasdavi/automacao_seo_ia.git meu-novo-blog
cd meu-novo-blog

# Renomear repositório (GitHub)
# Settings → Rename → novo-nome
```

---

### 2️⃣ **Customizar Identidade Visual**

#### `src/layouts/Layout.astro`
Editar cores e footer:

```html
<!-- Alterar cores -->
#006400 → sua cor principal
#fafafa → sua cor de fundo

<!-- Alterar footer -->
"🌿 Mente Leve" → "Seu Nome do Blog"
```

#### `src/pages/index.astro`
Editar hero banner:

```javascript
// Alterar tagline
"Conteúdo informativo sobre saúde mental..."
→ "Sua descrição"

// Alterar logo emoji
🌿 → 📱 / 🎯 / 💡 (escolher seu emoji)
```

---

### 3️⃣ **Preparar Dados: CSV + Gemini**

#### A. Criar `dados/calendario_blog_1_ano.csv`

Estrutura necessária:

```csv
Data,Horário,Tema,Palavra-chave principal,Artigo_Arquivo_HTML,Imagem_Miniatura
01/01/2025,09h,Saúde,Dicas de saúde natural,art-001-dicas.html,https://...
02/01/2025,12h,Nutrição,Alimentação saudável,art-002-nutricao.html,https://...
...
```

**Colunas essenciais:**
- `Data` - dd/mm/yyyy
- `Horário` - 09h, 12h, 20h
- `Tema` - categoria (para filtros)
- `Palavra-chave principal` - título do artigo
- `Artigo_Arquivo_HTML` - art-XXX.html
- `Imagem_Miniatura` - URL imagem (opcional)

#### B. Gerar Artigos com Gemini

Script Python (criar `gerar_artigos.py`):

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def gerar_artigo(tema, titulo, numero):
    prompt = f"""
    Escreva um artigo HTML completo sobre: {titulo}
    Tema: {tema}
    
    Requisitos:
    - 800-1200 palavras
    - Subtítulos com <h2>
    - Parágrafos com <p>
    - Lista com <ul><li>
    - Conclusão motivadora
    - Isenção de responsabilidade no final
    
    Retorne APENAS o HTML body (sem <html>, <head>, etc)
    """
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    # Salvar em dados/saida/html/art-{numero}.html
    with open(f"dados/saida/html/art-{numero:03d}.html", "w") as f:
        f.write(response.text)
    
    print(f"✅ art-{numero:03d}.html criado")

# Executar para cada artigo do CSV
gerar_artigo("Saúde", "Dicas de saúde natural", 1)
```

**Executar:**
```bash
export GEMINI_API_KEY="sua-chave-aqui"
python gerar_artigos.py
```

---

### 4️⃣ **Estrutura de Pastas**

```
seu-novo-blog/
├── dados/
│   ├── calendario_blog_1_ano.csv       ← Artigos + datas
│   └── saida/html/
│       ├── art-001-*.html
│       ├── art-002-*.html
│       └── ... (1 por artigo)
├── src/
│   ├── layouts/
│   │   └── Layout.astro               ← Template HTML
│   ├── pages/
│   │   ├── index.astro                ← Homepage
│   │   ├── sobre.astro
│   │   ├── contato.astro
│   │   └── privacidade.astro
├── astro.config.mjs                   ← Config Astro
├── package.json
├── vercel.json                        ← Config Vercel
└── README.md
```

---

### 5️⃣ **Configurar Vercel**

#### A. Criar conta no Vercel
https://vercel.com/signup

#### B. Conectar GitHub
```bash
# Push para GitHub primeiro
git add .
git commit -m "Initial commit: novo blog"
git push origin main
```

#### C. Importar no Vercel
1. Dashboard → "New Project"
2. Selecionar repositório
3. Framework: Astro
4. Deploy! ✅

---

### 6️⃣ **Adicionar Imagem de Fundo (Opcional)**

Editar `src/pages/index.astro`:

```css
.hero-landing {
  background-image: url('https://pixabay.com/seu-imagem.jpg');
  background-size: cover;
  background-attachment: fixed;
}
```

**Fontes de imagem gratuitas:**
- Pixabay.com
- Unsplash.com
- Pexels.com

---

### 7️⃣ **Páginas Estáticas (Customizar)**

#### `src/pages/sobre.astro`
```html
<h1>Sobre Seu Blog</h1>
<p>Sua missão, visão, valores...</p>
```

#### `src/pages/contato.astro`
Integrar com **Formspree** (gratuito):
1. Criar conta: https://formspree.io
2. Obter Form ID
3. Editar formulário com seu ID

#### `src/pages/privacidade.astro`
Adicionar sua política de privacidade

---

## 🔄 Workflow Mensal

### 1. Atualizar CSV
```csv
01/02/2025,09h,Saúde,Novo tópico,art-XXX.html,https://...
```

### 2. Gerar Artigo com Gemini
```bash
python gerar_artigos.py
```

### 3. Commit e Push
```bash
git add .
git commit -m "Feat: adicionar 4 novos artigos fevereiro"
git push origin main
```

### 4. Vercel Deploy Automático ✅

---

## 📊 Resultados Esperados

| Métrica | Resultado |
|---------|-----------|
| Tempo setup | 30 min |
| Tempo criação artigo | 2-3 min (Gemini) |
| Deploy | Automático (1-2 min) |
| Custo/mês | ~$0 (Vercel free) + Gemini API |
| Manutenção | ~1h/mês |

---

## 🎨 Personalizações Populares

### Mudar Cores
```css
/* Layout.astro */
#006400 → #1e3a8a (azul)
#fafafa → #f9fafb (cinza)
```

### Adicionar Logo
```html
<!-- index.astro hero -->
<img src="/logo.svg" width="100" />
```

### Integrar Newsletter
```html
<!-- contato.astro -->
<form action="https://formspree.io/f/SEU_ID" method="POST">
  <input type="email" name="email" placeholder="Seu email">
  <button>Inscrever-se</button>
</form>
```

---

## 🚨 Troubleshooting

### Build falha no Vercel
```bash
# Local: testar build
npm run build

# Se der erro, verificar:
# 1. CSV está bem formatado?
# 2. Arquivos .html existem em dados/saida/html/?
# 3. Sintaxe Astro correta?
```

### Imagens não carregam
```javascript
// index.astro - adicionar fallback
onError="this.style.opacity='0'"
```

### Deploy lento
```json
// vercel.json - aumentar timeout
{
  "buildCommand": "npm run build",
  "env": {
    "NODE_OPTIONS": "--max_old_space_size=3000"
  }
}
```

---

## ✅ Checklist: Novo Blog Pronto

- [ ] CSV com 365 dias de conteúdo
- [ ] Gemini gera todos artigos
- [ ] `src/layouts/Layout.astro` customizado
- [ ] `src/pages/index.astro` customizado
- [ ] Imagem hero adicionada
- [ ] Vercel configurado
- [ ] Deploy automático funcionando
- [ ] Páginas sobre/contato/privacidade feitas
- [ ] README com instruções
- [ ] Teste local: `npm run dev`

---

## 📝 Próximos Passos

1. **SEO**: Adicionar meta tags dinâmicas
2. **Analytics**: Google Analytics em Layout.astro
3. **Newsletter**: Formspree ou Brevo
4. **Social**: Open Graph meta tags
5. **Cache**: Vercel Cache estratégico

---

## 📞 Suporte

Dúvidas? Verifique:
- Astro docs: https://astro.build
- Vercel docs: https://vercel.com/docs
- Gemini API: https://ai.google.dev

---

**Criado com ❤️ usando Astro + Vercel + Gemini**
