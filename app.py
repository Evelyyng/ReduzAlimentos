
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import date, datetime

# =====================================================
# 1. CONFIGURACAO DA PAGINA
# =====================================================

st.set_page_config(
    page_title="ReduzAlimentos",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO = "dados_reduzalimentos.csv"

COLUNAS = [
    "ID",
    "Data",
    "Alimento",
    "Categoria",
    "Utilizado (kg)",
    "Descartado (kg)",
    "Aproveitado (kg)",
    "Desperdicio (%)",
    "Motivo",
    "Observacoes"
]

# =====================================================
# 2. IDENTIDADE VISUAL
# =====================================================


st.markdown("""
<style>

/* FUNDO GERAL */
.stApp {
    background-color: #F4F7F3;
    color: #244B35;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* TITULOS E TEXTOS */
h1, h2, h3, h4, h5, h6 {
    color: #214F37 !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown,
[data-testid="stCaptionContainer"] {
    color: #365B45;
}

/* MENU LATERAL */
section[data-testid="stSidebar"] {
    background-color: #E8F0E5;
    border-right: 1px solid #D2E1CE;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #214F37 !important;
}

/* INDICADORES */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE8D8;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 3px 12px rgba(40, 80, 50, 0.05);
}

div[data-testid="stMetricLabel"] {
    color: #55735F !important;
}

div[data-testid="stMetricValue"] {
    color: #245B3C !important;
    font-weight: 700 !important;
}

div[data-testid="stMetricDelta"] {
    color: #365B45 !important;
}

/* CAMPOS DE TEXTO */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #214F37 !important;
    border: 1px solid #BFD2BE !important;
    border-radius: 8px !important;
}

/* PLACEHOLDERS */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #718777 !important;
    opacity: 1;
}

/* CAMPOS DE SELEÇÃO */
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
}

.stSelectbox div[data-baseweb="select"] *,
.stMultiSelect div[data-baseweb="select"] * {
    color: #214F37 !important;
}

/* OPÇÕES DOS MENUS */
div[role="listbox"],
div[role="option"] {
    background-color: #FFFFFF !important;
    color: #214F37 !important;
}

/* BOTÕES PRINCIPAIS */
.stButton button,
.stDownloadButton button,
.stFormSubmitButton button {
    background-color: #34734F !important;
    color: #FFFFFF !important;
    border: 1px solid #34734F !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1rem;
}

/* TEXTO INTERNO DOS BOTÕES */
.stButton button *,
.stDownloadButton button *,
.stFormSubmitButton button * {
    color: #FFFFFF !important;
}

/* EFEITO AO PASSAR O MOUSE */
.stButton button:hover,
.stDownloadButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #245B3C !important;
    border-color: #245B3C !important;
    color: #FFFFFF !important;
}

/* BOTÕES DESABILITADOS */
.stButton button:disabled,
.stDownloadButton button:disabled {
    background-color: #A8BBAA !important;
    color: #FFFFFF !important;
}

/* BOTÕES DE RÁDIO E CHECKBOX */
.stRadio label,
.stCheckbox label {
    color: #214F37 !important;
}

/* CARTÕES DE CONTEÚDO */
.cartao {
    background-color: #FFFFFF;
    border: 1px solid #DCE8D8;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 15px;
}

/* MENSAGENS DO SISTEMA */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

div[data-testid="stAlert"] p {
    color: inherit !important;
}

/* TABELAS */
div[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE8D8;
    border-radius: 10px;
    overflow: hidden;
}

/* DIVISÓRIAS */
hr {
    border-color: #DCE8D8 !important;
}

/* RODAPÉ */
.rodape {
    color: #b7e4c7 !important;
    font-size: 13px;
    text-align: center;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. FUNCOES DE DADOS
# =====================================================

def carregar_dados():

    if os.path.exists(ARQUIVO):

        try:
            dados = pd.read_csv(ARQUIVO)

            for coluna in COLUNAS:
                if coluna not in dados.columns:
                    dados[coluna] = None

            dados = dados[COLUNAS]

            dados["Data"] = pd.to_datetime(
                dados["Data"],
                errors="coerce"
            ).dt.date

            return dados

        except Exception:
            st.error(
                "Não foi possível carregar o histórico. "
                "Verifique o arquivo de dados."
            )

    return pd.DataFrame(columns=COLUNAS)


def salvar_dados(dados):

    dados.to_csv(
        ARQUIVO,
        index=False,
        encoding="utf-8-sig"
    )


def calcular_desperdicio(utilizado, descartado):

    if utilizado <= 0:
        return 0

    return (descartado / utilizado) * 100


def classificar_risco(percentual, limite):

    if percentual > limite:
        return "Risco elevado"

    return "Dentro do limite"


def gerar_recomendacao(motivo, percentual):

    recomendacoes = {

        "Vencimento":
        "Revisar o controle de validade, "
        "o armazenamento e o planejamento de compras.",

        "Preparo excessivo":
        "Ajustar a quantidade preparada conforme "
        "a demanda observada.",

        "Armazenamento inadequado":
        "Verificar as condições de armazenamento "
        "e a organização dos alimentos.",

        "Aparência ou qualidade":
        "Avaliar o recebimento, a conservação "
        "e os critérios de seleção dos alimentos.",

        "Sobras de produção":
        "Reavaliar o planejamento da produção "
        "e a quantidade preparada.",

        "Outros":
        "Investigar a causa do descarte e registrar "
        "mais detalhes para facilitar a análise."
    }

    if percentual > 10:
        return recomendacoes.get(
            motivo,
            recomendacoes["Outros"]
        )

    return (
        "Continue acompanhando os registros para "
        "identificar possíveis oportunidades de melhoria."
    )


# =====================================================
# 4. CARREGAMENTO E CONFIGURACOES
# =====================================================

if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

if "limite" not in st.session_state:
    st.session_state.limite = 10.0

dados = st.session_state.dados


# =====================================================
# 5. MENU LATERAL
# =====================================================

with st.sidebar:

    st.markdown(
        "<h1 style='color:#245B3C;'>🌱 ReduzAlimentos</h1>",
        unsafe_allow_html=True
    )

    st.caption("Sistema de gestão de desperdício alimentar")

    st.divider()

    pagina = st.radio(
        "NAVEGAÇÃO",
        [
            "Visão geral",
            "Registrar alimento",
            "Análise de desperdício",
            "Histórico",
            "Configurações"
        ]
    )

    st.divider()

    st.markdown("### Limite de desperdício")

    st.session_state.limite = st.number_input(
        "Percentual máximo desejado (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.limite),
        step=1.0
    )

    st.caption(
        "O limite é ajustável conforme a realidade "
        "do estabelecimento."
    )

    st.divider()

    st.caption("ReduzAlimentos | Versão 2.0")


# Atualiza os dados após alterações
dados = st.session_state.dados
limite = st.session_state.limite


# =====================================================
# 6. CABECALHO
# =====================================================

st.markdown(
    """
    <div style="
        background: linear-gradient(110deg, #214F37, #3F8056);
        padding: 28px;
        border-radius: 16px;
        margin-bottom: 25px;
    ">
        <h1 style="color:white !important; margin:0;">
            ReduzAlimentos
        </h1>
        <p style="color:#E5F2E5 !important; margin-top:8px;">
            Monitoramento e prevenção do desperdício alimentar
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =====================================================
# 7. VISAO GERAL
# =====================================================

if pagina == "Visão geral":

    st.header("Painel de controle")

    st.write(
        "Acompanhe os principais indicadores "
        "de utilização e descarte de alimentos."
    )

    if not dados.empty:

        total_utilizado = dados["Utilizado (kg)"].sum()
        total_descartado = dados["Descartado (kg)"].sum()
        total_aproveitado = dados["Aproveitado (kg)"].sum()

        percentual_geral = calcular_desperdicio(
            total_utilizado,
            total_descartado
        )

        quantidade_registros = len(dados)

    else:

        total_utilizado = 0
        total_descartado = 0
        total_aproveitado = 0
        percentual_geral = 0
        quantidade_registros = 0

    # Indicadores

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Registros realizados",
        quantidade_registros
    )

    c2.metric(
        "Total utilizado",
        f"{total_utilizado:.2f} kg"
    )

    c3.metric(
        "Total descartado",
        f"{total_descartado:.2f} kg"
    )

    c4.metric(
        "Desperdício geral",
        f"{percentual_geral:.2f}%"
    )

    st.divider()

    st.subheader("Acompanhamento do desperdício")

    if dados.empty:

        st.info(
            "Ainda não existem registros. "
            "Acesse 'Registrar alimento' para começar."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("#### Utilização dos alimentos")

            comparacao = pd.DataFrame({
                "Categoria": [
                    "Aproveitado",
                    "Descartado"
                ],
                "Quantidade (kg)": [
                    total_aproveitado,
                    total_descartado
                ]
            })

            st.bar_chart(
                comparacao.set_index("Categoria")
            )

        with col2:

            st.markdown("#### Situação do desperdício")

            st.metric(
                "Limite configurado",
                f"{limite:.1f}%"
            )

            if percentual_geral > limite:

                st.error(
                    "O desperdício geral está acima "
                    "do limite estabelecido."
                )

            else:

                st.success(
                    "O desperdício geral está dentro "
                    "do limite estabelecido."
                )

        st.divider()

        st.subheader("Últimos registros")

        recentes = dados.tail(5).copy()

        st.dataframe(
            recentes[
                [
                    "Data",
                    "Alimento",
                    "Utilizado (kg)",
                    "Descartado (kg)",
                    "Desperdicio (%)"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Por que acompanhar o desperdício?")

    st.write(
        "O monitoramento permite identificar perdas, "
        "avaliar a eficiência do uso dos alimentos "
        "e encontrar oportunidades para melhorar "
        "o planejamento da produção."
    )


# =====================================================
# 8. REGISTRAR ALIMENTO
# =====================================================

elif pagina == "Registrar alimento":

    st.header("Registro de alimentos")

    st.write(
        "Preencha as informações para calcular "
        "o percentual de desperdício."
    )

    with st.form("formulario_registro"):

        col1, col2 = st.columns(2)

        with col1:

            alimento = st.text_input(
                "Nome do alimento",
                placeholder="Ex.: Arroz"
            )

            categoria = st.selectbox(
                "Categoria",
                [
                    "Grãos e cereais",
                    "Frutas",
                    "Verduras e legumes",
                    "Carnes e ovos",
                    "Laticínios",
                    "Outros"
                ]
            )

            data_registro = st.date_input(
                "Data do registro",
                value=date.today()
            )

        with col2:

            utilizado = st.number_input(
                "Quantidade utilizada (kg)",
                min_value=0.0,
                step=0.5,
                format="%.2f"
            )

            descartado = st.number_input(
                "Quantidade descartada (kg)",
                min_value=0.0,
                step=0.1,
                format="%.2f"
            )

            motivo = st.selectbox(
                "Principal motivo do descarte",
                [
                    "Vencimento",
                    "Preparo excessivo",
                    "Armazenamento inadequado",
                    "Aparência ou qualidade",
                    "Sobras de produção",
                    "Outros"
                ]
            )

        observacoes = st.text_area(
            "Observações adicionais",
            placeholder=(
                "Descreva detalhes que ajudem "
                "a identificar a causa do desperdício..."
            )
        )

        enviar = st.form_submit_button(
            "Registrar e analisar",
            use_container_width=True
        )

    if enviar:

        if not alimento.strip():

            st.error("Informe o nome do alimento.")

        elif utilizado <= 0:

            st.error(
                "A quantidade utilizada deve ser maior que zero."
            )

        elif descartado > utilizado:

            st.error(
                "A quantidade descartada não pode "
                "ser maior que a utilizada."
            )

        else:

            aproveitado = utilizado - descartado

            percentual = calcular_desperdicio(
                utilizado,
                descartado
            )

            registro = {
                "ID": str(uuid.uuid4()),
                "Data": data_registro,
                "Alimento": alimento.strip(),
                "Categoria": categoria,
                "Utilizado (kg)": utilizado,
                "Descartado (kg)": descartado,
                "Aproveitado (kg)": aproveitado,
                "Desperdicio (%)": round(percentual, 2),
                "Motivo": motivo,
                "Observacoes": observacoes
            }

            novos_dados = pd.concat(
                [
                    st.session_state.dados,
                    pd.DataFrame([registro])
                ],
                ignore_index=True
            )

            st.session_state.dados = novos_dados
            salvar_dados(novos_dados)

            st.success(
                "Registro realizado e salvo com sucesso!"
            )

            st.subheader("Resultado da análise")

            a, b, c = st.columns(3)

            a.metric(
                "Quantidade aproveitada",
                f"{aproveitado:.2f} kg"
            )

            b.metric(
                "Quantidade descartada",
                f"{descartado:.2f} kg"
            )

            c.metric(
                "Percentual de desperdício",
                f"{percentual:.2f}%"
            )

            if percentual > limite:

                st.error(
                    "Risco elevado: o percentual "
                    "ultrapassou o limite configurado."
                )

            else:

                st.success(
                    "O registro está dentro do limite configurado."
                )

            st.info(
                gerar_recomendacao(motivo, percentual)
            )


# =====================================================
# 9. ANALISE DE DESPERDICIO
# =====================================================

elif pagina == "Análise de desperdício":

    st.header("Análise de desperdício")

    st.write(
        "Identifique os alimentos que apresentam "
        "maiores perdas e os motivos mais frequentes."
    )

    if dados.empty:

        st.info(
            "Cadastre alimentos para visualizar as análises."
        )

    else:

        st.subheader("Desperdício por alimento")

        por_alimento = (
            dados.groupby("Alimento")[
                "Descartado (kg)"
            ]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(por_alimento)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Motivos do descarte")

            motivos = dados["Motivo"].value_counts()

            st.bar_chart(motivos)

        with col2:

            st.subheader("Desperdício por categoria")

            categorias = (
                dados.groupby("Categoria")[
                    "Descartado (kg)"
                ]
                .sum()
                .sort_values(ascending=False)
            )

            st.bar_chart(categorias)

        st.divider()

        st.subheader("Alimentos que exigem atenção")

        analise = (
            dados.groupby("Alimento")
            .agg({
                "Utilizado (kg)": "sum",
                "Descartado (kg)": "sum"
            })
            .reset_index()
        )

        analise["Desperdício (%)"] = (
            analise["Descartado (kg)"] /
            analise["Utilizado (kg)"] * 100
        )

        analise = analise.sort_values(
            "Desperdício (%)",
            ascending=False
        )

        st.dataframe(
            analise.style.format({
                "Utilizado (kg)": "{:.2f}",
                "Descartado (kg)": "{:.2f}",
                "Desperdício (%)": "{:.2f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "A classificação considera a proporção entre "
            "a quantidade descartada e a utilizada. "
            "Compare também as quantidades absolutas."
        )

        st.divider()

        st.subheader("Sugestões de melhoria")

        motivos_frequentes = dados["Motivo"].value_counts()

        principal_motivo = motivos_frequentes.index[0]

        st.write(
            f"O motivo mais registrado foi: "
            f"**{principal_motivo}**."
        )

        st.info(
            gerar_recomendacao(
                principal_motivo,
                calcular_desperdicio(
                    dados["Utilizado (kg)"].sum(),
                    dados["Descartado (kg)"].sum()
                )
            )
        )


# =====================================================
# 10. HISTORICO
# =====================================================

elif pagina == "Histórico":

    st.header("Histórico de registros")

    if dados.empty:

        st.info("Nenhum registro foi realizado ainda.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            alimentos_disponiveis = [
                "Todos"
            ] + sorted(
                dados["Alimento"].dropna().unique().tolist()
            )

            filtro_alimento = st.selectbox(
                "Filtrar por alimento",
                alimentos_disponiveis
            )

        with col2:

            motivos_disponiveis = [
                "Todos"
            ] + sorted(
                dados["Motivo"].dropna().unique().tolist()
            )

            filtro_motivo = st.selectbox(
                "Filtrar por motivo",
                motivos_disponiveis
            )

        filtrados = dados.copy()

        if filtro_alimento != "Todos":

            filtrados = filtrados[
                filtrados["Alimento"] == filtro_alimento
            ]

        if filtro_motivo != "Todos":

            filtrados = filtrados[
                filtrados["Motivo"] == filtro_motivo
            ]

        st.write(
            f"**{len(filtrados)} registro(s) encontrado(s).**"
        )

        st.dataframe(
            filtrados.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Exportar relatório")

        arquivo_csv = filtrados.drop(
            columns=["ID"]
        ).to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            "Baixar registros em CSV",
            data=arquivo_csv,
            file_name="relatorio_reduzalimentos.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.divider()

        st.subheader("Excluir registro")

        opcoes = {
            (
                f"{linha['Alimento']} | "
                f"{linha['Data']} | "
                f"{linha['Descartado (kg)']} kg descartados"
            ): linha["ID"]
            for _, linha in filtrados.iterrows()
        }

        if opcoes:

            escolhido = st.selectbox(
                "Selecione o registro",
                list(opcoes.keys())
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir este registro."
            )

            if st.button("Excluir registro"):

                if confirmar:

                    novo_historico = (
                        st.session_state.dados[
                            st.session_state.dados["ID"]
                            != opcoes[escolhido]
                        ]
                    )

                    st.session_state.dados = novo_historico

                    salvar_dados(novo_historico)

                    st.success("Registro excluído.")

                    st.rerun()

                else:

                    st.warning(
                        "Marque a confirmação antes de excluir."
                    )


# =====================================================
# 11. CONFIGURACOES
# =====================================================

elif pagina == "Configurações":

    st.header("Configurações do sistema")

    st.subheader("Limite de desperdício")

    st.write(
        "O percentual definido funciona como um parâmetro "
        "de acompanhamento. Ele não representa um limite "
        "universal para todos os estabelecimentos."
    )

    novo_limite = st.number_input(
        "Definir limite (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.limite),
        step=1.0
    )

    if st.button("Salvar configuração"):

        st.session_state.limite = novo_limite

        st.success(
            "Limite atualizado com sucesso!"
        )

    st.divider()

    st.subheader("Informações sobre os dados")

    st.write(
        f"Quantidade de registros armazenados: "
        f"**{len(st.session_state.dados)}**."
    )

    st.write(
        "Os registros são armazenados no arquivo "
        "`dados_reduzalimentos.csv`, na mesma pasta "
        "do aplicativo."
    )

    st.warning(
        "Faça cópias de segurança desse arquivo. "
        "A exclusão ou perda dele remove o histórico "
        "armazenado localmente."
    )


# =====================================================
# 12. RODAPE
# =====================================================

st.divider()

st.markdown(
    """
    <div class="rodape">
        ReduzAlimentos | Sistema de gestão de desperdício alimentar
        <br>
        Monitorar, analisar e reduzir perdas.
    </div>
    """,
    unsafe_allow_html=True
)
