import altair as alt


def bar_chart(df):
    return  alt.Chart(df).mark_bar().encode(
    y=alt.Y('name:N', sort='-x'),
    x=alt.X('qtd_mensagens:Q')
)


