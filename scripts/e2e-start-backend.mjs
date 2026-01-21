#!/usr/bin/env node
/**
 * E2E용 백엔드 기동: alembic upgrade head 후 uvicorn 실행
 * - DB: postgres-test(ddangha_test, 5434) — 통합 테스트와 동일
 * - Playwright webServer에서 사용. 선행: yarn test:infra:up
 */
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const backendDir = path.join(root, 'apps', 'backend');

const DATABASE_URL =
  process.env.E2E_DATABASE_URL ||
  'postgresql://ddangha_user:ddangha_password@localhost:5434/ddangha_test';

const env = { ...process.env, DATABASE_URL };
const py = process.env.PYTHON || 'python';

function run(args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(py, args, {
      cwd: backendDir,
      env,
      stdio: 'inherit',
      ...opts,
    });
    p.on('close', (c) => (c === 0 ? resolve() : reject(new Error(`exit ${c}`))));
    p.on('error', reject);
  });
}

async function main() {
  // 1. 스키마 적용 (postgres-test가 떠 있어야 함)
  await run(['-m', 'alembic', 'upgrade', 'head']);

  // 2. uvicorn 기동 (프로세스 유지 until Playwright가 종료)
  const uvicorn = spawn(
    py,
    ['-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
    { cwd: backendDir, env, stdio: 'inherit' }
  );

  await new Promise((resolve) => {
    uvicorn.on('close', (code) => {
      process.exit(code != null ? code : 0);
      resolve();
    });
    uvicorn.on('error', (e) => {
      console.error('uvicorn error:', e);
      process.exit(1);
      resolve();
    });
  });
}

main().catch((e) => {
  console.error('e2e-start-backend:', e.message);
  process.exit(1);
});
