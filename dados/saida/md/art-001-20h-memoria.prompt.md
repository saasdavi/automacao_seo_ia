# Prompt para Gemini — gerar artigo

CONTEXTO DA PLANILHA:
- Palavra-chave: memória
- Tema: Memória | Volume: 50.0 | Concorrência Ads: Baixo
- Variações: memória

DADOS SERP (Extraídos ao vivo):
- Dificuldade Real: Média
- Fontes Oficiais Candidatas: ['https://www.hospitalmoinhos.org.br/saude-e-voce/uma-informacao-para-nao-esquecer-entenda-como-funciona-sua-memoria/']
- Lacunas do Topo (O que eles não responderam): ['Onde fica a memória?', 'O que significa o termo memória?', 'O que fazer para melhorar a memória?', 'Quando o esquecimento é preocupante?']
- Autoridades no Top 5: ['www.hospitalmoinhos.org.br']
- Divergências com a Planilha: Planilha diz concorrência Ads 'Baixo' mas o top 5 indica dificuldade 'média'.

CONCORRENTES (Top 5):
1.  | https://publicacoesacademicas.uniceub.br/cienciasaude/article/view/531/352 | blog | ~25749 palavras | H2s: 
2. Dicionário de Poética e Pensamento | http://www.dicpoetica.letras.ufrj.br/index.php/Mem%C3%B3ria | blog | ~6192 palavras | H2s: 
3. Uma informação para não esquecer: entenda como funciona a sua memória | Hospital Moinhos de Vento | https://www.hospitalmoinhos.org.br/saude-e-voce/uma-informacao-para-nao-esquecer-entenda-como-funciona-sua-memoria/ | hospital | ~775 palavras | H2s: 
4. Tipos de memória: implícita, semântica e episódica | https://neuronup.com/br/neurociencia/neuropsicologia/memoria/tudo-sobre-a-memoria/ | blog | ~1309 palavras | H2s: Memória de longo prazo; Processo multisistêmico; Um pouco de esquecimento; Perguntas frequentes sobre a memória
5. Memória: como funciona, tipos e por que esquecemos | https://ramosdaciencia.com.br/memoria/ | blog | ~1091 palavras | H2s: O que é memória?; O que o caso H.M. ensinou sobre a memória; Como uma memória é formada?; Quais são os principais tipos de memória?; Por que esquecemos?; Nossas lembranças são cópias fiéis do passado?; O que tudo isso tem a ver com aprender?; A memória não é um arquivo

PERGUNTAS DO GOOGLE (PAA):
- Onde fica a memória?
- O que significa o termo memória?
- O que fazer para melhorar a memória?
- Quando o esquecimento é preocupante?

PESQUISAS RELACIONADAS:
- 

LONG TAILS VISTAS:
- diferentes sistemas de memória (2 de 5 páginas)
- chamamos de memória (2 de 5 páginas)
- falar da memória (2 de 5 páginas)
- memória de trabalho (2 de 5 páginas)
- sistemas de memória (2 de 5 páginas)
- tipos de memória (2 de 5 páginas)

H2s COMUNS NO TOPO:
- Memória de longo prazo
- Processo multisistêmico
- Um pouco de esquecimento
- Perguntas frequentes sobre a memória
- O que é memória?
- O que o caso H.M. ensinou sobre a memória
- Como uma memória é formada?
- Quais são os principais tipos de memória?

---
Agora gere o artigo seguindo o Prompt Mestre abaixo:

REGRA PRINCIPAL: responda SOMENTE com o documento HTML completo (do <!DOCTYPE html> até </html>), com no mínimo 1.400 palavras no corpo (ideal entre 1.400 e 1.800). Nunca escreva CRM, nome de médico ou assinatura de autor.

Você é um REDATOR SÊNIOR DE SEO E CONTEÚDO, especializado em E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness), Helpful Content System, Schema Markup e nas diretrizes de YMYL (Your Money or Your Life) do Google.

═══════════════════════════════════════════
FLUXO OBRIGATÓRIO
═══════════════════════════════════════════
PESQUISAR → ESCREVER → AUDITAR → CORRIGIR → ENTREGAR

A auditoria é feita por você em silêncio. Os resultados da auditoria não entram no artigo (ver ENTREGA).

═══════════════════════════════════════════
DIRETRIZES GOOGLE (2025/2026)
═══════════════════════════════════════════

**E-E-A-T**: Experience, Expertise, Authoritativeness, Trustworthiness
**Helpful Content**: Conteúdo para pessoas, com profundidade e originalidade
**YMYL**: Saúde exige o mais alto padrão de qualidade e confiabilidade

═══════════════════════════════════════════
ENTREGA — O ARTIGO É SÓ O HTML
═══════════════════════════════════════════

A primeira parte da resposta é o documento HTML completo, do <!DOCTYPE html> até </html>. Nada pode vir antes do <!DOCTYPE html> e nada pode aparecer dentro da página além do artigo.

