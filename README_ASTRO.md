# 🌿 Blog Mente Leve — Astro + Vercel

Blog de saúde mental e bem-estar construído com **Astro** e pronto para deploy no Vercel.

## 🚀 Quick Start

### Instalação Local

```bash
npm install
npm run dev
```

Acesse: `http://localhost:3000`

### Build para Produção

```bash
npm run build
```

Saída: `dist/`

## 📁 Estrutura

```
src/
├── layouts/
│   └── Layout.astro          # Template principal
├── pages/
│   ├── index.astro           # Homepage (lista artigos)
│   ├── sobre.astro           # Página Sobre
│   ├── contato.astro         # Formulário de contato
│   └── privacidade.astro     # Política de privacidade
dados/
├── calendario_blog_1_ano.csv  # Dados dos artigos
└── saida/html/
    ├── art-001-*.html        # Artigos (gerados pelo Gemini)
    ├── sobre.html
    └── ...
astro.config.mjs              # Configuração Astro
package.json                  # Dependências
vercel.json                   # Configuração Vercel
```

## 📝 Como Adicionar Artigos

1. **Gere o artigo com Gemini**
2. **Salve como HTML** em `dados/saida/html/art-XXX.html`
3. **Atualize o CSV** `dados/calendario_blog_1_ano.csv` com as informações
4. **Build local**: `npm run build`
5. **Push**: `git add . && git commit && git push`
6. **Vercel** faz deploy automático! 🎉

## 🔗 Integração com Gemini

O CSV deve ter estas colunas essenciais:
- `Data` (dd/mm/yyyy)
- `Horário` (09h, 12h, 20h)
- `Tema` (categoria)
- `Palavra-chave principal` (título)
- `Artigo_Arquivo_HTML` (arquivo: art-XXX.html)

## 🌍 Deploy no Vercel

Ja configurado! Vercel detecta `package.json` e `vercel.json` automaticamente.

Apenas faça push para GitHub:
```bash
git push origin main
```

Vercel faz build e publica em: `https://seu-projeto.vercel.app`

## 🎨 Customização

Edite `src/layouts/Layout.astro` para:
- Cores (mudar `#006400` para sua cor)
- Logo (trocar `🌿 Mente Leve`)
- Links de navegação
- Footer

## 📞 Contato

Quer adicionar um formulário de contato funcional?

1. Crie conta em https://formspree.io (gratuito)
2. Obtenha seu Form ID
3. Edite `src/pages/contato.astro` na linha com `YOUR_FORM_ID`

---

**Feito com ❤️ e Astro**
