#!/usr/bin/env node
/**
 * 테스트 DB 데이터만 삭제 (스키마 유지)
 * - TRUNCATE TABLE ... RESTART IDENTITY CASCADE (public 스키마 전체)
 * - postgres-test / ddangha_test (통합 + E2E 공용)
 */
import { spawnSync } from 'child_process';

const TRUNCATE_SQL = `
DO $$
DECLARE
  r RECORD;
  lst text := '';
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
    IF lst <> '' THEN lst := lst || ', '; END IF;
    lst := lst || quote_ident(r.tablename);
  END LOOP;
  IF lst <> '' THEN
    EXECUTE 'TRUNCATE TABLE ' || lst || ' RESTART IDENTITY CASCADE';
  END IF;
END $$;
`;

const r = spawnSync(
  'docker',
  ['exec', '-i', 'ddangha-postgres-test', 'psql', '-U', 'ddangha_user', '-d', 'ddangha_test', '-v', 'ON_ERROR_STOP=1', '-f', '-'],
  { input: TRUNCATE_SQL, encoding: 'utf-8', stdio: ['pipe', 'inherit', 'inherit'] }
);
process.exit(r.status !== 0 ? (r.status ?? 1) : 0);
