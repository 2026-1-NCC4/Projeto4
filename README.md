# Projeto4

## FECAP - Fundação de Comércio Álvares Penteado

<p align="center">
  <a href="https://www.fecap.br/">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhZPrRa89Kma0ZZogxm0pi-tCn_TLKeHGVxywp-LXAFGR3B1DPouAJYHgKZGV0XTEf4AE&usqp=CAU" alt="FECAP - Fundação de Comércio Álvares Penteado" border="0">
  </a>
</p>

# Dashboard de Indicadores Cannoli - Foodtech

https://dashboard-web-canolli360.streamlit.app

## 👥 Grupo: TechTonics

## Integrantes

* **[Fernanda Loura da Silva](https://www.linkedin.com/in/fernandaloura/)**
* **[Gustavo Henrique Da Silva Santos](https://www.linkedin.com/in/ghsantos24/)**
* **[Lucas Alves Bernardo](https://www.linkedin.com/in/lucas-alves-bernardo-093871252/)**
* **[Nicolly da Silva Soares](https://www.linkedin.com/in/nicolly-silva-soares-10b627171/)**
* **[Thiffany Morais Vieira da Silva](https://www.linkedin.com/in/thiffany-morais/)**

---

### 👨‍🏫 Professor Orientador

* **[Eduardo Savino Gomes](https://www.linkedin.com/in/eduardo-savino)**

### 👨‍🏫 Orientadores Complementares

* **[Lucy Mari Tabuti](https://www.linkedin.com/in/lucymari/)**
* **[Maurício Lopes da Cunha](https://www.linkedin.com/in/maureen-leung-5630492a/)**
* **[Rodnil da Silva Moreira Lisboa](https://www.linkedin.com/in/professorrodnil/)**
* **[Victor Bruno Alexander Rosetti de Quiroz](https://www.linkedin.com/in/victorbarq/)**

## 📌 1. Apresentação do Projeto

A **Cannoli** é uma startup foodtech que integra CRM, automação de engajamento e cardápio digital. O objetivo deste projeto é desenvolver um **Dashboard Web** capaz de apoiar decisões estratégicas e operacionais, permitindo que a Cannoli e seus restaurantes parceiros visualizem dados de vendas, comportamento de clientes e eficácia de campanhas em tempo real (ou via simulação realista).

O dashboard explora princípios de **Ciência de Dados** (modelagem, métricas e inferência) e **Usabilidade** (clareza e hierarquia visual), garantindo segurança e escalabilidade.

---

## 📁 2. Estrutura de Pastas

Conforme os requisitos das disciplinas e a organização atual do repositório:

```text
Projeto4/
├── Documentos/                           # Engenharia de Software e Modelagem
│   ├── ES_e_ML/
│   │   ├── Entrega 1
│   │   └── Entrega 2                          
│   ├── Entrega 1/
│   │   ├── Análise Inferencial de Dados/
│   │   ├── Ciência de Dados/
│   │   └── Contabilidade e Finanças/
│   └── Entrega 2/
│       ├── Análise Inferencial de Dados/
│       ├── Ciência de dados/
│       ├── ColabEntrega_2_Ciencia_de_dados.ipynb
│       ├── Contabilidade e Finanças/
│       └── Entrega2-Ciência de Dados/ #protótipo inicial(app, gráficos, tratamento)
├── src/
│   ├── canolli360/                       # aplicação Streamlit (dashboard principal)
│   │   ├── .streamlit/
│   │   │   └── config.toml               # tema e configuração do Streamlit
│   │   ├── app.py                        # página: Visão geral
│   │   ├── etl.py                        # carga e tratamento dos dados
│   │   ├── funcs.py                      # métricas, filtros e formatação
│   │   ├── graficos.py                   # gráficos (Plotly / Altair)
│   │   ├── menu.py                       # sidebar, navegação e cabeçalho
│   │   ├── paths.py                      # caminhos de arquivos e datasets
│   │   ├── privacidade.py
│   │   ├── pages/
│   │   │   ├── indicadores.py            # página: Indicadores
│   │   │   ├── fidelizacao.py            # página: RFM e retenção
│   │   │   └── campanhas.py              # página: Campanhas
│   │   └── ui/
│   │       ├── dashboard_charts.py       # componentes visuais dos gráficos
│   │       └── dashboard_theme.py        # CSS e tema executivo
│   └── notebooks/
│       └── Entrega1_PI.ipynb             # notebook da Entrega 1 (Ciência de Dados)
├── requirements.txt
└── README.md
```

### Módulos principais (`src/canolli360`)

| Arquivo / pasta | Função |
|-----------------|--------|
| `app.py` | Visão geral com KPIs (receita, pedidos, ticket médio, clientes). |
| `pages/indicadores.py` | Indicadores detalhados da operação. |
| `pages/fidelizacao.py` | Análise RFM e retenção de clientes. |
| `pages/campanhas.py` | Desempenho e eficácia de campanhas. |
| `etl.py` | Leitura da base (CSV/planilhas) ou dados de demonstração. |
| `ui/` | Tema visual e helpers de gráficos reutilizáveis. |

---

## 🚀 3. Como executar localmente

Na raiz do repositório:

```bash
pip install -r requirements.txt
cd src/canolli360
streamlit run app.py
```

O dashboard abre no navegador (por padrão em `http://localhost:8501`). A versão publicada está em [dashboard-web-canolli360.streamlit.app](https://dashboard-web-canolli360.streamlit.app).

---

## 📄 Licença / License

[TechTonics](https://github.com/2026-1-NCC4/Projeto4) © 2026 by [TechTonics](https://github.com/2026-1-NCC4/Projeto4) is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## 📚 Referências

1. Cannoli. Plataforma de CRM, fidelização e inteligência de dados para foodservice. Disponível em: [https://www.cannoli.food/](https://www.cannoli.food/)
