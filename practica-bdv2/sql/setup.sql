-- Ejecutar en Supabase: SQL Editor -> New query -> Run

create extension if not exists vector;

-- Una fila por fragmento (chunk) del documento
create table if not exists politicas_chunks (
    id bigserial primary key,
    archivo text not null,          -- nombre del archivo de origen
    capitulo text,                  -- ej. "CAPÍTULO 3. VACACIONES"
    articulo text,                  -- ej. "Artículo 7. Días de vacaciones por antigüedad."
    content text not null,          -- texto del fragmento
    embedding vector(384)           -- all-MiniLM-L6-v2 genera 384 dimensiones
);

-- Búsqueda por similitud coseno
create or replace function match_politicas (
    query_embedding vector(384),
    match_count int default 3
)
returns table (
    id bigint,
    capitulo text,
    articulo text,
    content text,
    similarity float
)
language sql stable
as $$
    select
        p.id,
        p.capitulo,
        p.articulo,
        p.content,
        1 - (p.embedding <=> query_embedding) as similarity
    from politicas_chunks p
    order by p.embedding <=> query_embedding
    limit match_count;
$$;
