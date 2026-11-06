-- Banco de pruebas de chunking y embeddings
-- Ejecutar en Supabase: SQL Editor -> New query -> Run
-- (No toca la tabla politicas_chunks de la línea base.)

create extension if not exists vector;

-- Una fila por chunk. La columna "estrategia" distingue el chunking
-- (articulo | fijo | fijo_traslape). Cada modelo tiene su propia columna
-- vector(n): la dimensión va atada al modelo.
drop table if exists chunks_bench cascade;
create table chunks_bench (
    id          bigserial primary key,
    estrategia  text not null,
    articulo    text,
    content     text not null,
    emb_minilm  vector(384),    -- all-MiniLM-L6-v2
    emb_multi   vector(384),    -- paraphrase-multilingual-MiniLM-L12-v2
    emb_bge     vector(1024),   -- BAAI/bge-m3
    tsv         tsvector generated always as (to_tsvector('spanish', content)) stored
);

create index chunks_bench_estrategia_idx on chunks_bench (estrategia);
create index chunks_bench_tsv_idx on chunks_bench using gin (tsv);

-- ---------------------------------------------------------------
-- Búsqueda vectorial (similitud coseno), una función por modelo
-- ---------------------------------------------------------------
create or replace function match_bench_minilm (
    query_embedding vector(384), p_estrategia text, match_count int default 3
)
returns table (id bigint, articulo text, content text, similarity float)
language sql stable as $$
    select c.id, c.articulo, c.content, 1 - (c.emb_minilm <=> query_embedding) as similarity
    from chunks_bench c
    where c.estrategia = p_estrategia and c.emb_minilm is not null
    order by c.emb_minilm <=> query_embedding
    limit match_count;
$$;

create or replace function match_bench_multi (
    query_embedding vector(384), p_estrategia text, match_count int default 3
)
returns table (id bigint, articulo text, content text, similarity float)
language sql stable as $$
    select c.id, c.articulo, c.content, 1 - (c.emb_multi <=> query_embedding) as similarity
    from chunks_bench c
    where c.estrategia = p_estrategia and c.emb_multi is not null
    order by c.emb_multi <=> query_embedding
    limit match_count;
$$;

create or replace function match_bench_bge (
    query_embedding vector(1024), p_estrategia text, match_count int default 3
)
returns table (id bigint, articulo text, content text, similarity float)
language sql stable as $$
    select c.id, c.articulo, c.content, 1 - (c.emb_bge <=> query_embedding) as similarity
    from chunks_bench c
    where c.estrategia = p_estrategia and c.emb_bge is not null
    order by c.emb_bge <=> query_embedding
    limit match_count;
$$;

-- ---------------------------------------------------------------
-- Búsqueda híbrida: vectorial + texto completo, fusionadas con
-- Reciprocal Rank Fusion (score = sum 1/(60 + rank)).
-- query_text es una tsquery ya armada, p. ej. 'vacaciones | años'.
-- ---------------------------------------------------------------
create or replace function match_bench_hibrido_minilm (
    query_embedding vector(384), query_text text, p_estrategia text, match_count int default 3
)
returns table (id bigint, articulo text, content text, similarity float)
language sql stable as $$
    with vec as (
        select c.id, row_number() over (order by c.emb_minilm <=> query_embedding) as rk
        from chunks_bench c
        where c.estrategia = p_estrategia and c.emb_minilm is not null
        order by c.emb_minilm <=> query_embedding
        limit 20
    ), fts as (
        select c.id, row_number() over (order by ts_rank(c.tsv, q) desc) as rk
        from chunks_bench c, to_tsquery('spanish', query_text) q
        where c.estrategia = p_estrategia and c.tsv @@ q
        order by ts_rank(c.tsv, q) desc
        limit 20
    )
    select c.id, c.articulo, c.content,
           (coalesce(1.0 / (60 + vec.rk), 0) + coalesce(1.0 / (60 + fts.rk), 0))::float as similarity
    from chunks_bench c
    left join vec on vec.id = c.id
    left join fts on fts.id = c.id
    where vec.id is not null or fts.id is not null
    order by similarity desc
    limit match_count;
$$;

create or replace function match_bench_hibrido_multi (
    query_embedding vector(384), query_text text, p_estrategia text, match_count int default 3
)
returns table (id bigint, articulo text, content text, similarity float)
language sql stable as $$
    with vec as (
        select c.id, row_number() over (order by c.emb_multi <=> query_embedding) as rk
        from chunks_bench c
        where c.estrategia = p_estrategia and c.emb_multi is not null
        order by c.emb_multi <=> query_embedding
        limit 20
    ), fts as (
        select c.id, row_number() over (order by ts_rank(c.tsv, q) desc) as rk
        from chunks_bench c, to_tsquery('spanish', query_text) q
        where c.estrategia = p_estrategia and c.tsv @@ q
        order by ts_rank(c.tsv, q) desc
        limit 20
    )
    select c.id, c.articulo, c.content,
           (coalesce(1.0 / (60 + vec.rk), 0) + coalesce(1.0 / (60 + fts.rk), 0))::float as similarity
    from chunks_bench c
    left join vec on vec.id = c.id
    left join fts on fts.id = c.id
    where vec.id is not null or fts.id is not null
    order by similarity desc
    limit match_count;
$$;

create or replace function match_bench_hibrido_bge (
    query_embedding vector(1024), query_text text, p_estrategia text, match_count int default 3
)
returns table (id bigint, articulo text, content text, similarity float)
language sql stable as $$
    with vec as (
        select c.id, row_number() over (order by c.emb_bge <=> query_embedding) as rk
        from chunks_bench c
        where c.estrategia = p_estrategia and c.emb_bge is not null
        order by c.emb_bge <=> query_embedding
        limit 20
    ), fts as (
        select c.id, row_number() over (order by ts_rank(c.tsv, q) desc) as rk
        from chunks_bench c, to_tsquery('spanish', query_text) q
        where c.estrategia = p_estrategia and c.tsv @@ q
        order by ts_rank(c.tsv, q) desc
        limit 20
    )
    select c.id, c.articulo, c.content,
           (coalesce(1.0 / (60 + vec.rk), 0) + coalesce(1.0 / (60 + fts.rk), 0))::float as similarity
    from chunks_bench c
    left join vec on vec.id = c.id
    left join fts on fts.id = c.id
    where vec.id is not null or fts.id is not null
    order by similarity desc
    limit match_count;
$$;