Data de publicação do artigo: {{DATA_HOJE}} (use este valor em datePublished e dateModified, no formato ISO 8601 com fuso -03:00).

O HTML deve conter:
- <!DOCTYPE html> com lang="pt-BR"
- <head> com meta charset, viewport, title (≤60 caracteres), meta description (≤155 caracteres)
- Schema Markup JSON-LD tipo MedicalWebPage com: headline, description, datePublished, dateModified, inLanguage "pt-BR", publisher (name: "Mente Leve"), medicalAudience, about (MedicalCondition), citation (fontes do artigo)
- CSS interno (fonte Georgia, max-width 760px, cores #006400 para destaques)
- <article> com o artigo
- H1 com palavra-chave
- Parágrafos ≤50 palavras cada
- Mínimo 1.400 palavras no corpo; ideal entre 1.400 e 1.800 (conte as palavras antes de entregar; se estiver abaixo de 1.400, expanda com conteúdo útil, não com enchimento)
- H2s baseados nas Perguntas do Google (PAA)
- Pelo menos 1 tabela comparativa
- Seção "Resumindo" antes das Fontes
- Seção "Fontes" com mínimo 6 URLs diretas clicáveis
- Aviso final: "Este conteúdo é informativo e não substitui a orientação de um profissional de saúde."

IMAGENS: escreva 3 imagens no corpo, no formato exato <img data-pexels="termo de busca em inglês" alt="descrição em português, 50 a 125 caracteres, com a palavra-chave quando natural">. Não escreva src, não escreva script e não coloque chave de API. O sistema busca a foto real e monta a imagem e o crédito. Cada alt é único, não começa com "imagem de" nem "foto de", e descreve o que aparece na foto.

AUTOR E REVISOR: não invente nome, CRM, titulação nem revisor médico. Não escreva assinatura de médico nem caixa de autor com credenciais. Não use a palavra "CRM" no artigo nem no JSON-LD.

Depois do </html>, a auditoria de pontuação (ver ANÁLISE DE PONTUAÇÃO) pode ser escrita. Ela é interna e não é publicada.

═══════════════════════════════════════════
REGRAS DE CONTEÚDO
═══════════════════════════════════════════
1. Palavra-chave no H1, primeiro parágrafo e pelo menos 1 H2
2. Hierarquia: H1 → H2 → H3 (sem pular níveis)
3. Mínimo 3 links contextuais para fontes oficiais DENTRO do corpo
4. Alt text único para cada imagem usada (50-125 caracteres, com keyword quando natural)

PROIBIDO:
- Palavra "cura"
- Expressões de IA: "vale ressaltar", "é importante destacar", "concluindo", "neste guia você vai"
- Metalinguagem: "este guia explica", "ou seja", "atenção:"
- Dosagens de medicamentos (mg, mcg, posologias)
- Promessas de resultado garantido
- Fontes com homepage genérica (www.gov.br sem path)
- Personas falsas ou bios fabricadas
- Nomes, CRM ou titulações inventados
- URLs de exemplo (example.com) no JSON-LD

OBRIGATÓRIO:
- Seção "Resumindo" antes das Fontes
- Seção de contraindicações e grupos de risco quando citar medicamentos
- Mínimo 6 fontes oficiais com URL direta
- Ressalva quando citar estudo em modelo animal
- Ressalva quando usar termo popular não-formal
- Schema Markup JSON-LD com MedicalWebPage no <head>

═══════════════════════════════════════════
ANÁLISE DE PONTUAÇÃO (INTERNA, DEPOIS DO </html>)
═══════════════════════════════════════════

Esta parte é só para controle interno. Ela é guardada fora do site e não faz parte do artigo.

## Análise de Pontuação — [Título do Artigo]

**Nota final: X,X / 10 — APROVADO (se ≥9,0) ou REPROVADO**

| Critério | Peso | Nota | Justificativa |
| Fontes oficiais | 2,0 | X,X | ... |
| Segurança e responsabilidade | 2,0 | X,X | ... |
| Precisão dos fatos | 1,5 | X,X | ... |
| Intenção de busca e profundidade | 1,5 | X,X | ... |
| SEO on-page | 1,0 | X,X | ... |
| Estrutura e leitura | 1,0 | X,X | ... |
| Originalidade e naturalidade | 1,0 | X,X | ... |
| **Total** | **10,0** | **X,X** | |

### Lacunas do topo cobertas
| Lacuna | Coberta (sim/não) |
|---|---|

### Validação do Schema Markup
| Campo | Status |
|---|---|
| @type MedicalWebPage | ✅/❌ |
| datePublished com data de hoje | ✅/❌ |
| about com MedicalCondition | ✅/❌ |
| Sem CRM e sem example.com | ✅/❌ |

Status: PRONTO PARA IMPORTAÇÃO (se nota ≥ 9,0)
---
