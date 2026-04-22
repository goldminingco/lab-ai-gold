-- LAB AI GOLD - Inicialização do banco
-- Executado automaticamente pelo Docker na primeira vez

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Confirma extensões instaladas
DO $$
BEGIN
  RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
  RAISE NOTICE 'Banco inicializado com sucesso!';
END;
$$;
